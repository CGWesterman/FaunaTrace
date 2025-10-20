#!/usr/bin/env python3
"""
Test script for iNaturalist time processing logic.

This script allows you to test the time processing logic locally
before deploying to Foundry.
"""

from datetime import datetime, timezone, timedelta
import pandas as pd


def process_inaturalist_time_data(df, threshold_hours=24):
    """
    Process iNaturalist data and update time_observed_at based on threshold.
    
    Args:
        df: pandas DataFrame containing iNaturalist data
        threshold_hours: Number of hours to use as threshold (default: 24)
        
    Returns:
        pandas DataFrame with processed data
    """
    # Calculate threshold time
    current_time = datetime.now(timezone.utc)
    threshold_time = current_time - timedelta(hours=threshold_hours)
    
    # Create a copy of the dataframe
    processed_df = df.copy()
    
    # Process time_observed_at column
    if 'time_observed_at' in processed_df.columns:
        # Convert to datetime if it's not already
        processed_df['time_observed_at'] = pd.to_datetime(processed_df['time_observed_at'])
        
        # Create a boolean mask for timestamps older than threshold
        is_older_than_threshold = processed_df['time_observed_at'] < threshold_time
        
        # Update the column based on the threshold
        processed_df['time_observed_at'] = ~is_older_than_threshold
        
        # Add metadata columns
        processed_df['processing_timestamp'] = current_time
        processed_df['threshold_time'] = threshold_time
        processed_df['is_older_than_threshold'] = is_older_than_threshold
        
    return processed_df


def create_sample_data():
    """Create sample iNaturalist data for testing."""
    sample_data = {
        'observation_id': [
            'obs_001', 'obs_002', 'obs_003', 'obs_004', 'obs_005',
            'obs_006', 'obs_007', 'obs_008', 'obs_009', 'obs_010'
        ],
        'time_observed_at': [
            datetime.now(timezone.utc) - timedelta(hours=2),   # Recent (should be True)
            datetime.now(timezone.utc) - timedelta(hours=12),  # Recent (should be True)
            datetime.now(timezone.utc) - timedelta(hours=25),  # Old (should be False)
            datetime.now(timezone.utc) - timedelta(hours=48),  # Old (should be False)
            datetime.now(timezone.utc) - timedelta(hours=6),   # Recent (should be True)
            datetime.now(timezone.utc) - timedelta(hours=30),  # Old (should be False)
            datetime.now(timezone.utc) - timedelta(hours=1),    # Recent (should be True)
            datetime.now(timezone.utc) - timedelta(hours=72),   # Old (should be False)
            datetime.now(timezone.utc) - timedelta(hours=18),   # Recent (should be True)
            datetime.now(timezone.utc) - timedelta(hours=36),   # Old (should be False)
        ],
        'species': [
            'Cardinal', 'Robin', 'Sparrow', 'Blue Jay', 'Finch',
            'Wren', 'Hawk', 'Eagle', 'Owl', 'Dove'
        ],
        'location': [
            'Park A', 'Park B', 'Park C', 'Park D', 'Park E',
            'Park F', 'Park G', 'Park H', 'Park I', 'Park J'
        ]
    }
    
    return pd.DataFrame(sample_data)


def main():
    """Test the processing logic with sample data."""
    print("Creating sample iNaturalist data...")
    df = create_sample_data()
    
    print("Original data:")
    print(df[['observation_id', 'time_observed_at', 'species']].to_string(index=False))
    print()
    
    print("Processing data with 24-hour threshold...")
    processed_df = process_inaturalist_time_data(df, threshold_hours=24)
    
    print("Processed data:")
    print(processed_df[['observation_id', 'time_observed_at', 'is_older_than_threshold', 'species']].to_string(index=False))
    print()
    
    # Summary statistics
    true_count = processed_df['time_observed_at'].sum()
    false_count = len(processed_df) - true_count
    
    print(f"Summary:")
    print(f"  - Observations within 24 hours: {true_count}")
    print(f"  - Observations older than 24 hours: {false_count}")
    print(f"  - Total observations: {len(processed_df)}")
    
    # Test with different threshold
    print("\n" + "="*50)
    print("Testing with 12-hour threshold...")
    processed_df_12h = process_inaturalist_time_data(df, threshold_hours=12)
    
    true_count_12h = processed_df_12h['time_observed_at'].sum()
    false_count_12h = len(processed_df_12h) - true_count_12h
    
    print(f"Summary (12-hour threshold):")
    print(f"  - Observations within 12 hours: {true_count_12h}")
    print(f"  - Observations older than 12 hours: {false_count_12h}")


if __name__ == "__main__":
    main()
