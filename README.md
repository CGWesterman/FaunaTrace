# Waypoint-Video Correlator

A Python program that correlates GPX waypoints with video files through naming keys and outputs a CSV mapping waypoints to video timestamps.

## Features

- Parses GPX files with waypoint timestamps
- Extracts video metadata (creation time, duration) using ffprobe or file system fallback
- Correlates waypoints with videos using flexible naming key matching
- Outputs detailed CSV with time offsets and metadata
- Handles multiple video formats (MP4, AVI, MOV, MKV, etc.)

## Installation

1. Ensure Python 3.6+ is installed
2. For enhanced video metadata extraction, install ffmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

### Basic Usage

```bash
python waypoint_video_correlator.py path/to/waypoints.gpx path/to/video/directory
```

### With Custom Output File

```bash
python waypoint_video_correlator.py waypoints.gpx ./videos -o my_correlation.csv
```

### Command Line Options

- `gpx_file`: Path to GPX file containing waypoints with timestamps
- `video_directory`: Directory containing video files
- `-o, --output`: Output CSV file (default: waypoint_video_correlation.csv)

## Input Requirements

### GPX File
- Must contain waypoints (`<wpt>`) with timestamps (`<time>`)
- Supports GPX 1.0 and 1.1 formats
- Waypoint names should match video file naming patterns

### Video Files
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V
- Should have meaningful filenames that correlate with waypoint names
- Timestamps extracted from file metadata or creation time

## Output CSV Format

The program generates a CSV with the following columns:

| Column | Description |
|--------|-------------|
| `waypoint_name` | Name from GPX waypoint |
| `waypoint_lat` | Latitude coordinate |
| `waypoint_lon` | Longitude coordinate |
| `waypoint_timestamp` | ISO timestamp from GPX |
| `video_file` | Matched video filename |
| `video_full_path` | Full path to video file |
| `video_creation_time` | Video creation timestamp |
| `video_duration` | Video duration in seconds |
| `time_offset_seconds` | Time difference (waypoint - video start) |
| `time_offset_formatted` | Time offset as HH:MM:SS |
| `waypoint_description` | Description from GPX (if available) |

## Naming Key Correlation

The program uses multiple strategies to match waypoints with videos:

1. **Exact match**: Waypoint name exactly matches video filename (without extension)
2. **Contains match**: Waypoint name is contained in video filename
3. **Reverse contains**: Video filename is contained in waypoint name
4. **Word intersection**: Common words between waypoint and video names

## Example

### Input Structure
```
waypoints/
  └── survey_track.gpx

videos/
  ├── site_001_recording.mp4
  ├── site_002_recording.mp4
  └── site_003_recording.mp4
```

### GPX Waypoint Example
```xml
<wpt lat="40.7128" lon="-74.0060">
  <name>site_001</name>
  <time>2024-01-15T10:30:00Z</time>
  <desc>Survey point 1</desc>
</wpt>
```

### Command
```bash
python waypoint_video_correlator.py waypoints/survey_track.gpx videos/
```

### Output CSV Sample
```csv
waypoint_name,waypoint_lat,waypoint_lon,waypoint_timestamp,video_file,video_full_path,video_creation_time,video_duration,time_offset_seconds,time_offset_formatted,waypoint_description
site_001,40.7128,-74.0060,2024-01-15T10:30:00+00:00,site_001_recording.mp4,/path/to/videos/site_001_recording.mp4,2024-01-15T10:25:00+00:00,300.0,300.0,00:05:00,Survey point 1
```

## Troubleshooting

### No waypoints found
- Verify GPX file format and namespace
- Check that waypoints have `<name>` and `<time>` elements

### No video matches
- Ensure video filenames contain recognizable patterns from waypoint names
- Check that video files are in supported formats

### Missing video metadata
- Install ffmpeg for enhanced metadata extraction
- Program will fall back to file system timestamps if ffprobe unavailable

## License

This project is open source and available under the MIT License.