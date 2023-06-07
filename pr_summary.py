import os
import json
import requests
import getpass
import smtplib
from email.message import EmailMessage
from tabulate import tabulate
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def get_pull_requests():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=all"

    response = requests.get(url)
    response.raise_for_status()  # Check for any API errors

    pull_requests = json.loads(response.text)
    return pull_requests

def format_datetime(datetime_str):
    dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def generate_email(pull_requests, open_count, closed_count):
    email_subject = "Pull Request Summary"
    email_body = f"Pull Request Summary\n"

    table_data = []
    for pr in pull_requests:
        pr_title = pr["title"]
        pr_status = pr["state"]
        pr_created_at = format_datetime(pr["created_at"])
        pr_user = pr["user"]["login"]
        table_data.append([pr_title, pr_status, pr_user, pr_created_at])

    email_body += tabulate(table_data, headers=["PR Title", "State", "User", "Time"], tablefmt="grid")

    email = EmailMessage()
    email["From"] = SENDER_EMAIL
    email["To"] = RECIPIENT_EMAIL
    email["Subject"] = email_subject
    email.set_content(email_body)

    return email

def send_email(email):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SENDER_EMAIL")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # Prompt for the email password
    sender_password = getpass.getpass("Enter the email password: ")

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        # Print email details to console
        print("Email details:")
        print(f"From: {email['From']}")
        print("To:", email['To'])
        print(f"Subject: {email['Subject']}")
        print(f"Body:\n{email.get_content()}")

        # Send the email
        server.send_message(email)

    print("Email sent successfully!")

def main():
    # Retrieve pull requests
    pull_requests = get_pull_requests()
    
    # Count open and closed pull requests
    open_count = 0
    closed_count = 0
    for pr in pull_requests:
        if pr["state"] == "open":
            open_count += 1
        elif pr["state"] == "closed":
            closed_count += 1
    
    # Generate email
    email = generate_email(pull_requests, open_count, closed_count)
    
    # Send email
    send_email(email)
    
    # Print counts to console
    print(f"Open Pull Requests: {open_count}")
    print(f"Closed Pull Requests: {closed_count}")

if __name__ == "__main__":
    main()
