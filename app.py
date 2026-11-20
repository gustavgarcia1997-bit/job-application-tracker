"""Flask web UI for the Job Application Tracker course project."""

import json
import os
import re
import secrets
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

import mysql.connector
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)

import database as db
from matching import job_match, read_json, required_skills, split_skills

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)

# All resources and fields are explicitly defined here; clients cannot choose SQL fields.
RESOURCES = {
    "companies": {
        "singular": "Company", "icon": "🏢",
        "fields": [
            {"name": "company_name", "label": "Company name", "required": True, "maxlen": 150},
            {"name": "industry", "label": "Industry", "maxlen": 100},
            {"name": "city", "label": "City", "maxlen": 100},
            {"name": "state", "label": "State", "maxlen": 100},
            {"name": "website", "label": "Website", "type": "url", "maxlen": 255},
            {"name": "notes", "label": "Notes", "type": "textarea"},
        ],
        "columns": [("company_name", "Company"), ("industry", "Industry"),
                    ("city", "City"), ("state", "State")],
    },
    "jobs": {
        "singular": "Job", "icon": "💼",
        "fields": [
            {"name": "company_id", "label": "Company", "required": True, "type": "company"},
            {"name": "job_title", "label": "Job title", "required": True, "maxlen": 150},
            {"name": "job_type", "label": "Job type", "type": "select",
             "options": ["Full-time", "Part-time", "Contract", "Internship", "Temporary", "Other"]},
            {"name": "salary_min", "label": "Salary minimum ($)", "type": "number"},
            {"name": "salary_max", "label": "Salary maximum ($)", "type": "number"},
            {"name": "location", "label": "Location / remote", "maxlen": 150},
            {"name": "source_url", "label": "Job posting URL", "type": "url", "maxlen": 255},
            {"name": "description", "label": "Job description", "type": "textarea"},
            {"name": "required_skills", "label": "Required skills (comma-separated)",
             "type": "textarea", "hint": "Example: Python, SQL, Linux, Git"},
            {"name": "experience", "label": "Experience requirement", "maxlen": 200},
        ],
        "columns": [("job_title", "Job"), ("company_name", "Company"),
                    ("job_type", "Type"), ("salary_min", "Min salary"),
                    ("salary_max", "Max salary")],
    },
    "applications": {
        "singular": "Application", "icon": "📨",
        "fields": [
            {"name": "job_id", "label": "Job", "type": "job", "required": True},
            {"name": "application_date", "label": "Application date", "type": "date", "required": True},
            {"name": "status", "label": "Status", "type": "select", "required": True,
             "options": ["Saved", "Applied", "Interview Scheduled", "Interview Completed",
                         "Offer Received", "Rejected", "Withdrawn"]},
            {"name": "resume_version", "label": "Resume version", "maxlen": 60},
            {"name": "cover_letter_sent", "label": "Cover letter sent", "type": "checkbox"},
            {"name": "follow_up_date", "label": "Follow-up date", "type": "date"},
            {"name": "notes", "label": "Application notes", "type": "textarea"},
            {"name": "interviewers", "label": "Interviewers (comma-separated)", "type": "textarea"},
            {"name": "next_steps", "label": "Interview next steps", "type": "textarea"},
            {"name": "feedback", "label": "Interview feedback", "type": "textarea"},
        ],
        "columns": [("job_title", "Job"), ("company_name", "Company"),
                    ("application_date", "Applied on"), ("status", "Status")],
    },
    "contacts": {
        "singular": "Contact", "icon": "👤",
        "fields": [
            {"name": "company_id", "label": "Company", "type": "company", "required": True},
            {"name": "first_name", "label": "First name", "required": True, "maxlen": 100},
            {"name": "last_name", "label": "Last name", "required": True, "maxlen": 100},
            {"name": "email", "label": "Email", "type": "email", "maxlen": 200},
            {"name": "phone", "label": "Phone", "type": "tel", "maxlen": 40},
            {"name": "job_title", "label": "Contact's job title", "maxlen": 150},
            {"name": "notes", "label": "Notes", "type": "textarea"},
        ],
        "columns": [("first_name", "First name"), ("last_name", "Last name"),
                    ("company_name", "Company"), ("email", "Email")],
    },
}


