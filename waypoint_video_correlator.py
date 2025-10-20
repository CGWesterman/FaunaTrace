#!/usr/bin/env python3
"""
Waypoint-Video Correlator

This program correlates GPX waypoints with video files through naming keys
and outputs a CSV mapping waypoints to video timestamps.
"""

import os
import sys
import csv
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import xml.etree.ElementTree as ET
import subprocess
import json


class GPXParser:
    """Parse GPX files to extract waypoints with timestamps."""
    
    def __init__(self, gpx_file: str):
        self.gpx_file = gpx_file
        self.waypoints = []
    
    def parse(self) -> List[Dict]:
        """Parse GPX file and return list of waypoints with metadata."""
        try:
            tree = ET.parse(self.gpx_file)
            root = tree.getroot()
            
            waypoints = []
            
            # Try different namespace approaches
            # First, try to find namespace from root element
            namespace = None
            if root.tag.startswith('{'):
                namespace = root.tag.split('}')[0] + '}'
            
            # Try with detected namespace
            if namespace:
                for wpt in root.findall(f'.//{{{namespace.split("}")[1]}}}wpt'):
                    waypoint = self._extract_waypoint(wpt, namespace)
                    if waypoint:
                        waypoints.append(waypoint)
            
            # Try common GPX namespaces
            if not waypoints:
                namespaces = {
                    'gpx': 'http://www.topografix.com/GPX/1/1',
                    'gpx10': 'http://www.topografix.com/GPX/1/0'
                }
                
                for ns_prefix, ns_uri in namespaces.items():
                    for wpt in root.findall(f'.//{{{ns_uri}}}wpt'):
                        waypoint = self._extract_waypoint(wpt, ns_uri)
                        if waypoint:
                            waypoints.append(waypoint)
                    if waypoints:  # Stop if we found waypoints
                        break
            
            # If still no waypoints, try without namespace
            if not waypoints:
                for wpt in root.findall('.//wpt'):
                    waypoint = self._extract_waypoint(wpt, '')
                    if waypoint:
                        waypoints.append(waypoint)
            
            self.waypoints = waypoints
            return waypoints
            
        except ET.ParseError as e:
            print(f"Error parsing GPX file: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error reading GPX file: {e}")
            return []
    
    def _extract_waypoint(self, wpt_element, namespace: str) -> Optional[Dict]:
        """Extract waypoint data from XML element."""
        try:
            lat = float(wpt_element.get('lat', 0))
            lon = float(wpt_element.get('lon', 0))
            
            # Extract name
            name_elem = None
            if namespace:
                # Try with namespace
                name_elem = wpt_element.find(f'.//{{{namespace}}}name')
            if name_elem is None:
                # Try without namespace
                name_elem = wpt_element.find('.//name')
            
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
            
            # Extract timestamp
            time_elem = None
            if namespace:
                # Try with namespace
                time_elem = wpt_element.find(f'.//{{{namespace}}}time')
            if time_elem is None:
                # Try without namespace
                time_elem = wpt_element.find('.//time')
            
            timestamp = None
            if time_elem is not None and time_elem.text:
                try:
                    # Parse ISO 8601 timestamp
                    timestamp = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            # Extract description if available
            desc_elem = None
            if namespace:
                # Try with namespace
                desc_elem = wpt_element.find(f'.//{{{namespace}}}desc')
            if desc_elem is None:
                # Try without namespace
                desc_elem = wpt_element.find('.//desc')
            
            description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
            
            return {
                'name': name,
                'lat': lat,
                'lon': lon,
                'timestamp': timestamp,
                'description': description
            }
            
        except (ValueError, AttributeError) as e:
            print(f"Error extracting waypoint data: {e}")
            return None


