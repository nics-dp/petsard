---
title: "update_config()"
weight: 336
---

Update the processor's configuration settings.

## Syntax

```python
def update_config(
    config: dict
) -> None
```

## Parameters

- **config** : dict, required
    - New processor configuration
    - Required parameter
    - Structure: `{processor_type: {field_name: processing_method}}`

## Returns

None (method modifies instance state)

## Description

The `update_config()` method updates the processor configuration. It can:

1. Override default processing methods
2. Set custom processors for specific columns
3. Disable processing for specific columns (set to `None` or `"none"`)

## Basic Example

```python
from petsard import Loader, Processor

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Create processor
processor = Processor(metadata=schema)

# Update configuration
new_config = {
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot',
        'education': 'encoder_label'
    }
}
processor.update_config(new_config)

# Use updated configuration
processor.fit(data)
processed_data = processor.transform(data)
```

## Configuration Formats

### 1. Using Processor Name (String)

```python
config = {
    'missing': {
        'age': 'missing_mean',
        'income': 'missing_median'
    },
    'outlier': {
        'age': 'outlier_zscore',
        'income': 'outlier_iqr'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    },
    'scaler': {
        'age': 'scaler_minmax',
        'income': 'scaler_standard'
    }
}
processor.update_config(config)
```

### 2. Using Processor with Parameters (Dictionary)

```python
config = {
    'missing': {
        'age': {
            'method': 'missing_simple',
            'value': 0.0
        }
    },
    'scaler': {
        'created_at': {
            'method': 'scaler_timeanchor',
            'reference': 'event_time',
            'unit': 'D'
        }
    },
    'encoder': {
        'doc_date': {
            'method': 'encoder_date',
            'input_format': '%MinguoY-%m-%d',
            'date_type': 'date'
        }
    }
}
processor.update_config(config)
```

### 3. Disable Specific Processing

```python
config = {
    'outlier': {
        'age': None,  # Don't process age outliers
        'income': 'outlier_iqr'
    },
    'scaler': {
        'gender': 'none'  # String "none" also disables
    }
}
processor.update_config(config)
```

## Partial Update

```python
# Update only some columns, others keep default
processor = Processor(metadata=schema)

# Update only missing value handling for age
processor.update_config({
    'missing': {
        'age': 'missing_median'
    }
})

# Other columns still use default configuration
```

## Multiple Updates

```python
processor = Processor(metadata=schema)

# First update
processor.update_config({
    'missing': {'age': 'missing_median'}
})

# Second update (will override or add)
processor.update_config({
    'missing': {'income': 'missing_mean'},
    'encoder': {'gender': 'encoder_onehot'}
})

# Final configuration includes all updates
```

## Setting Configuration at Initialization

```python
# Can also provide configuration when creating processor
custom_config = {
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    }
}

processor = Processor(metadata=schema, config=custom_config)
# No need to call update_config()
```

## Verify Configuration Update

```python
processor = Processor(metadata=schema)

# Update configuration
new_config = {
    'missing': {'age': 'missing_median'},
    'encoder': {'gender': 'encoder_onehot'}
}
processor.update_config(new_config)

# Verify update
config = processor.get_config(col=['age', 'gender'])
print("age missing:", type(config['missing']['age']).__name__)
print("gender encoder:", type(config['encoder']['gender']).__name__)
```

## Available Processor Names

### Missing Value Processors
- `missing_mean`: Fill with mean
- `missing_median`: Fill with median
- `missing_mode`: Fill with mode
- `missing_simple`: Fill with custom value (requires `value` parameter)
- `missing_drop`: Drop rows with missing values

### Outlier Processors
- `outlier_zscore`: Z-Score method
- `outlier_iqr`: Interquartile Range method
- `outlier_isolationforest`: Isolation Forest (global)
- `outlier_lof`: Local Outlier Factor (global)

### Encoders
- `encoder_uniform`: Uniform encoding
- `encoder_label`: Label encoding
- `encoder_onehot`: One-Hot encoding
- `encoder_date`: Date format conversion (requires parameters)

### Scalers
- `scaler_standard`: Standardization
- `scaler_minmax`: Min-Max scaling
- `scaler_zerocenter`: Zero centering
- `scaler_log`: Logarithmic transformation
- `scaler_log1p`: log(1+x) transformation
- `scaler_timeanchor`: Time anchor scaling (requires parameters)

### Discretization
- `discretizing_kbins`: K-bins discretization (requires parameters)

## Notes

- Updating configuration overwrites default settings for that column
- Must call this method before `fit()`
- If updating after `fit()`, need to retrain
- Invalid processor names will raise `ConfigError`
- Setting to `None` or `"none"` disables that processing
- Processors with parameters must use dictionary format
- Updates are cumulative, won't clear other columns' configuration