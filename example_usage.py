#!/usr/bin/env python3
"""
Example usage of the Waypoint-Video Correlator

This script demonstrates how to use the correlator programmatically
and provides sample data for testing.
"""

import os
import tempfile
from datetime import datetime, timezone
from waypoint_video_correlator import WaypointVideoCorrelator


def create_sample_gpx():
    """Create a sample GPX file for testing."""
    from datetime import datetime, timezone, timedelta
    
    # Use current time as base for realistic timestamps
    now = datetime.now(timezone.utc)
    base_time = now - timedelta(hours=2)  # 2 hours ago
    
    gpx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Example" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="40.7128" lon="-74.0060">
    <name>site_001</name>
    <time>{(base_time).isoformat()}</time>
    <desc>Survey point 1 - Central Park</desc>
  </wpt>
  <wpt lat="40.7589" lon="-73.9851">
    <name>site_002</name>
    <time>{(base_time + timedelta(minutes=15)).isoformat()}</time>
    <desc>Survey point 2 - Times Square</desc>
  </wpt>
  <wpt lat="40.6892" lon="-74.0445">
    <name>site_003</name>
    <time>{(base_time + timedelta(minutes=30)).isoformat()}</time>
    <desc>Survey point 3 - Statue of Liberty</desc>
  </wpt>
  <wpt lat="40.7505" lon="-73.9934">
    <name>site_004</name>
    <time>{(base_time + timedelta(minutes=45)).isoformat()}</time>
    <desc>Survey point 4 - Empire State Building</desc>
  </wpt>
</gpx>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
        f.write(gpx_content)
        return f.name


def create_sample_video_files():
    """Create sample video files (empty files for demonstration)."""
    video_dir = tempfile.mkdtemp()
    
    # Create sample video files with matching names
    video_files = [
        'site_001_recording.mp4',
        'site_002_recording.mp4', 
        'site_003_recording.mp4',
        'unrelated_video.mp4'  # This won't match any waypoint
    ]
    
    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        with open(video_path, 'w') as f:
            f.write('')  # Empty file for demonstration
    
    return video_dir


def run_example():
    """Run the example correlation."""
    print("Creating sample data...")
    
    # Create sample GPX file
    gpx_file = create_sample_gpx()
    print(f"Created sample GPX: {gpx_file}")
    
    # Create sample video directory
    video_dir = create_sample_video_files()
    print(f"Created sample video directory: {video_dir}")
    
    # Run correlation
    print("\nRunning correlation...")
    correlator = WaypointVideoCorrelator(gpx_file, video_dir)
    
    output_file = "example_correlation.csv"
    success = correlator.correlate(output_file)
    
    if success:
        print(f"\nCorrelation completed successfully!")
        print(f"Results saved to: {output_file}")
        
        # Display results
        print("\nCorrelation Results:")
        print("-" * 100)
        try:
            import csv
            with open(output_file, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    print(f"{i}. Waypoint: {row['waypoint_name']}")
                    print(f"   Video: {row['video_file']}")
                    print(f"   Coordinates: {row['waypoint_lat']}, {row['waypoint_lon']}")
                    print(f"   Waypoint Time: {row['waypoint_timestamp']}")
                    print(f"   Video Time: {row['video_creation_time']}")
                    print(f"   Time Offset: {row['time_offset_formatted']} ({row['time_offset_seconds']} seconds)")
                    print(f"   Description: {row['waypoint_description']}")
                    print()
        except Exception as e:
            print(f"Error reading results: {e}")
    else:
        print("Correlation failed!")
    
    # Cleanup
    print("\nCleaning up sample files...")
    try:
        os.unlink(gpx_file)
        import shutil
        shutil.rmtree(video_dir)
        print("Cleanup completed.")
    except Exception as e:
        print(f"Cleanup error: {e}")


if __name__ == "__main__":
    run_example()