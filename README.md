# ATSense: An Explainable NLP and Machine Learning-Based Resume Analysis and Job Matching System

ATSense is a production-quality academic project designed as an explainable, local-first system for resume analysis, applicant tracking system (ATS) scoring, and semantic job matching. 

Unlike black-box AI tools, ATSense highlights exact scoring weights, lexical frequency matches, compliance audits, and semantic gap calculations to give users transparency.

---

## 1. Problem Statement & Objectives

Modern Applicant Tracking Systems (ATS) automatically filter out over 75% of resumes before a recruiter ever reviews them. However, standard ATS algorithms can be overly punitive to formatting errors, missing section tags, or lack of quantifiable results. Candidates struggle to optimize their applications because commercial tools offer vague, non-explainable scores.

### Key Objectives:
* Build a local, modular NLP pipeline to tokenize, clean, and structure resumes.
* Map technical and soft skills to a multi-category taxonomical classifier.
* Develop an explainable compliance checker that highlights rule failures by severity.
* Integrate job compatibility scoring using TF-IDF matching and SentenceTransformer semantic embeddings.
* Facilitate an iterative improvement loop, tracking resume progression across versions (v1, v2, v3).
* Provide print-ready PDF reports and JSON exports for candidates.

---

## 2. Technology Stack

* **Frontend**: React.js, Vite, Tailwind CSS, Framer Motion, Lucide React, Axios.
* **Backend**: Python 3, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic.
* **Document Parsers**: PyMuPDF (`fitz`), `python-docx`.
* **NLP & Similarity Engine**: spaCy (`en_core_web_sm`), scikit-learn (`TfidfVectorizer`), NumPy, `sentence-transformers` (`all-MiniLM-L6-v2`).
* **Database**: SQLite (local storage, file: `atsense.db`).
* **PDF Exporter**: ReportLab layout engines.

---

## 3. Project Structure

```
ATSense/
├── backend/
│   ├── main.py                  # API endpoints entry
│   ├── database.py              # SQLite session setup
│   ├── models.py                # SQL database tables (User, Resume, JobDescription, Analysis)
│   ├── schemas.py               # Pydantic serialization models
│   ├── parser.py                # Text extraction from PDF & DOCX
│   ├── preprocessing.py         # spaCy tokenizers and cleaners
│   ├── nlp_engine.py            # Section chunkers & contact checkers
│   ├── skill_extractor.py       # Taxonomy matching rules
│   ├── ats_engine.py            # Formatting & keyword check rules
│   ├── similarity_engine.py     # TF-IDF & SentenceTransformers comparison
│   ├── scoring_engine.py        # ATS weighted scoring
│   ├── recommendation_engine.py  # Local guideline engines & optional LLMs
│   ├── report_generator.py      # ReportLab PDF report builder
│   ├── evaluation.py            # Precision, Recall & F1 metrics calculator
│   ├── utils.py                 # Logger and file config helpers
│   ├── requirements.txt         # Backend Python packages
│   └── tests/                   # Automated pytest suite
├── frontend/
│   ├── package.json
│   ├── vite.config.js           # API proxy configured
│   ├── index.html
│   ├── public/assets/           # ATSense logos
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css            # Custom glassmorphism variables
│       ├── components/          # Reusable UI widgets
│       ├── pages/               # Routing views
│       ├── context/             # React global states
│       └── services/            # Axios API wrappers
├── docs/                        # Detailed architectural writeups
└── README.md
```

---

## 4. Installation & Local Setup

### Backend Setup:
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. Run development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup:
1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run React dev server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 5. Execution of Testing & Evaluation

### Run Academic Evaluation Simulator:
The evaluation module tests the extraction accuracy of Name, Email, Phone, sections, and skills against synthetic ground truth labels, printing Precision, Recall, and F1 averages.
```bash
python backend/evaluation.py
```

### Run Unit Tests:
Ensure backend schemas, parser rules, and api routers function correctly:
```bash
pytest backend/tests/
```
