# Required 3–7 Minute Project Demonstration — Recording Plan

**This video is mandatory.** The professor says the project will not be graded without it. Record your own app running; the zip package cannot include a genuine recording from your computer.

## Before pressing Record

- Import `schema.sql` into MySQL and optionally `sample_data.sql` for easy demo records.
- Open MySQL Workbench, your Flask terminal window, and your browser at http://127.0.0.1:5000/.
- Check that the pages work. Close personal notifications. Never show your `.env` password on screen.
- Use any screen recorder (Windows Snipping Tool screen recording, OBS, Xbox Game Bar, etc.). MP4 recommended; keep it under 100 MB for normal GitHub upload.

## Suggested walkthrough (~5 minutes)

| Part | Approx. duration | What to demonstrate |
|---|---:|---|
| 1. Introduction | 0:30 | Show dashboard; say it is Python Flask + MySQL |
| 2. Database | 0:40 | Show the 4 tables and relationships in MySQL Workbench; optionally view JSON |
| 3. Companies & jobs CRUD | 1:10 | Create/edit/delete a company or job; show required skills |
| 4. Applications & contacts CRUD | 1:10 | Add/edit application status and interview data; add a contact |
| 5. Job Match | 0:55 | Enter `Python, SQL`, see percent and matched/missing skills |
| 6. Server & wrap-up | 0:35 | Show Flask terminal requests and summarize features |

If a record is linked to another record, MySQL foreign keys prevent deleting its parent. For an uncomplicated delete demo, create an extra unlinked company, then delete it.

## Add your finished video to GitHub

1. Save the **actual recording** as `video/demo.mp4`.
2. From the project folder run:

   ```powershell
   git add video/demo.mp4
   git commit -m "Add required project demo video"
   git push
   ```

3. Open your GitHub repository in a browser and check that `video/demo.mp4` is present and can be opened.
4. Copy your GitHub repository URL into Canvas. **Do not submit only the video link.**
