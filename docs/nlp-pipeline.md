# NLP Processing Pipeline

ATSense implements a robust NLP processing pipeline to extract, structure, and analyze resume data.

```
[Raw Document (PDF/DOCX)]
          ↓ (PyMuPDF / docx)
[Raw Text Extraction]
          ↓ (Normalizers)
[Normalized Text]
          ↓ (spaCy en_core_web_sm)
[Tokenization, Sentence Segmentation, NER]
          ↓ (Regular Expressions & Rules)
[Section Detection & Contact Info Extraction]
          ↓ (Taxonomy Phrase Matching)
[Structured Skills & Metrics]
```

## Parsing
* **PDF Parser**: Uses `PyMuPDF` (`fitz`) to extract page-by-page text blocks.
* **DOCX Parser**: Uses `python-docx` to extract text from paragraphs and tables.

## Preprocessing
* Whitespace normalization.
* Casing standardizations for vocabulary checks.
* Stop-words filtering.

## Named Entity Recognition & Patterns
* **Contact Details**: Regex patterns identify emails, phone numbers, and professional URLs. SpaCy's `PERSON` and `GPE` entity tags locate name and location candidates in header zones.
* **Section Splitting**: Identifies header structures using custom short line regex matching for standard terms (e.g. `Education`, `Work Experience`). Text between matches is grouped as section blocks.
* **Skill Extraction**: Matches terms against an extensible dictionary taxonomy grouped by programming, web, data, AI/ML, DevOps, and soft skill categories.
