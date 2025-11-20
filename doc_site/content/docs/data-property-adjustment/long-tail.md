---
title: Logarithmic Transformation
type: docs
weight: 530
prev: docs/data-property-adjustment/uniform-encoding
next: docs/data-property-adjustment/time-anchoring
math: true
---

A long-tailed distribution (Heavy-tailed Distribution) refers to data distribution exhibiting significant skewness, where there is a substantial gap between a few extreme values and the majority of common values. This type of distribution is extremely common in real-world data, such as income distribution, transaction amounts, and website traffic. Long-tailed distributions significantly impact the quality of synthetic data because synthesizers struggle to simultaneously capture both the dense distribution of common values and the sparse characteristics of extreme values.

Logarithmic transformation is one of the most commonly used and effective methods for handling long-tailed distributions. By taking the logarithm of original values, skewed distributions can be transformed into more symmetric distributions. The core value of logarithmic transformation lies in compressing the value range, where larger values are compressed more while smaller values are compressed less, thereby reducing the dominant influence of extreme values on the overall distribution. This transformation not only improves the synthesizer's learning effectiveness but, more importantly, preserves the relative size relationships between values, ensuring that the transformed data maintains the original ordering structure.

## Types and Effects of Logarithmic Transformation

Logarithmic transformation mainly comes in two forms. The standard logarithmic transformation is defined as $y = \log(x)$, suitable for numerical variables where all values are greater than zero, converting multiplicative relationships into additive relationships, commonly used for strictly positive variables such as price or area. The other is log-plus-one transformation, defined as $y = \log(x + 1)$, suitable for numerical variables containing zero values, solving the problem of $\log(0)$ being undefined, commonly used for count data such as purchase counts or view counts.

In practical applications, the effect of logarithmic transformation is quite significant. Before transformation, long-tailed distributions typically show most values concentrated in the low-value region while a few extreme values are scattered in the high-value region, making it difficult for synthesizers to balance learning at both ends. After logarithmic transformation, the value distribution becomes more symmetric, extreme values are effectively compressed, and synthesizers can more easily learn overall patterns, thus producing higher-quality synthetic data.

## Determining Whether Logarithmic Transformation Is Needed

When data exhibits the following characteristics, logarithmic transformation should be considered. If the data shows obvious skewed distribution, such as skewness (Skewness) absolute value greater than 1 or histogram showing obvious left skew, this is a signal suitable for transformation. If extreme values exist in the data, such as maximum and minimum values differing by several orders of magnitude, or outliers far from the main distribution, logarithmic transformation can effectively compress these extreme values. From domain knowledge judgment, if variables exhibit multiplicative relationships rather than additive relationships (such as compound growth, proportional changes), logarithmic transformation is particularly effective. Additionally, if synthetic data cannot produce extreme values or excessively produces unreasonable extreme values, this also indicates that the original data may need logarithmic transformation.

Judging distribution skewness can be done through statistical indicators and visual inspection. For statistical indicators, after calculating the skewness value, if the absolute value is greater than 1, it indicates strong skewness and logarithmic transformation should be used; if between 0.5 and 1, it indicates moderate skewness and transformation may be considered; if close to 0, it indicates symmetric distribution and transformation may not be needed. Visual inspection includes plotting histograms to observe distribution shape, using Q-Q plots to check normality, and comparing median and mean differences to assess skewness degree.

Choosing between standard logarithm $\log(x)$ or log-plus-one $\log(x+1)$ depends on data characteristics. If all values are greater than 0, use standard logarithmic transformation $\log(x)$ which provides better interpretability, suitable for strictly positive variables such as price or area. If data contains 0 values, use log-plus-one transformation $\log(x+1)$ to avoid the undefined problem of $\log(0)$, particularly suitable for count data such as purchase counts or view counts. If data contains negative values, other processing is needed before applying logarithmic transformation.

In some cases, logarithmic transformation is not suitable. If the distribution is already symmetric, with skewness close to 0, applying logarithmic transformation will instead increase training data precision. If data contains negative values, logarithms cannot directly handle them, and other transformation methods should be considered. If business interpretation is important, such as when zero or negative values represent specific business states, consider treating them as categories rather than performing numerical transformation.

