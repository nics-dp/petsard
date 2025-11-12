---
title: Time Anchoring Scaling
weight: 4
---

Multi-timestamp data refers to recording multiple key time nodes with clear temporal relationships within the same business process or entity lifecycle. Unlike time series data, multi-timestamp data are not equally-spaced observations but represent important milestones in business processes. The core characteristics of this type of data lie in the clear business logic and dependency relationships between time points, each time point represents a key event in the business process, the existence or absence of time points itself has business implications, and the intervals between time points reflect business patterns and individual differences. Typical application scenarios include enterprise data (establishment date → first financing application → approval date → latest tracking date), customer journey (registration date → first purchase → membership upgrade → last activity date), and medical records (first visit → diagnosis confirmation → treatment start → follow-up examination).

## Challenges and Solutions for Multi-Timestamp Data

In the field of synthetic data, multi-timestamp data requires special handling for quite complex reasons. First is the problem of logical constraints—there are clear business logic constraints between different time points, such as loan application time cannot be earlier than enterprise establishment time, financial tracking time must be later than loan approval time. Second, current open-source synthesizers have obvious deficiencies in handling multiple time points, treating each time point as independent time distributions to learn, which although may capture potential relationships from data, easily produces results that violate business logic. If these relationships are not explicitly specified, absurd situations occur such as application date being earlier than establishment date. Additionally, the existence or absence of time points and their intervals all imply important business logic, time differences reflect industry characteristics and economic cycles, missing time points may represent specific business states (such as unapproved applications), and time intervals may also hint at risk levels or policy changes.

Time Anchoring is a best practice method proposed by our team based on practical experience to address these challenges. Its core concept is to select the most important time field that never has null values as the "anchor point," then transform other time points into time differences (duration) relative to the anchor point according to appropriate time precision, use these time differences as numerical fields for synthesizer learning, and restore them to absolute dates or times after synthesis is complete. This method brings multiple advantages: transforming absolute time into relative time differences can simplify the synthesizer's learning difficulty, synthesizers generally have better grasp of integer types (time differences) than date types, learning effects for simple constraints like "value must be greater than zero" are better, and it can more effectively ensure logical coherence between multiple time points.

## Determining Whether Time Anchoring Is Needed

When data contains multiple time points and exhibits the following characteristics, time anchoring should be considered. If temporal logic is clear, with definite sequential relationships between time points, this is the most important criterion. If time points are related to business processes, representing different lifecycle stages of the same entity, time anchoring can effectively capture these relationships. When time constraints exist, with certain time points having to be later than others, time anchoring can ensure synthetic data meets these constraints. If time differences are meaningful, with intervals between time points reflecting important business patterns, time anchoring can preserve these business insights.

Typical data types requiring time anchoring include enterprise financing (establishment→application→approval→tracking), customer journey (registration→first purchase→upgrade→churn), medical records (visit→diagnosis→treatment→follow-up), order data (order→payment→shipment→receipt), etc. In these scenarios, clear business logic and dependency relationships exist between time points.

Ideal anchor points should have the following characteristics: never missing, with time points existing for all records; earliest occurrence, usually the starting point of business processes; business stability, unaffected by subsequent business changes; clear semantics, with well-defined business definitions. Common anchor points include establishment date for enterprise data, registration date for customer data, project initiation date for project data, and first visit date for medical record data—these time points all represent the starting points of their respective business processes.

In some cases, time anchoring is not suitable. Single timestamps (such as transaction time in a single field) or equally-spaced time series data (such as monthly sales) do not need time anchoring. Time series data (equally-spaced continuous observations) should use time series prediction models like TimeGAN or DoppelGANger. When time points have no logical associations, each time point should be treated as an independent field. If there is no permanently existing starting time point, consider using business rules to generate virtual anchor points. When time relationships vary based on other conditions, group processing or conditional constraints are recommended.

## Practical Application Examples

The following example demonstrates how to use time anchoring in enterprise financing data from policy financial institutions:

```yaml
Preprocessor:
  time_anchoring:
    method: 'default'
    config:
      scaler:
        established_date:
          # Use company establishment date as anchor, calculate day differences with other time points
          method: 'scaler_timeanchor'
          reference:
            - 'first_apply_date'
            - 'first_approval_date'
            - 'latest_apply_date'
            - 'latest_approval_date'
            - 'last_tracking_date'
          unit: 'D'  # D represents days as unit
```

This configuration uses enterprise establishment date (established_date) as the anchor point, calculating day differences between five other time points and the anchor. In the original data, company C000001's established_date is 2019-11-03, first_apply_date is 2022-01-21, after transformation first_apply_date becomes 810 (day difference), and other time points are transformed accordingly. Missing time points (such as first approval date being null for some enterprises) are preserved as NaN, and the synthesizer learns their distribution patterns.

Different time units can be selected based on business needs. Seconds (s) are suitable for real-time systems and transaction records such as financial transaction timestamps, minutes (m) for scheduling systems and short-term processes such as customer service call records, hours (h) for same-day business and shift systems such as hospital bed usage, days (D) for cross-day/week/month processes such as enterprise financing and project management, weeks (W) for long-term tracking such as regular health checks and quarterly reports. Selection principles should be based on business characteristics and data precision, recommending selection of the largest unit that adequately reflects business precision, avoiding excessive detail (such as using seconds to record annual events) or excessive coarseness (such as using weeks to record real-time transactions).

## Notes and Common Questions

### Why Not Let Synthesizers Learn Absolute Time Directly?

Using absolute time directly (such as complete datetime timestamps) encounters multiple difficulties. Absolute time has large value ranges (such as Unix timestamps), relationships between time points are not obvious, and synthesizers have difficulty capturing time constraints. This easily produces invalid values, possibly generating future dates or violating time sequences (such as application date later than approval date), making it difficult to ensure business logic consistency.

The advantages of time anchoring lie in time differences having smaller and bounded value ranges, time relationships being clearer (such as "approval date must be later than application date" becoming "time difference must be positive"), making it easier for synthesizers to learn and maintain these constraints.

### What If Time Differences Are Negative?

Negative time differences usually indicate data problems, requiring investigation of possible causes including data entry errors, system timezone inconsistencies, business logic changes (such as retroactive historical data entry), or special business situations (such as retrospectively modified application dates).

It's recommended to prioritize solving in data preprocessing stage before inputting to PETsARD preprocessing, ensuring input data's business logic correctness. If complete avoidance is impossible, constraints can be used in the synthesizer to ensure time differences are positive, or records violating constraints can be validated and corrected after synthesis.

### What If There's No Clear Anchor Point?

When data has no permanently existing starting time point, consider creating virtual anchor points by taking the minimum value of all time fields as the anchor point in data preprocessing stage.

Another method is using the most common time point, selecting the time point with lowest missing rate as anchor, accepting that a few records cannot calculate time differences.

Alternatively, group by business type, with each group using different anchor points. If time points are highly independent, time anchoring can be avoided, directly using original time fields with constraints.

### What Impact Does Time Anchoring Have on Synthesis Quality?

According to our team's practical experience, time anchoring brings significant positive impacts. In reducing invalid samples, it greatly reduces synthetic records that violate time logic. In improving correlations, it better preserves association patterns between time points. In stability enhancement, it reduces extreme or abnormal time values.

Possible trade-offs include requiring additional preprocessing steps, anchor point selection requiring domain knowledge, and possibly needing multiple adjustments for complex time relationships. However, overall, for data containing multiple time points, using time anchoring almost always brings quality improvements and is a strongly recommended best practice.