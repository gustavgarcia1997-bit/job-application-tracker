# AI Usage Documentation — Job Application Tracker

> **Important:** This file documents the AI assistance used to prepare the project scaffold. The student should review it, add their real testing/debugging experiences, and remove any statement that does not accurately describe their own work before submitting. The template below intentionally does not invent testing, personal modifications, or outcomes.

## AI tool used

**ChatGPT (OpenAI)** was used to help plan and generate a first working draft of the Job Application Tracker, including Python, Flask, MySQL SQL scripts, HTML/CSS, project structure, validation, matching logic, and the initial README.

## Key prompts / requests

1. **Project instructions shared:** "Course Project: Job Application Tracker ... Build a complete web application ... MySQL ... Python with Flask ... HTML/CSS ... CRUD on all four tables ... Job Match feature ... AI_USAGE.md ... video demo."
2. **Earlier course context reused:** four related tables named `companies`, `jobs`, `applications`, and `contacts`; MySQL database `job_tracker`; JSON for job requirements and interview data.

Add other actual prompts here if you use AI for further changes or troubleshooting:

- `[Add the exact prompt you used, or remove this placeholder.]`

## What AI helped generate

- `schema.sql`: four linked tables, primary/foreign keys, JSON columns, indexes.
- `database.py`: centralized MySQL connection and parameterized CRUD functions.
- `app.py`: Flask routes, forms, field validation, CSRF protections, dashboard, and error handling.
- `matching.py`: exact, case-insensitive skill comparisons and percent calculations.
- `templates/` and `static/style.css`: responsive user interface and reusable templates.
- `README.md` and `VIDEO_CHECKLIST.md`: installation/submission instructions.
- `tests/test_matching.py`: automated tests for matching behavior.

## Changes I personally made after receiving AI output

**Complete this section truthfully based on your actual work.** Examples of changes you *might* make include adjusting the app styling, matching your earlier SQL schema, changing sample records, rewriting a form label, or debugging a connection error. Do not claim these changes unless you really did them.

- `[Your actual change and why you made it.]`
- `[Your actual debugging fix or test outcome.]`

## How I verified the code

**Complete after running the project on your computer.** Check off only tests you really performed:

- [ ] Created/imported all four MySQL tables using `schema.sql`
- [ ] Started Flask and opened the website
- [ ] Created, listed, edited, and deleted a company
- [ ] Created, listed, edited, and deleted a job
- [ ] Created, listed, edited, and deleted an application
- [ ] Created, listed, edited, and deleted a contact
- [ ] Calculated a job-skill match percentage and checked the result manually
- [ ] Used MySQL Workbench to confirm changes reached the database
- [ ] Tested setup from a fresh clone
- [ ] Recorded and uploaded the required 3–7 minute demo video

## What I learned from using AI

Write your own reflection here. Some ideas: how Flask routes call reusable database functions, why SQL parameters are safer than concatenating strings, the benefits of a normalized relational schema, how JSON helps store flexible requirements, and why AI-generated code still requires testing against a real MySQL database.

`[Add a few sentences about what you actually understood, verified, and found helpful or unhelpful.]`

## Responsible use

AI was used as a development assistant. The final submission should reflect code the student inspected, tested, and can explain. No claim is made that the generated app was already run with the student's MySQL server.
