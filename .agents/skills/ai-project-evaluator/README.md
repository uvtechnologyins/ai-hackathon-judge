# AI Powered Project Evaluator Skill

This skill allows you to automatically evaluate software project repositories. It can monitor an email inbox for submissions or be run manually against specific repository URLs.

## 🚀 Overview

The evaluator analyzes projects for:
- **Readme Quality**: Checks for depth and clarity.
- **Architecture**: Identifies languages and structure.
- **AI Integration**: Detects libraries like OpenAI, LangChain, PyTorch.
- **Prompt Engineering**: Rates prompt files if present.

## 🛠️ Setup

Before using, you must configure the following environment variables. You can add these to your `.env` file or export them in your terminal.

```bash
# Email Settings (for monitoring inbox)
export EVAL_EMAIL_HOST="imap.gmail.com"
export EVAL_EMAIL_USER="your-email@example.com"
export EVAL_EMAIL_PASS="your-app-password"

# SMTP Settings (for sending replies)
export EVAL_SMTP_HOST="smtp.gmail.com"
```

## 📖 How to Use

### 1. Automatic: Email Monitoring
Use this mode to let the agent actively check for new submissions.

**When to start**: Run this periodically (e.g., via cron) or trigger it when you expect submissions.
**How to start**:
```bash
python3 scripts/process_submissions.py
```
*The script will connect to your inbox, look for unread emails with "Project Submission" in the subject, process them, and send a reply.*

### 2. Manual: Single Repo Evaluation
Use this mode to test the evaluation logic on a specific public repository without sending emails.

**When to start**: When you want to check a specific repo URL quickly.
**How to start**:
```bash
python3 scripts/evaluate_repo.py <repo_url> <output_file>
```
**Example**:
```bash
python3 scripts/evaluate_repo.py https://github.com/langchain-ai/langchain report.md
```

## 💡 Example Usage

**Input (Email)**:
> **Subject**: Project Submission
> **Body**: Hi, here is my AI agent project: https://github.com/user/my-agent-repo

**Process**:
1. Agent detects email.
2. Extracts URL.
3. Clones and analyzes repo.
4. Generates report.

**Output (Email Reply)**:
```markdown
# Project Evaluation Report
**Score**: 8/10

## Analysis
- [x] Python project detected
- [x] Uses OpenAI, LangChain
- [x] Good README detected

## Recommendation
**APPROVED**. Solid AI integration found.
```