## Practical Application Examples

The following example demonstrates combining different transformation methods to process financial data:

```yaml
Preprocessor:
  financial_data:
    method: 'default'
    config:
      sequence:
        - 'encoder'
        - 'scaler'
      scaler:
        # Logarithmic transformation: strictly positive values
        transaction_amount: 'scaler_log'
        account_balance: 'scaler_log'

        # Log-plus-one transformation: may be zero
        transaction_count: 'scaler_log1p'
        failed_attempts: 'scaler_log1p'

        # Standardization: already symmetric variables
        credit_score: 'scaler_standard'
        interest_rate: 'scaler_standard'
```

This configuration applies appropriate transformation strategies for columns with different characteristics. Transaction amount (transaction_amount) and account balance (account_balance) are strictly positive values, using standard logarithmic transformation to effectively compress their long-tailed distribution. Transaction count (transaction_count) and failed attempts count (failed_attempts) may contain zero values, thus using log-plus-one transformation. Credit score (credit_score) and interest rate (interest_rate) already show symmetric distribution, only requiring standardization processing.

## Notes and Common Questions

### How to Handle Data Containing Negative Values?

Logarithms cannot directly handle negative values, and strategies need to be chosen based on business context. Possible approaches include adding a constant to all values to make them all positive, but this may reduce potential heterogeneous relationships and change the data's internal structure. Another approach is to separate positive and negative values, create a categorical variable to mark the sign, then apply logarithmic transformation to absolute values. If data contains both positive and negative values that cannot be separated, consider using Yeo-Johnson transformation or quantile transformation.

Most importantly, understand the business meaning of negative values. For example, if negative values represent losses or refunds and other special states, they can be considered as independent categories to be handled separately rather than simply as numerical values. These alternative methods are not currently included in PETsARD and need to be implemented in the preprocessing stage.

### What Impact Does Logarithmic Transformation Have on Synthetic Data Quality?

According to our team's practical experience, appropriate use of logarithmic transformation can significantly improve synthetic data quality. In terms of distribution similarity, column shape scores can typically improve by 10-30%, extreme value handling becomes more reasonable, reducing unrealistic extreme synthetic values. Additionally, logarithmic transformation helps better capture correlations between variables while making the synthesizer's training process more stable and faster.

However, note that excessive transformation may produce adverse effects. For example, applying logarithmic transformation to originally symmetric distributions will instead introduce skewness. Therefore, after applying transformation, it's essential to check whether the restored synthetic data conforms to business logic and statistical properties.

### Do Outliers Need to Be Handled Before or After Logarithmic Transformation?

PETsARD's default preprocessing handles outliers first before scaling (including logarithmic transformation), and the order cannot be changed. If outlier execution is not disabled using positive listing, it's easy for long-tail outliers to be removed, resulting in poor logarithmic transformation effectiveness.

The choice of processing order depends on the nature of outliers. If outliers are data errors or abnormal records, or if extreme values severely distort the overall distribution, outlier processing should be performed before logarithmic transformation. Conversely, if extreme values are real and important data points, direct logarithmic transformation is usually sufficient, as logarithmic transformation itself has the effect of compressing extreme values.

In practice, it's recommended to first visually inspect the data distribution, assess the business reasonableness of extreme values, then try different strategies and compare final synthesis quality to make decisions.

### Do Standardization Scaling Need to Be Done Before or After Logarithmic Transformation?

It's not recommended to apply logarithmic transformation to already standardized data. Standardization transforms data into a distribution with mean zero and standard deviation one, producing negative values, which logarithms cannot handle.

Based on our team's practical experience, even performing standardization after logarithmic transformation has almost no difference in effect compared to only performing logarithmic transformation. This may be because most distribution deviations have already been handled in logarithmic transformation.

Therefore, our team recommends users focus on determining whether columns need logarithmic transformation, without needing other scaling processing.