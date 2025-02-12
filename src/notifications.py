# Email notifications

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from dotenv import load_dotenv

load_dotenv() # loading env variables

smtp_server = os.getenv("smtp_server")
port = 587
sender = os.getenv("smtp_sender")
pwd = os.getenv("smtp_pwd")

def send_email_notification(commit_id, receiver, build_status, log_output, user, branch):
    """
    Sends an email notification about the CI build result.

    param commit_id (str): The Git commit hash being tested
    param build_status (str): "Success" or "Failure"
    param log_output (str): Log output from the build/test process
    """
    subject = f"CI Build: {build_status}, Commit: {commit_id[:7]}"
    message = f"""
    The CI build for commit {commit_id} {build_status}.

    Made by user: {user}, on branch: {branch}.

    Build logs:
    {log_output}
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        mail_server = smtplib.SMTP(smtp_server, port)
        mail_server.starttls()
        mail_server.login(sender, pwd)

        mail_server.sendmail(sender, receiver, msg.as_string())
        mail_server.quit()
        print("Email sent")
        

    except Exception as e:
        print("Error when sending email:", e)