@app.before_request
def check_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    if request.method == "POST":
        received = request.form.get("csrf", "")
        if not secrets.compare_digest(received, session["csrf"]):
            abort(400, "Invalid form token. Refresh and try again.")


@app.context_processor
def common_template_data():
    return {"resources": RESOURCES, "csrf_token": session.get("csrf", "")}


def ensure_resource(resource):
    if resource not in RESOURCES:
        abort(404)
    return RESOURCES[resource]


def choices_for(resource):
    fields = RESOURCES[resource]["fields"]
    choices = {}
    if any(f.get("type") == "company" for f in fields):
        choices["company"] = db.selectable_companies()
    if any(f.get("type") == "job" for f in fields):
        choices["job"] = db.selectable_jobs()
    return choices


def form_from_item(resource, item):
    result = {f["name"]: item.get(f["name"]) for f in RESOURCES[resource]["fields"]}
    if resource == "jobs":
        required = read_json(item.get("requirements"))
        result["required_skills"] = ", ".join(required_skills(item.get("requirements")))
        result["experience"] = required.get("experience") or ""
    elif resource == "applications":
        interview = read_json(item.get("interview_data"))
        result["interviewers"] = ", ".join(interview.get("interviewers") or [])
        result["next_steps"] = interview.get("next_steps") or ""
        result["feedback"] = interview.get("feedback") or ""
    return result


def valid_url(value):
    if not value:
        return True
    parsed = urlsplit(value)
    return parsed.scheme in ("https", "http") and bool(parsed.netloc)


def validate_form(resource, raw):
    """Parse form values, produce DB fields, and return human-friendly errors."""
    output = {}
    errors = []
    for field in RESOURCES[resource]["fields"]:
        name = field["name"]
        kind = field.get("type", "text")
        value = str(raw.get(name, "") or "").strip()
        if kind == "checkbox":
            output[name] = 1 if raw.get(name) else 0
            continue
        if field.get("required") and not value:
            errors.append(f"{field['label']} is required.")
        if field.get("maxlen") and len(value) > field["maxlen"]:
            errors.append(f"{field['label']} must be {field['maxlen']} characters or less.")
        if kind in ("company", "job"):
            if value:
                try:
                    number = int(value)
                    if number < 1:
                        raise ValueError
                    output[name] = number
                except ValueError:
                    errors.append(f"Please select a valid {field['label'].lower()}.")
                    output[name] = None
            else:
                output[name] = None
        elif kind == "number":
            try:
                number = Decimal(value) if value else None
                if number is not None and (not number.is_finite() or number < 0 or number > 9999999999.99):
                    raise InvalidOperation
                output[name] = number
            except InvalidOperation:
                errors.append(f"{field['label']} must be a valid nonnegative amount.")
                output[name] = None
        elif kind == "date":
            if value:
                try:
                    output[name] = date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{field['label']} must be a valid date.")
                    output[name] = None
            else:
                output[name] = None
        elif kind == "select":
            if value and value not in field["options"]:
                errors.append(f"Invalid {field['label'].lower()}.")
            output[name] = value or None
        elif kind == "url":
            if not valid_url(value):
                errors.append(f"{field['label']} must start with http:// or https://.")
            output[name] = value or None
        elif kind == "email":
            if value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
                errors.append("Email address does not look valid.")
            output[name] = value or None
        else:
            output[name] = value or None
    if resource == "jobs":
        if (output["salary_min"] is not None and output["salary_max"] is not None
                and output["salary_min"] > output["salary_max"]):
            errors.append("Minimum salary cannot exceed maximum salary.")
        output["requirements"] = json.dumps({
            "skills": split_skills(raw.get("required_skills", "")),
            "experience": str(raw.get("experience", "") or "").strip(),
        })
        del output["required_skills"]
        del output["experience"]
    elif resource == "applications":
        output["interview_data"] = json.dumps({
            "interviewers": split_skills(raw.get("interviewers", "")),
            "next_steps": str(raw.get("next_steps", "") or "").strip(),
            "feedback": str(raw.get("feedback", "") or "").strip(),
        })
        del output["interviewers"]
        del output["next_steps"]
        del output["feedback"]
    return output, errors


