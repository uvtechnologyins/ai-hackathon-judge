import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import os
import re
import sys
import subprocess
import time

# Configuration
IMAP_SERVER = os.getenv('EVAL_EMAIL_HOST')
SMTP_SERVER = os.getenv('EVAL_SMTP_HOST')
EMAIL_USER = os.getenv('EVAL_EMAIL_USER')
EMAIL_PASS = os.getenv('EVAL_EMAIL_PASS')
CHECK_INTERVAL = 60 # Check every minute if running in loop

def connect_imap():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        return mail
    except Exception as e:
        print(f"IMAP Connection Error: {e}")
        return None

def send_email(to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = f"Re: {subject}"
    msg['From'] = EMAIL_USER
    msg['To'] = to_addr

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_addr, msg.as_string())
        print(f"Replied to {to_addr}")
    except Exception as e:
        print(f"SMTP Error: {e}")

def extract_repo_url(text):
    # Regex for finding github urls
    url_pattern = r'(https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)'
    match = re.search(url_pattern, text)
    return match.group(1) if match else None

def process_email(mail, email_id):
    _, data = mail.fetch(email_id, '(RFC822)')
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    sender = msg['From']
    subject = msg['Subject']
    print(f"Processing email from {sender}: {subject}")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    repo_url = extract_repo_url(body)
    
    if repo_url:
        print(f"Found repo: {repo_url}")
        
        # Run evaluation
        report_file = "eval_report.txt"
        eval_script = os.path.join(os.path.dirname(__file__), "evaluate_repo.py")
        
        try:
            subprocess.run([sys.executable, eval_script, repo_url, report_file], check=True)
            with open(report_file, 'r') as f:
                report_content = f.read()
            
            # Send Reply
            send_email(sender, subject, report_content)
            
            # Cleanup
            if os.path.exists(report_file):
                os.remove(report_file)
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to evaluate repository {repo_url}. Error: {e}"
            send_email(sender, subject, error_msg)
    else:
        print("No repository URL found in email.")
        # Optional: Send "No url found" reply

def main():
    if not all([IMAP_SERVER, SMTP_SERVER, EMAIL_USER, EMAIL_PASS]):
        print("Error: Missing environment variables (EVAL_EMAIL_HOST, EVAL_EMAIL_USER, etc.)")
        return

    mail = connect_imap()
    if not mail:
        return

    mail.select('inbox')
    # Search for unread emails with "Project Submission" in subject
    _, messages = mail.search(None, '(UNSEEN SUBJECT "Project Submission")')
    
    email_ids = messages[0].split()
    print(f"Found {len(email_ids)} new submissions.")
    
    for i, email_id in enumerate(email_ids, 1):
        print(f"\n--- Processing Submission {i}/{len(email_ids)} (ID: {email_id.decode()}) ---")
        try:
            process_email(mail, email_id)
        except Exception as e:
            print(f"CRITICAL ERROR processing email ID {email_id}: {e}")
            print("Skipping to next submission...")
            continue
        print("--- Submission processed ---\n")
        
    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
