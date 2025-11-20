---
title: Data Synthesis with Default Parameters
type: docs
weight: 110
prev: docs/getting-started
next: docs/getting-started/default-synthesis-default-evaluation
---

The simplest way to generate privacy-enhanced synthetic data.
Current default synthesis uses Gaussian Copula from SDV.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/getting-started/default-synthesis.ipynb)

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
Preprocessor:
  default:
    method: 'default'
Synthesizer:
  default:
    method: 'default'
Postprocessor:
  default:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
```

## YAML Parameters Detailed Explanation

### Loader (Data Loading Module)

- **`load_csv`**: Experiment name, can be freely named, recommended to use descriptive names
- **`filepath`**: Data file path
  - Value: `benchmark/adult-income.csv`
  - Description: Specifies the location of the data file to load. This example uses `adult-income.csv`, which you can replace with your own CSV file path
  - Supported formats: CSV, TSV, Excel (requires openpyxl), OpenDocument
  - Supports relative or absolute paths
  - Also supports `benchmark://` protocol for automatic standard dataset downloads

**Recommended: Use Schema:**
To ensure data loading accuracy and consistency, it is highly recommended to use the `schema` parameter to pre-define the data structure. Schema allows you to explicitly specify the data type of each column (numeric, categorical, datetime, etc.), constraints, and relationships between columns.

Example with schema:
```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml
```

For detailed information about Schema, please refer to the [Schema YAML Documentation](../../schema-yaml/).

### Preprocessor (Data Preprocessing Module)

- **`default`**: Experiment name, can be freely named
- **`method`**: Preprocessing method
  - Value: `default`
  - Description: Uses the default processing sequence, including the following steps:
    1. **missing** (missing value handling): Numeric columns use mean imputation, categorical columns are dropped
    2. **outlier** (outlier handling): Numeric columns use IQR method
    3. **encoder** (encoding): Categorical columns use uniform encoding (`encoder_uniform`)
    4. **scaler** (scaling): Numeric columns use standardization (`scaler_standard`)

### Synthesizer (Synthetic Data Generation Module)

- **`default`**: Experiment name, can be freely named
- **`method`**: Synthesis method
  - Value: `default`
  - Description: Uses the default synthesis method, which is **SDV Gaussian Copula**
  - Gaussian Copula is a statistical-based synthesis method that captures correlations between variables

### Postprocessor (Data Postprocessing Module)

- **`default`**: Experiment name, can be freely named
- **`method`**: Postprocessing method
  - Value: `default`
  - Description: Automatically performs reverse operations of Preprocessor to restore synthetic data to original format
  - Restoration sequence (reverse of preprocessing):
    1. **inverse scaler**: Reverse scaling, restoring standardized values
    2. **inverse encoder**: Reverse encoding, restoring encoded categorical variables
    3. **restore missing**: Reinsert missing values according to original proportion
  - Note: Outlier handling cannot be reversed

### Reporter (Output Module)

- **`output`**: Experiment name, can be freely named
- **`method`**: Report method
  - Value: `save_data`
  - Description: Saves the output data from the specified module as a CSV file
- **`source`**: Data source module
  - Value: `Synthesizer`
  - Description: Saves synthetic data generated from the Synthesizer module
  - Can also choose other modules, such as `Preprocessor`, `Postprocessor`, etc.
  - Default output file naming format: `petsard_Synthesizer[output].csv`

## Execution Flow

1. **Loader** loads the [`adult-income.csv`](benchmark/adult-income.csv) data
2. **Preprocessor** performs preprocessing (impute missing values, handle outliers, encode, scale)
3. **Synthesizer** generates synthetic data using the Gaussian Copula method
4. **Postprocessor** restores synthetic data to original format (reverse scaling, reverse encoding, insert missing values)
5. **Reporter** saves the final synthetic data as a CSV file

## Advanced Usage

For custom parameters, please refer to the following documentation:

- [Loader YAML Parameter Guide](../../petsard-yaml/loader-yaml/)
- [Preprocessor YAML Parameter Guide](../../petsard-yaml/preprocessor-yaml/)
- [Synthesizer YAML Parameter Guide](../../petsard-yaml/synthesizer-yaml/)
- [Postprocessor YAML Parameter Guide](../../petsard-yaml/postprocessor-yaml/)
- [Reporter YAML Parameter Guide](../../petsard-yaml/reporter-yaml/)