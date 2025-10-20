#!/usr/bin/env python3
"""
iNaturalist Time Processor for Palantir Foundry

This transform processes iNaturalist data and updates the time_observed_at column
based on whether the timestamp is older than 24 hours.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, when, current_timestamp, lit
from pyspark.sql.types import TimestampType, BooleanType


class iNaturalistTimeProcessor:
    """Process iNaturalist data to update time_observed_at based on 24-hour threshold."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def process_inaturalist_data(self, input_df: DataFrame) -> DataFrame:
        """
        Process iNaturalist data and update time_observed_at column.
        
        Args:
            input_df: DataFrame containing iNaturalist data with time_observed_at column
            
        Returns:
            DataFrame with updated time_observed_at values
        """
        # Get current timestamp for comparison
        current_time = datetime.now(timezone.utc)
        
        # Calculate 24 hours ago
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        
        # Convert to Spark timestamp
        threshold_timestamp = lit(twenty_four_hours_ago)
        
        # Update time_observed_at based on whether timestamp is older than 24 hours
        processed_df = input_df.withColumn(
            "time_observed_at",
            when(
                col("time_observed_at") < threshold_timestamp,
                lit(False)  # Set to False if older than 24 hours
            ).otherwise(
                col("time_observed_at")  # Keep original value if within 24 hours
            )
        )
        
        return processed_df
    
    def process_with_boolean_logic(self, input_df: DataFrame) -> DataFrame:
        """
        Alternative approach: If time_observed_at is a boolean column,
        this method checks the timestamp and sets the boolean accordingly.
        
        Args:
            input_df: DataFrame containing iNaturalist data
            
        Returns:
            DataFrame with updated time_observed_at boolean values
        """
        # Get current timestamp
        current_time = datetime.now(timezone.utc)
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        threshold_timestamp = lit(twenty_four_hours_ago)
        
        # If time_observed_at is a boolean column, update it based on timestamp age
        processed_df = input_df.withColumn(
            "time_observed_at",
            when(
                col("timestamp") < threshold_timestamp,  # Assuming there's a 'timestamp' column
                lit(False)  # Set to False if timestamp is older than 24 hours
            ).otherwise(
                lit(True)  # Set to True if timestamp is within 24 hours
            )
        )
        
        return processed_df
    
    def process_with_timestamp_conversion(self, input_df: DataFrame) -> DataFrame:
        """
        Process data where time_observed_at needs to be converted from timestamp to boolean.
        
        Args:
            input_df: DataFrame with time_observed_at as timestamp
            
        Returns:
            DataFrame with time_observed_at as boolean
        """
        current_time = datetime.now(timezone.utc)
        twenty_four_hours_ago = current_time - timedelta(hours=24)
        threshold_timestamp = lit(twenty_four_hours_ago)
        
        # Convert timestamp to boolean based on 24-hour threshold
        processed_df = input_df.withColumn(
            "time_observed_at",
            when(
                col("time_observed_at") < threshold_timestamp,
                lit(False)
            ).otherwise(
                lit(True)
            ).cast(BooleanType())
        )
        
        return processed_df


def main():
    """Main function for Foundry transform."""
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("iNaturalistTimeProcessor") \
        .getOrCreate()
    
    # Create processor instance
    processor = iNaturalistTimeProcessor(spark)
    
    # Read input data (replace with your actual input dataset)
    # input_df = spark.read.table("your_dataset.inaturalist_data")
    # Or read from a specific path:
    # input_df = spark.read.parquet("path/to/your/inaturalist/data")
    
    # For demonstration, create sample data
    sample_data = [
        ("obs_1", datetime.now(timezone.utc) - timedelta(hours=12)),  # Within 24 hours
        ("obs_2", datetime.now(timezone.utc) - timedelta(hours=30)),  # Older than 24 hours
        ("obs_3", datetime.now(timezone.utc) - timedelta(hours=2)),  # Within 24 hours
        ("obs_4", datetime.now(timezone.utc) - timedelta(hours=48)),  # Older than 24 hours
    ]
    
    # Create sample DataFrame
    columns = ["observation_id", "time_observed_at"]
    input_df = spark.createDataFrame(sample_data, columns)
    
    print("Original data:")
    input_df.show(truncate=False)
    
    # Process the data
    processed_df = processor.process_inaturalist_data(input_df)
    
    print("Processed data:")
    processed_df.show(truncate=False)
    
    # Write output (replace with your actual output dataset)
    # processed_df.write.mode("overwrite").saveAsTable("your_dataset.processed_inaturalist_data")
    # Or save to a specific path:
    # processed_df.write.mode("overwrite").parquet("path/to/output")
    
    spark.stop()


if __name__ == "__main__":
    main()




