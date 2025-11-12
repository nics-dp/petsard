---
title: Split-Synthesize-Merge
weight: 1
---

High heterogeneity data refers to datasets containing multiple subgroups with different characteristics and significant differences within the same dataset. These subgroups exhibit obvious differences in statistical distribution, variable relationships, and data density, making it difficult for a single synthesizer to simultaneously capture the characteristics of all subgroups. Split-Synthesize-Merge is a strategy that leverages domain knowledge to pre-split heterogeneous data into more homogeneous subsets, synthesize them separately, and then integrate the results.

## Origin and Value of Split-Synthesize-Merge

The split-synthesize-merge method originated from the CAPE team's practical experience in assisting with large-scale demographic data processing in a public sector scenario. The main challenge at that time was hardware limitations: the data volume reached several GB, exceeding the capacity of existing hardware to process completely at once, with insufficient memory causing frequent interruptions during training. To solve this problem, the team adopted a "split-synthesize-merge" strategy. This splitting is performed by "row," not by column. The specific approach is to select key grouping variables based on domain knowledge (such as household type), split data rows into multiple smaller subsets based on different category values of that variable (for example, splitting population data by household type into seven subsets: single-person households, couple households, single-parent households, nuclear families, grandparent-grandchild households, three-generation households, and other households), then synthesize each subset separately, and finally integrate the synthesis results into a complete dataset.

Although split-synthesize-merge was initially created to overcome hardware limitations, the team discovered this method has unique value during practice. In handling high heterogeneity data, different subgroups may have completely different statistical characteristics, and separate processing can more precisely capture the characteristics of each subgroup. For imbalanced data, rare categories are easily overlooked in the overall data, and after splitting, synthesis strategies can be adjusted for subgroups of different proportions to ensure rare categories receive sufficient attention. Additionally, split-synthesize-merge fully utilizes domain knowledge, pre-assisting the synthesizer through data engineering means, which is more efficient and provides better control over heterogeneous data compared to purely relying on deep learning models.

The core concepts of split-synthesize-merge include three key elements. First is selecting appropriate splitting variables, where ideal splitting variables should represent the data's inherent heterogeneity, usually categorical variables with clear business meaning. Second is following appropriate grouping principles, where ideal groups should have within-group homogeneity (similar data characteristics within the same subgroup) and between-group heterogeneity (significant differences between different subgroups), while avoiding excessive disparity in subgroup sizes. Finally is designing integration strategies, where when merging synthesis results from each subgroup, the distribution characteristics of the original grouping variable need to be maintained, the number of synthetic samples for each subgroup should be allocated according to original proportions, and overall logical consistency of the integrated data should be ensured.

This method brings multiple advantages: overcoming hardware limitations by splitting large datasets into manageable units; improving synthesis quality by optimizing for homogeneous subgroup characteristics; improving rare category handling to ensure small groups receive sufficient attention; providing flexible adjustment strategy space where different subgroups can adopt different parameters or synthesizers; facilitating parallel processing implementation, significantly reducing overall processing time.

### Workflow Diagram

{{< mermaid-file file="content/docs/data-property-adjustment/split-synthesize-workflow.zh-tw.mmd" >}}

**Legend:**

- Light yellow boxes: External operations (splitting and merging using SQL/Python)
- Light blue boxes: PETsARD operations (synthesis and evaluation)
- Light green boxes: Process completion

## Determining Whether Split-Synthesize-Merge Is Needed

When data exhibits the following characteristics, split-synthesize-merge should be considered. If there is obvious inherent heterogeneity, meaning there are key variables that can distinguish data characteristics, and statistical distributions of different subgroups are significantly different, this is the most important criterion. If there is high imbalance, with extremely few samples in certain categories on key variables, rare categories easily submerged by overall distribution, split-synthesize-merge can ensure these rare categories receive sufficient attention. Additionally, when data volume is too large, cannot be loaded into memory at once, or training time is too long (exceeding several hours) with insufficient hardware resources, split-synthesize-merge is also an effective solution.

Ideal splitting variables should have clear business meaning (such as household type, transaction type, customer segmentation), and different category values of this variable should correspond to data rows with distinctly different characteristics. For example, in population data, single-person households and multi-person households show completely different patterns in family member numbers, income structure, and consumption patterns; in transaction data, normal transactions and fraud transactions have obvious distinctions in amount, time, and frequency characteristics. The key is to find that group variable that can naturally divide data into "internally similar, mutually different" groups, ensuring data rows within the same category have similar characteristics while data rows between different categories show obvious differences.

When necessary, ANOVA or chi-square tests can be performed on candidate variables to confirm statistically significant differences between different categories. It's recommended to control the number of subgroups to 3-10, with minimum subgroup sample size greater than 1000, and subgroup sizes should not be too disparate (maximum/minimum ratio should be less than 100).

