-- Optional fictional sample data for demonstrating the project.
-- Import only once into a new, empty job_tracker database.
USE job_tracker;
INSERT INTO companies (company_name, industry, city, state, website, notes)
VALUES
('Demo Security Labs', 'Cybersecurity', 'Miami', 'FL', 'https://example.com', 'Fictional company for this class demo'),
('Example Software Group', 'Technology', 'Doral', 'FL', 'https://example.org', 'Fictional company for this class demo');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, location, description, requirements)
VALUES
((SELECT company_id FROM companies WHERE company_name='Demo Security Labs' ORDER BY company_id DESC LIMIT 1),
 'Junior Security Analyst', 'Full-time', 55000, 75000, 'Miami, FL',
 'Monitor security alerts and document incidents',
 JSON_OBJECT('skills', JSON_ARRAY('Python', 'SQL', 'Networking', 'Linux'), 'experience', 'Entry level')),
((SELECT company_id FROM companies WHERE company_name='Example Software Group' ORDER BY company_id DESC LIMIT 1),
 'Backend Developer', 'Full-time', 65000, 85000, 'Remote',
 'Build and maintain web application backends',
 JSON_OBJECT('skills', JSON_ARRAY('Python', 'Flask', 'MySQL', 'Git'), 'experience', '1-2 years'));

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
VALUES
((SELECT job_id FROM jobs WHERE job_title = 'Junior Security Analyst' ORDER BY job_id DESC LIMIT 1),
 CURDATE(), 'Applied', 'Cybersecurity v1', TRUE,
 JSON_OBJECT('interviewers', JSON_ARRAY(), 'next_steps', 'Check back next week', 'feedback', ''));

INSERT INTO contacts (company_id, first_name, last_name, email, job_title)
VALUES
((SELECT company_id FROM companies WHERE company_name='Demo Security Labs' ORDER BY company_id DESC LIMIT 1),
 'Taylor', 'Morgan', 'recruiter@example.com', 'Demo Recruiter');
