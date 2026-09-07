# Scoring Methodology

ATSense computes an explainable ATS score from 0 to 100 based on a deterministic, configurable weighted formula.

## Score Component Weights

When a target job description is provided, the composite score utilizes the following configuration:

| Component | Weight | Calculation Basis |
|---|---|---|
| **Job Match** | 30% | Composite similarity metric (Semantic, TF-IDF, Keywords) |
| **Skills** | 20% | Number of programming/web/data/cloud skills extracted |
| **Experience** | 15% | Timeline formatting, dates, metrics, and action verbs |
| **Resume Structure** | 10% | Detection of core structural headers (Education, Skills, etc.) |
| **Education** | 10% | Presence of degree listings and graduation dates |
| **Projects** | 10% | Detail density and context descriptions |
| **Formatting** | 5% | Deductions for special characters, key stuffing, or length |

If no job description is provided, the 30% **Job Match** weight is re-allocated proportionally across the other components.

## Explainability

Every score is accompanied by an automated explanation summarizing positive attributes (e.g. "+ Strong skills coverage") and negative compliance failures (e.g. "- Missing quantifiable metrics").
