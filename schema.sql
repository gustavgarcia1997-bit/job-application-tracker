-- Course Project: Job Application Tracker (MySQL 8.0+)
-- WARNING: no DROP statements; this script is safe to execute on an empty database.
CREATE DATABASE IF NOT EXISTS job_tracker
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE job_tracker;

CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    website VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_companies_name (company_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    job_type VARCHAR(40),
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    location VARCHAR(150),
    description TEXT,
    source_url VARCHAR(255),
    requirements JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_company FOREIGN KEY (company_id)
      REFERENCES companies(company_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_jobs_company (company_id),
    INDEX idx_jobs_title (job_title)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    application_date DATE NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'Applied',
    resume_version VARCHAR(60),
    cover_letter_sent BOOLEAN NOT NULL DEFAULT FALSE,
    follow_up_date DATE,
    notes TEXT,
    interview_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_job FOREIGN KEY (job_id)
      REFERENCES jobs(job_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_applications_job (job_id),
    INDEX idx_applications_status (status),
    INDEX idx_applications_date (application_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(200),
    phone VARCHAR(40),
    job_title VARCHAR(150),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contacts_company FOREIGN KEY (company_id)
      REFERENCES companies(company_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_contacts_company (company_id)
) ENGINE=InnoDB;
