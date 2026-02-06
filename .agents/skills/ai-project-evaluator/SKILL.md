---
name: ai-project-evaluator
description: Monitors an email inbox for project submissions (repo URLs), evaluates them using AI (Readme, Architecture, AI Usage, Prompts), and automatically replies with a report.
---

# AI Powered Project Evaluator

This skill actively monitors a configured email inbox for new project submissions. When a submission is found (email containing a GitHub repo URL), it clones the repository, analyzes it based on specific AI criteria, and sends a detailed evaluation report back to the sender.

## Capabilities

1.  **Email Monitoring**: Connects to IMAP to find unread emails with "Project Submission" in the subject.
2.  **Repo Analysis**:
    *   **Readme Quality**: Checks for existence and detailed content.
    *   **Architecture**: Analyzes file structure and tech stack.
    *   **AI Integration**: Detects AI libraries (OpenAI, LangChain, etc.).
    *   **Prompt Engineering**: Rates prompts if found.
3.  **Auto-Reply**: Sends the generated report via SMTP.

## Usage

To use this skill, you must set the following environment variables:
*   `EVAL_EMAIL_USER`: Email address to login.
*   `EVAL_EMAIL_PASS`: App password for the email.
*   `EVAL_EMAIL_HOST`: IMAP host (e.g., `imap.gmail.com`).
*   `EVAL_SMTP_HOST`: SMTP host (e.g., `smtp.gmail.com`).

### Commands

*   `check submissions` / `evaluate projects`: Runs the monitoring script to check for new emails and process them.
*   `test evaluation <repo_url>`: Runs the evaluation logic on a specific repo URL manually (skips email).

## Script Locations

*   **Logic**: `scripts/evaluate_repo.py`
*   **Orchestrator**: `scripts/process_submissions.py`

## Example Output

```markdown
# Project Evaluation Report

**Repo:** https://github.com/user/my-ai-project
**Score:** 8/10

## Analysis
- [x] Readme present (Good quality)
- [x] Python project detected
- [x] Uses OpenAI API

## AI Implementation
Found logical use of LLMs in `src/agent.py`.
```