class VideoMetadataExtractor:
    """Extract metadata from video files using ffprobe."""
    
    def __init__(self):
        self.ffprobe_available = self._check_ffprobe()
    
    def _check_ffprobe(self) -> bool:
        """Check if ffprobe is available."""
        try:
            subprocess.run(['ffprobe', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def extract_metadata(self, video_file: str) -> Dict:
        """Extract metadata from video file."""
        if not self.ffprobe_available:
            return self._extract_fallback_metadata(video_file)
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            # Extract creation time
            creation_time = None
            if 'format' in metadata and 'tags' in metadata['format']:
                tags = metadata['format']['tags']
                for time_key in ['creation_time', 'date', 'com.apple.quicktime.creationdate']:
                    if time_key in tags:
                        try:
                            creation_time = datetime.fromisoformat(tags[time_key].replace('Z', '+00:00'))
                            break
                        except ValueError:
                            continue
            
            # Extract duration
            duration = None
            if 'format' in metadata and 'duration' in metadata['format']:
                duration = float(metadata['format']['duration'])
            
            return {
                'creation_time': creation_time,
                'duration': duration,
                'file_size': os.path.getsize(video_file),
                'filename': os.path.basename(video_file)
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error extracting video metadata: {e}")
            return self._extract_fallback_metadata(video_file)
    
    def _extract_fallback_metadata(self, video_file: str) -> Dict:
        """Fallback metadata extraction using file system."""
        try:
            stat = os.stat(video_file)
            creation_time = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            return {
                'creation_time': creation_time,
                'duration': None,
                'file_size': stat.st_size,
                'filename': os.path.basename(video_file)
            }
        except OSError as e:
            print(f"Error getting file metadata: {e}")
            return {
                'creation_time': None,
                'duration': None,
                'file_size': 0,
                'filename': os.path.basename(video_file)
            }


class WaypointVideoCorrelator:
    """Main class for correlating waypoints with video files."""
    
    def __init__(self, gpx_file: str, video_directory: str):
        self.gpx_file = gpx_file
        self.video_directory = video_directory
        self.gpx_parser = GPXParser(gpx_file)
        self.video_extractor = VideoMetadataExtractor()
    
    def correlate(self, output_file: str = "waypoint_video_correlation.csv") -> bool:
        """Main correlation logic."""
        print(f"Parsing GPX file: {self.gpx_file}")
        waypoints = self.gpx_parser.parse()
        
        if not waypoints:
            print("No waypoints found in GPX file.")
            return False
        
        print(f"Found {len(waypoints)} waypoints")
        
        print(f"Scanning video directory: {self.video_directory}")
        video_files = self._find_video_files()
        
        if not video_files:
            print("No video files found in directory.")
            return False
        
        print(f"Found {len(video_files)} video files")
        
        # Extract metadata from all videos
        video_metadata = {}
        for video_file in video_files:
            print(f"Processing video: {os.path.basename(video_file)}")
            metadata = self.video_extractor.extract_metadata(video_file)
            video_metadata[video_file] = metadata
        
        # Correlate waypoints with videos
        correlations = self._correlate_waypoints_videos(waypoints, video_metadata)
        
        # Write CSV output
        self._write_csv(correlations, output_file)
        
        print(f"Correlation complete. Results saved to: {output_file}")
        return True
    
    def _find_video_files(self) -> List[str]:
        """Find all video files in the directory."""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        video_files = []
        
        for root, dirs, files in os.walk(self.video_directory):
            for file in files:
                if Path(file).suffix.lower() in video_extensions:
                    video_files.append(os.path.join(root, file))
        
        return sorted(video_files)
    
    def _correlate_waypoints_videos(self, waypoints: List[Dict], video_metadata: Dict) -> List[Dict]:
        """Correlate waypoints with video files based on naming keys."""
        correlations = []
        
        for waypoint in waypoints:
            waypoint_name = waypoint['name'].lower()
            
            # Find matching video based on naming key
            matching_video = self._find_matching_video(waypoint_name, video_metadata)
            
            if matching_video:
                video_file, metadata = matching_video
                
                # Calculate time offset within video
                time_offset = None
                if waypoint['timestamp'] and metadata['creation_time']:
                    time_diff = waypoint['timestamp'] - metadata['creation_time']
                    time_offset = time_diff.total_seconds()
                
                correlation = {
                    'waypoint_name': waypoint['name'],
                    'waypoint_lat': waypoint['lat'],
                    'waypoint_lon': waypoint['lon'],
                    'waypoint_timestamp': waypoint['timestamp'].isoformat() if waypoint['timestamp'] else '',
                    'video_file': os.path.basename(video_file),
                    'video_full_path': video_file,
                    'video_creation_time': metadata['creation_time'].isoformat() if metadata['creation_time'] else '',
                    'video_duration': metadata['duration'],
                    'time_offset_seconds': time_offset,
                    'time_offset_formatted': self._format_time_offset(time_offset) if time_offset is not None else '',
                    'waypoint_description': waypoint['description']
                }
            else:
                # No matching video found
                correlation = {
                    'waypoint_name': waypoint['name'],
                    'waypoint_lat': waypoint['lat'],
                    'waypoint_lon': waypoint['lon'],
                    'waypoint_timestamp': waypoint['timestamp'].isoformat() if waypoint['timestamp'] else '',
                    'video_file': 'NO_MATCH',
                    'video_full_path': '',
                    'video_creation_time': '',
                    'video_duration': '',
                    'time_offset_seconds': '',
                    'time_offset_formatted': '',
                    'waypoint_description': waypoint['description']
                }
            
            correlations.append(correlation)
        
        return correlations
    
    def _find_matching_video(self, waypoint_name: str, video_metadata: Dict) -> Optional[Tuple[str, Dict]]:
        """Find video file that matches waypoint name."""
        # Try different matching strategies
        for video_file, metadata in video_metadata.items():
            video_filename = os.path.basename(video_file).lower()
            video_name_without_ext = os.path.splitext(video_filename)[0]
            
            # Strategy 1: Exact match
            if waypoint_name == video_name_without_ext:
                return video_file, metadata
            
            # Strategy 2: Waypoint name contains video name
            if waypoint_name in video_name_without_ext:
                return video_file, metadata
            
            # Strategy 3: Video name contains waypoint name
            if video_name_without_ext in waypoint_name:
                return video_file, metadata
            
            # Strategy 4: Partial match (common words)
            waypoint_words = set(waypoint_name.split('_'))
            video_words = set(video_name_without_ext.split('_'))
            if waypoint_words.intersection(video_words):
                return video_file, metadata
        
        return None
    
    def _format_time_offset(self, seconds: float) -> str:
        """Format time offset as HH:MM:SS."""
        if seconds is None:
            return ""
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _write_csv(self, correlations: List[Dict], output_file: str):
        """Write correlations to CSV file."""
        if not correlations:
            return
        
        fieldnames = [
            'waypoint_name', 'waypoint_lat', 'waypoint_lon', 'waypoint_timestamp',
            'video_file', 'video_full_path', 'video_creation_time', 'video_duration',
            'time_offset_seconds', 'time_offset_formatted', 'waypoint_description'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(correlations)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Correlate GPX waypoints with video files through naming keys"
    )
    parser.add_argument("gpx_file", help="Path to GPX file containing waypoints")
    parser.add_argument("video_directory", help="Directory containing video files")
    parser.add_argument("-o", "--output", default="waypoint_video_correlation.csv",
                       help="Output CSV file (default: waypoint_video_correlation.csv)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.gpx_file):
        print(f"Error: GPX file not found: {args.gpx_file}")
        sys.exit(1)
    
    if not os.path.exists(args.video_directory):
        print(f"Error: Video directory not found: {args.video_directory}")
        sys.exit(1)
    
    # Run correlation
    correlator = WaypointVideoCorrelator(args.gpx_file, args.video_directory)
    success = correlator.correlate(args.output)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()