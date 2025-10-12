---
title: Use Cases
type: docs
weight: 15
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial
sidebar:
  open: true
---


When developing privacy-preserving data synthesis workflows, you may encounter special requirements. The following scenarios will help you handle these situations. Each topics provides complete examples that you can execute and test directly through Colab links.

## **Data Understanding**:

### **Data Loading: [Specify Data Schema]({{< ref "specify-schema" >}})**

  - Precisely control field processing during data loading
  - Support custom missing value markers, data type conversion, and numeric precision settings
  - Ensure data quality is guaranteed from the source

### **Data Insights: [Data Description]({{< ref "data-description" >}})**

  - Understand your data before synthesis
  - Analyze data characteristics at different granularities
  - Includes global, column-wise, and pairwise statistics

## **Data Generating**:

- If the synthesis results are not satisfactory, you can:
  - Try different synthesis algorithms
  - Adjust model parameters (if any)
  - Perform more detailed data preprocessing

### **Data Quality Enhancement: [Data Preprocessing]({{< ref "data-preprocessing" >}})**

  - Systematically address various data quality issues
  - Provide multiple methods for handling missing values, encoding, and outliers
  - Include uniform encoding, standardization, and discretization techniques

### **Data Plausibility: [Data Constraining]({{< ref "data-constraining" >}})**

  - Ensure synthetic data complies with real business rules
  - Provide constraints for field values, field combinations, and null values
  - Include numeric range limits, category relationships, and null handling strategies

## **Workflow improvement**

### **Performance Analysis: [Timing]({{< ref "timing" >}})**

  - Monitor execution time for each module in your pipeline
  - Identify performance bottlenecks in your workflow
  - Compare execution times across different configurations
  - Generate timing reports for performance analysis