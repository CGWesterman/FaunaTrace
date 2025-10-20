# iNaturalist Time Processing for Palantir Foundry

This implementation provides a solution for processing iNaturalist data in Palantir Foundry and updating the `time_observed_at` column based on a 24-hour threshold.

## Overview

The solution includes:
- **Foundry Transform**: Ready-to-deploy transform for your Foundry stack
- **Local Testing**: Script to test the logic before deployment
- **Configuration**: YAML configuration for the transform
- **Multiple Approaches**: Different ways to handle the time processing

## Files Created

### 1. `foundry_transform.py`
The main Foundry transform file with three different approaches:

- **`compute()`**: Basic transform that updates `time_observed_at` based on 24-hour threshold
- **`compute_boolean_conversion()`**: Converts timestamp to boolean based on threshold
- **`compute_with_metadata()`**: Enhanced version with processing metadata

### 2. `inaturalist_time_processor.py`
Standalone processor class that can be used in various contexts:

- **`process_inaturalist_data()`**: Main processing method
- **`process_with_boolean_logic()`**: Alternative boolean-based approach
- **`process_with_timestamp_conversion()`**: Converts timestamps to booleans

### 3. `test_inaturalist_processing.py`
Local testing script with sample data:

- Creates sample iNaturalist observations
- Tests the processing logic
- Provides summary statistics
- Allows testing with different thresholds

### 4. `transform_config.yaml`
Configuration file for the Foundry transform:

- Input/output dataset configuration
- Processing parameters
- Runtime requirements

## Usage

### 1. Deploy to Foundry

1. **Update Dataset RIDs**: Replace the placeholder RIDs in `foundry_transform.py` with your actual dataset RIDs:
   ```python
   Output("ri.foundry.main.dataset.your_output_dataset")
   Input("ri.foundry.main.dataset.your_input_dataset")
   ```

2. **Deploy the Transform**: Upload the `foundry_transform.py` file to your Foundry workspace

3. **Configure the Transform**: Use the `transform_config.yaml` as a reference for configuration

### 2. Test Locally

Run the test script to verify the logic:

```bash
python test_inaturalist_processing.py
```

This will:
- Create sample iNaturalist data with various timestamps
- Process the data with a 24-hour threshold
- Show before/after results
- Provide summary statistics

### 3. Customize the Threshold

You can easily change the threshold from 24 hours to any other value:

```python
# In the transform
twenty_four_hours_ago = current_time - timedelta(hours=48)  # 48 hours instead

# In the test script
processed_df = process_inaturalist_time_data(df, threshold_hours=12)  # 12 hours
```

## Logic Explanation

The processing logic works as follows:

1. **Get Current Time**: Uses UTC timezone for consistency
2. **Calculate Threshold**: Subtracts the specified hours (default: 24) from current time
3. **Compare Timestamps**: For each `time_observed_at` timestamp:
   - If timestamp < threshold: Set to `False`
   - If timestamp >= threshold: Keep original value or set to `True`
4. **Return Processed Data**: DataFrame with updated `time_observed_at` values

## Data Types

The solution handles different scenarios:

- **Timestamp to Boolean**: If `time_observed_at` is a timestamp, converts to boolean
- **Boolean Update**: If `time_observed_at` is already boolean, updates based on threshold
- **Metadata Addition**: Optionally adds processing metadata columns

## Example Output

```
Original Data:
observation_id  time_observed_at           species
obs_001         2024-01-15 10:30:00+00:00  Cardinal
obs_002         2024-01-14 22:30:00+00:00  Robin
obs_003         2024-01-13 10:30:00+00:00  Sparrow

Processed Data (24-hour threshold):
observation_id  time_observed_at  is_older_than_threshold  species
obs_001         True              False                    Cardinal
obs_002         True              False                    Robin
obs_003         False             True                     Sparrow
```

## Configuration Options

- **Threshold Hours**: Default 24, can be changed to any value
- **Timezone**: Default UTC, can be configured
- **Metadata**: Optional processing metadata columns
- **Output Format**: Boolean or timestamp preservation

## Next Steps

1. **Update Dataset RIDs**: Replace placeholder RIDs with your actual dataset RIDs
2. **Test Locally**: Run the test script to verify the logic
3. **Deploy to Foundry**: Upload and configure the transform
4. **Monitor Results**: Check the output dataset for processed data
5. **Schedule**: Set up scheduling if needed for regular processing

## Troubleshooting

- **RID Errors**: Make sure to use the correct dataset RIDs from your Foundry workspace
- **Timezone Issues**: Ensure all timestamps are in UTC or adjust the timezone logic
- **Data Types**: Verify that your `time_observed_at` column is a timestamp type
- **Permissions**: Ensure the transform has read/write permissions for the datasets
