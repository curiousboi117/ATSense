# System Architecture

ATSense is structured as a decoupled, local-first client-server application. It integrates natural language processing and lexical/semantic similarity engines to optimize resume compatibility.

## Block Diagram

```
[ User UI ] <----> [ React SPA (Vite) ]
                          |
                    (REST API / CORS)
                          |
                    [ FastAPI Backend ]
                    /        |        \
    [ Parsers (PyMuPDF) ] [ SQL DB ] [ NLP/ML Engines (spaCy & ML) ]
```

## Modular Responsibilities

1. **Frontend**: React-based UI implementing Glassmorphic theme styles, animated score meters, custom SVGs for trends, and dynamic history loaders.
2. **REST API**: Built with FastAPI. It handles routing and validation schemas via Pydantic.
3. **Database Layer**: SQLite stores resumes, analyses, and job matching history via SQLAlchemy ORM.
4. **NLP Pipeline**: Extracts entities, sections, and structural patterns.
5. **Similarity Engine**: Combines keyword density, TF-IDF cosine matching, and SentenceTransformer semantic embeddings.
6. **ATS Compliance Engine**: Audits formatting, lengths, verb patterns, dates, and metrics.
7. **Report Generator**: Generates print-ready PDF summaries via ReportLab.
