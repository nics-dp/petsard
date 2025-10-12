---
title: "Clustering Task"
weight: 3
---

Evaluate synthetic data utility for unsupervised clustering problems.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-clustering.ipynb)

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Evaluator:
  clustering_utility:
    method: mlutility
    task_type: clustering
    experiment_design: domain_transfer   # Experiment design (default: domain_transfer)
    n_clusters: 3                        # Number of clusters (default: 3)
    metrics:                             # Evaluation metrics
      - silhouette_score
    random_state: 42                     # Random seed (default: 42)
```

## Task-Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **n_clusters** | `integer` | `5` | Number of clusters for K-means |
| **metrics** | `array` | `[silhouette_score]` | Evaluation metrics (currently only silhouette_score supported) |

Note: Clustering tasks do not require a `target` parameter since they are unsupervised.

## Supported Metrics

| Metric | Description | Range | Default |
|--------|-------------|-------|---------|
| `silhouette_score` | Measure of cluster cohesion and separation | -1 to 1 | ✓ |

## Key Metrics Recommendations

| Metric | Description | Recommended Standard |
|--------|-------------|---------------------|
| **Silhouette Score** | Evaluates cluster compactness and separation<br>• 1: Perfect clustering<br>• 0: Overlapping clusters<br>• Negative: Misaligned clusters | ≥ 0.5 |

## Usage Considerations

### When to Use Clustering

- **No target variable available**: Exploratory data analysis
- **Pattern discovery needed**: Customer segmentation, anomaly detection
- **All numerical features**: Clustering works best with numerical data

### Choosing Number of Clusters

Consider these approaches:
- **Domain knowledge**: Industry standards or business requirements
- **Elbow method**: Plot inertia vs. k and find the "elbow"
- **Silhouette analysis**: Test different k values and compare scores
- **Gap statistic**: Statistical method to estimate optimal k

### Data Preprocessing

MLUtility automatically performs the following preprocessing on input data:

1. **Missing Value Handling**
   - Removes samples containing missing values (using `dropna()`)

2. **Column Type Identification**
   - Checks all datasets (ori, syn, control)
   - If a column is categorical in any dataset, treats it as categorical
   - Conservative approach ensures no categorical features are missed

3. **Categorical Feature Encoding**
   - Uses OneHotEncoder for one-hot encoding
   - Trains encoder only on ori and syn data (avoids data leakage)
   - `handle_unknown='ignore'`: Unseen categories in control encoded as all-zero vectors

4. **Feature Standardization**
   - Uses StandardScaler on all features (numerical + encoded categorical)
   - Computes mean and std only from ori and syn data (avoids data leakage)
   - Control dataset uses the same transformation parameters

5. **Data Alignment**
   - Ensures consistent feature dimensions across all datasets
   - Processed data ready for clustering analysis

{{< callout type="info" >}}
**Data Leakage Prevention**: Encoders and scalers are trained only on ori and syn data, preventing control information from leaking into the training process.
{{< /callout >}}

### Model Details

- **Algorithm**: K-means clustering
- **Distance metric**: Euclidean distance
- **Initialization**: k-means++ (default)
- **Maximum iterations**: 300

### Limitations

{{< callout type="warning" >}}
**Current Limitations:**
- Only K-means clustering is supported
- Only silhouette score metric is available
- Assumes spherical clusters (K-means assumption)
{{< /callout >}}

### Interpreting Results

**Silhouette Score Interpretation:**
- **0.71-1.00**: Strong structure found
- **0.51-0.70**: Reasonable structure found
- **0.26-0.50**: Weak structure, may be artificial
- **< 0.25**: No substantial structure found

The score measures:
- **Cohesion**: How close points are to their own cluster
- **Separation**: How far points are from other clusters

{{< callout type="info" >}}
For datasets with non-spherical clusters, consider that K-means may underperform, affecting utility evaluation accuracy.
{{< /callout >}}