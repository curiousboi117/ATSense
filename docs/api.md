# API Documentation

The ATSense REST API endpoints are exposed on `http://localhost:8000`.

## Endpoints List

### Health check
* **GET** `/api/health`
* **Response**: Checks dependencies (spaCy, SentenceTransformers loading states).

### Resume Upload & Initial Analysis
* **POST** `/api/upload`
* **Content-Type**: `multipart/form-data`
* **Form Parameters**:
  * `file`: UploadFile (PDF/DOCX)
  * `job_description`: string (optional)
  * `job_title`: string (optional)
* **Response**: Returns JSON analysis details.

### Job Description Matching
* **POST** `/api/match-job`
* **Form Parameters**:
  * `resume_id`: integer
  * `job_description`: string
  * `job_title`: string
* **Response**: Returns recalculated analysis.

### History Lists
* **GET** `/api/history`
* **Response**: Lists past resume metadata, versions, and scores.

### Specific Analysis Detail
* **GET** `/api/analysis/{id}`
* **Response**: JSON detailing score, extracted skills, checks, and similarity metrics.

### PDF Report Download
* **GET** `/api/report/{id}/pdf`
* **Response**: Serves ReportLab compiled PDF.

### JSON Export
* **GET** `/api/report/{id}/json`
* **Response**: Downloads raw JSON analysis file.

### Resume Deletion
* **DELETE** `/api/resume/{id}`
* **Response**: Cascade deletes resume and analyses.

### Database Reset
* **POST** `/api/reset-all`
* **Response**: Wipes SQLite tables.
