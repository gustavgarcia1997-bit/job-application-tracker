# JobTrack — Job Application Tracker

**COP4751 Advanced Database Management course project**  
Python · Flask · MySQL · HTML/CSS · JSON

A web app for storing companies, job openings, job applications, and recruiting contacts. Users can create, view, update, and delete records, plus calculate skill-match percentages for saved jobs.

## Features

- **4 related MySQL tables:** `companies`, `jobs`, `applications`, `contacts`
- **CRUD:** create, list, edit, and delete records in each table
- **Foreign keys:** jobs → companies; applications → jobs; contacts → companies
- **JSON:** job requirements (`skills` and `experience`) and application interview data (`interviewers`, `next_steps`, `feedback`)
- **Job Match:** compares entered skills to a job's requirements, displays matching/missing skills and a rounded match percentage
- **User experience:** dashboard counts, recent applications, responsive interface, inline success/error messages
- **Validation and safe queries:** required fields, email/URL/salary validation, parameterized SQL, CSRF form tokens

## Project structure

```text
job-application-tracker/
├── app.py                 # Flask routes + form validation
├── database.py            # MySQL connection + CRUD functions
├── matching.py            # Skill matching logic
├── schema.sql             # All four MySQL tables with FKs + JSON
├── sample_data.sql        # Optional fictional demo records
├── templates/             # HTML / Jinja pages
│   ├── base.html
│   ├── dashboard.html
│   ├── list.html
│   ├── form.html
│   ├── match.html
│   └── error.html
├── static/style.css       # Responsive styling
├── tests/test_matching.py # Skill matching tests
├── AI_USAGE.md            # AI development documentation
├── VIDEO_CHECKLIST.md     # Required video guide
├── video/README.md        # Replace with a real 3–7 minute MP4!
├── requirements.txt
└── .env.example
```

## Requirements

- **Python 3.10+** (recommended Python 3.11 or later)
- **MySQL 8.0+** with MySQL Server running and MySQL Workbench (optional GUI)
- Git and a GitHub account for the final submission

## Setup — fresh clone (Windows PowerShell)

1. Clone your repository and enter the folder:

   ```powershell
   git clone https://github.com/YOUR_USERNAME/job-application-tracker.git
   cd job-application-tracker
   ```

2. Create and activate a Python virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   If PowerShell blocks virtual environment activation, use Command Prompt instead:

   ```cmd
   .venv\Scripts\activate.bat
   ```

3. Create your database in **MySQL Workbench**:

   - Open MySQL Workbench and connect to your local MySQL server.
   - Open `schema.sql` from this project (`File → Open SQL Script`).
   - Execute the whole script using the lightning-bolt button.
   - The script creates database `job_tracker` and four related tables.
   - **Optional:** open and run `sample_data.sql` once, preferably in a fresh database, to insert fictional demonstration records.

   Alternatively, from a terminal with `mysql` on PATH:

   ```bash
   mysql -u root -p < schema.sql
   mysql -u root -p < sample_data.sql
   ```

4. Configure your database credentials:

   ```powershell
   Copy-Item .env.example .env
   ```

   Open `.env` in a text editor and set `DB_USER`, `DB_PASSWORD`, and if necessary `DB_HOST` and `DB_PORT`. Set `FLASK_SECRET_KEY` to a long random value. **Do not upload `.env` to GitHub.**

5. Run the application:

   ```powershell
   python app.py
   ```

   Visit **http://127.0.0.1:5000/** in your browser.

6. Verify it works:

   - Dashboard loads and shows counts for all four tables.
   - Create a company, then a job belonging to it.
   - Add the job's skills (e.g., `Python, SQL, Linux`).
   - Create and update an application; add interviewers and next steps.
   - Add a contact and edit it.
   - Open **Job Match**, enter `Python, SQL`, and verify the matching percentage.
   - Test deleting a record. If a company has linked jobs/contacts, you must remove those dependent records first.

### If your assignments already created `job_tracker`

The `CREATE TABLE IF NOT EXISTS` statements in `schema.sql` do **not** add columns to an existing table. Compare the existing database structure to `schema.sql`; you may need `ALTER TABLE` statements (or, **only if you do not need the old data**, create a separate fresh database for this project). The configuration defaults to `job_tracker`.

### macOS / Linux

Replace virtual environment commands with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Copy the environment file with `cp .env.example .env`.

## Job match calculation

The app extracts the `skills` array from a job's JSON `requirements` column, then compares it with the comma-separated user skills.

```text
match percentage = (number of required skills the user has / total required skills) × 100
```

Example: job requires `Python`, `SQL`, `Flask`, `Linux`; user enters `Python`, `SQL`, `Linux`. Result: **75% match** (3/4). Comparison is case-insensitive, ignores surrounding and repeated spaces, and removes duplicate skill entries. Jobs with no required skills are shown as `N/A` instead of a misleading `0%` or `100%`. This is a basic exact-skill matcher, **not** an AI semantic ranking system.

## Tests

Run the pure skill-matching tests without a live MySQL connection:

```powershell
python -m unittest discover -s tests -v
```

For full end-to-end tests, ensure MySQL is running, then manually test all four CRUD flows and Job Match using the checks above. The automated tests do not substitute for manual database/browser tests.

## Deploying / running securely

This project is designed for **local classroom demonstration**, not production deployment. Development debug mode must not be enabled on public servers. It has no user accounts, access control, or production-grade session persistence. Keep it accessible only to your local machine.

## GitHub submission

If starting from these files in a new folder:

```powershell
git init
git add .
git commit -m "Build Flask Job Application Tracker with MySQL and Job Match"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-application-tracker.git
git push -u origin main
```

Create the empty repository on GitHub before running the `remote add` and `push` commands. You can also make smaller, incremental commits as you develop/test instead of one big commit.

**Mandatory video:** record the app in action for **3–7 minutes**, including browser, Flask server, and MySQL database; add the actual MP4 file under `video/demo.mp4` (or at the repository root), commit it, and push it to GitHub. A README mentioning the video does not count. GitHub blocks normal git files over 100 MB; compress the MP4 below that limit. See [VIDEO_CHECKLIST.md](VIDEO_CHECKLIST.md) for a suggested recording flow.

**Submission:** submit the full GitHub repository URL to Canvas. Your instructor must be able to clone the repo, import `schema.sql`, configure `.env`, install dependencies, run `python app.py`, and view the demonstration video.

## Notes for instructor

- Uses normal MySQL 8 JSON columns and InnoDB foreign keys.
- CRUD SQL uses `%s` parameter placeholders, not concatenated user input.
- All app files except local credentials and the required self-recorded video are included.
- Dependencies are declared in `requirements.txt`.