In some cases, split-synthesize-merge is not suitable. If no key variable can represent heterogeneity, with no clear splitting variable available, this method should not be used. If data is highly homogeneous, with no clear internal grouping structure and all samples having similar characteristics, splitting will instead add unnecessary complexity. If subgroup sample size is too small (< 1000) after splitting, groups are too fragmented, and representation of synthesis models is insufficient, split-synthesize-merge is also not suitable.

## Practical Application Examples

PETsARD currently does not have built-in split-synthesize-merge functionality, users need to manually split data before using PETsARD, and manually merge results after synthesis is complete. The following demonstrates how to use SQL for splitting and merging using population statistical data as an example.

**Step 1: Split Data**

```sql
-- Split into four subsets by household type
SELECT * FROM population_data WHERE household_type = 'Single-person'
INTO OUTFILE '/data/split/household_1_single.csv';

SELECT * FROM population_data WHERE household_type = 'Couple'
INTO OUTFILE '/data/split/household_2_couple.csv';

SELECT * FROM population_data WHERE household_type = 'Nuclear'
INTO OUTFILE '/data/split/household_3_nuclear.csv';

SELECT * FROM population_data WHERE household_type = 'Multigenerational'
INTO OUTFILE '/data/split/household_4_multigenerational.csv';
```

**Step 2: Execute PETsARD Synthesis for Each Subset**

Create configuration files for each subset and execute synthesis:

```bash
# Execute synthesis for each subgroup
petsard run config_household_1.yaml --output synthetic_household_1.csv
petsard run config_household_2.yaml --output synthetic_household_2.csv
# ... and so on
```

**Step 3: Merge Synthesis Results**

```sql
-- Create merged table
CREATE TABLE synthetic_population_merged AS
SELECT *, 'Single-person' as household_type FROM synthetic_household_1
UNION ALL
SELECT *, 'Couple' as household_type FROM synthetic_household_2
UNION ALL
SELECT *, 'Nuclear' as household_type FROM synthetic_household_3
UNION ALL
SELECT *, 'Multigenerational' as household_type FROM synthetic_household_4;


-- Verify household type distribution of merged results
SELECT household_type, COUNT(*) as count,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM synthetic_population_merged) as percentage
FROM synthetic_population_merged
GROUP BY household_type;
```

This process demonstrates the complete split-synthesize-merge workflow. In the splitting stage, based on household type—a variable with clear business meaning—the original data is divided into four subsets. Data within each subset has similar family structure characteristics; for example, single-person households have income and consumption patterns significantly different from multi-person households. In the synthesis stage, PETsARD is executed separately for each subset, where each subset can use the same or different synthesizer parameters. Finally, in the merging stage, UNION ALL is used to integrate synthesis results from all subsets, and the household type distribution after merging is verified to ensure it meets expected proportions.

## Notes and Common Questions

### What If Subgroup Sample Size Is Too Small After Splitting?

When some subgroups have insufficient samples, consider adjusting grouping strategy to ensure each subgroup has sufficient samples. Specific approaches include merging categories with too few samples (< 1000) into an "other" category, or changing from fine classification to coarse classification, i.e., merging certain categories based on domain knowledge for generalization.

### Does Split-Synthesize-Merge Affect Privacy Protection?

Theoretically, the impact of split-synthesize-merge on privacy protection is two-sided. Potential risks include small groups being easier to identify, and the splitting variable itself may leak information (for example, if the splitting variable is a sensitive attribute like disease type, synthetic data may be highly representative and easy to infer).

For protective measures, differential privacy can be used with appropriate privacy budgets set; privacy risk assessment can be performed separately for each subgroup (such as using Anonymeter's singling-out attack tests) to ensure each subgroup's risk is below acceptable thresholds; if a group has high privacy risk and few samples, consider merging it into an "other" category.

If necessary, privacy indicators for each subgroup can be recorded and reported, paying special attention to groups with fewer than 1,000 samples.

### Can Different Synthesizers Be Used After Splitting?

Yes, and this is precisely one of the advantages of split-synthesize-merge. Different subgroups can choose the most suitable synthesizer based on their characteristics. The recommended implementation strategy is to first use the same synthesizer for all subgroups to establish a baseline, identify subgroups with poor quality, then try different synthesizers for problem subgroups, and finally compare results and select the best combination.

### Overall, What Are the Advantages and Disadvantages of Split-Synthesize-Merge Compared to Direct Synthesis?

Advantages of split-synthesize-merge: can overcome hardware limitations by splitting large datasets for processing, reducing memory requirements and enabling parallel computation acceleration; for heterogeneous data, can more precisely capture characteristics of each subgroup, ensuring rare subgroups receive sufficient attention; provides flexible parameter adjustment space where different subgroups can use different strategies and hyperparameter settings.

Disadvantages of split-synthesize-merge: increases operational complexity, requiring additional data processing steps, multiple configuration files and synthesis tasks, and careful handling in the merging stage; may lose associations between different subgroups, overall pattern capture may not be as good as direct synthesis; management costs increase, requiring tracking of multiple synthesis tasks, quality assessment becomes more complex, and debugging difficulty also increases accordingly.