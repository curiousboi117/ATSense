# Database Schema

ATSense utilizes a local SQLite database file (`atsense.db`) mapped via SQLAlchemy ORM.

## Entity Relationship Diagram (ERD)

```
[ User ] (id=1, default profile)
   ├── [ Resume ] (stores text, file info, versioning increments)
   │      └── [ Analysis ] (stores scores, breakdowns, JSON details)
   └── [ JobDescription ] (stores title and requirements)
```

## Tables Schema

### Users
* `id`: Integer, Primary Key
* `username`: String (default "ats_user")
* `email`: String (optional)
* `created_at`: DateTime

### Resumes
* `id`: Integer, Primary Key
* `user_id`: ForeignKey to Users
* `filename`: String
* `file_size`: Integer
* `version`: Integer (increments on every upload)
* `extracted_text`: Text
* `created_at`: DateTime

### JobDescriptions
* `id`: Integer, Primary Key
* `user_id`: ForeignKey to Users
* `title`: String
* `text`: Text
* `created_at`: DateTime

### Analyses
* `id`: Integer, Primary Key
* `resume_id`: ForeignKey to Resumes
* `job_description_id`: ForeignKey to JobDescriptions (Nullable)
* `ats_score`: Float
* `score_breakdown`: JSON (dictionary)
* `personal_info`: JSON (dictionary)
* `skills`: JSON (dictionary)
* `ats_checks`: JSON (list of compliance warnings)
* `recommendations`: JSON (list)
* `similarity_metrics`: JSON (Nullable)
* `created_at`: DateTime