@app.get("/")
def dashboard():
    stats, recent = db.dashboard_data()
    return render_template("dashboard.html", title="Dashboard", stats=stats, recent=recent)


@app.get("/match")
def match_page():
    skills_text = request.args.get("skills", "").strip()
    user_skills = split_skills(skills_text)
    jobs = db.list_items("jobs")
    results = []
    for job in jobs:
        match = job_match(user_skills, job.get("requirements"))
        results.append({**job, **match})
    results.sort(key=lambda x: (x["score"] is not None, x["score"] or 0), reverse=True)
    return render_template("match.html", title="Job Match", skills_text=skills_text,
                           user_skills=user_skills, results=results,
                           searched=bool(skills_text))


@app.get("/<resource>/")
def list_page(resource):
    config = ensure_resource(resource)
    return render_template("list.html", title=resource.title(), config=config,
                           resource=resource, rows=db.list_items(resource))


@app.route("/<resource>/new", methods=["GET", "POST"])
def create_page(resource):
    config = ensure_resource(resource)
    if request.method == "POST":
        form = request.form.to_dict()
        data, errors = validate_form(resource, form)
        if not errors:
            try:
                db.create_item(resource, data)
                flash(f"{config['singular']} created successfully.", "success")
                return redirect(url_for("list_page", resource=resource))
            except mysql.connector.IntegrityError:
                errors.append("The selected company or job is not valid. Please select an existing record.")
        for error in errors:
            flash(error, "error")
    else:
        form = {"application_date": date.today().isoformat(), "status": "Applied"}
        if resource == "applications" and request.args.get("job_id", "").isdigit():
            form["job_id"] = request.args["job_id"]
    return render_template("form.html", title=f"Add {config['singular']}", resource=resource,
                           config=config, form=form, action="Create", choices=choices_for(resource))


@app.route("/<resource>/<int:item_id>/edit", methods=["GET", "POST"])
def edit_page(resource, item_id):
    config = ensure_resource(resource)
    item = db.get_item(resource, item_id)
    if item is None:
        abort(404)
    if request.method == "POST":
        form = request.form.to_dict()
        data, errors = validate_form(resource, form)
        if not errors:
            try:
                db.update_item(resource, item_id, data)
                flash(f"{config['singular']} updated successfully.", "success")
                return redirect(url_for("list_page", resource=resource))
            except mysql.connector.IntegrityError:
                errors.append("The selected company or job is not valid. Please select an existing record.")
        for error in errors:
            flash(error, "error")
    else:
        form = form_from_item(resource, item)
    return render_template("form.html", title=f"Edit {config['singular']}", resource=resource,
                           config=config, form=form, action="Save changes", choices=choices_for(resource))


@app.post("/<resource>/<int:item_id>/delete")
def delete_page(resource, item_id):
    config = ensure_resource(resource)
    if db.get_item(resource, item_id) is None:
        abort(404)
    try:
        db.delete_item(resource, item_id)
        flash(f"{config['singular']} deleted.", "success")
    except mysql.connector.IntegrityError:
        flash("This record is linked to other data. Delete dependent records first.", "error")
    return redirect(url_for("list_page", resource=resource))


@app.errorhandler(mysql.connector.Error)
def database_error(error):
    app.logger.exception("Database problem: %s", error.__class__.__name__)
    return render_template("error.html", title="Database unavailable",
                           message="Cannot connect to MySQL or execute the query. Check that MySQL is running, "
                                   "you imported schema.sql, and your .env credentials are correct."), 503


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", title="Page not found",
                           message="That page or record doesn't exist."), 404


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", host="127.0.0.1", port=5000)
