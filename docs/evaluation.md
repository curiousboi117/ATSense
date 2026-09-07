# Evaluation Methodology

ATSense includes an academic evaluation module to measure the extraction accuracy of its NLP pipeline.

## Evaluation Metrics

Precision, Recall, and F1-score are calculated as follows:

$$\text{Precision} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Positives (FP)}} \times 100$$

$$\text{Recall} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Negatives (FN)}} \times 100$$

$$\text{F1-score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

## Tested Parameters

1. **Entity Accuracy**: Matches exact values of extracted Name, Email, and Phone number relative to ground truth labels.
2. **Section Detection (Macro Average)**: Evaluates structural section splits.
3. **Skill Taxonomy Matching (Macro Average)**: Measures matched skill tokens.

## Execution
Run the evaluation module directly from the terminal:
```bash
python backend/evaluation.py
```
This script computes statistics on a synthetic test dataset to display precision, recall, and F1 indicators.
