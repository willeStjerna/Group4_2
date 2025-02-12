# Email notifications

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more verbosity
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


load_dotenv() # loading env variables

smtp_server = os.getenv("smtp_server")
port = 587
sender = os.getenv("smtp_sender")
pwd = os.getenv("smtp_pwd")

def send_email_notification(commit_id, receiver, build_status, log_output):
    """
    Sends an email notification about the CI build result.

    param commit_id (str): The Git commit hash being tested
    param build_status (str): "Success" or "Failure"
    param log_output (str): Log output from the build/test process
    """
    subject = f"CI Build: {build_status}, Commit: {commit_id[:7]}"
    message = f"""
    The CI build status for commit {commit_id} has {build_status}.

    Build logs:
    {log_output}
    """

    try:

        logging.info(f"Preparing email notification for commit {commit_id[:7]} ({build_status}) to {receiver}...")

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        logging.info("Connecting to SMTP server...")

        mail_server = smtplib.SMTP(smtp_server, port)
        mail_server.starttls()
        mail_server.login(sender, pwd)

        mail_server.sendmail(sender, receiver, msg.as_string())
        mail_server.quit()
        logging.info(f"Email successfully sent to {receiver} for commit {commit_id[:7]} ({build_status}).")

        

    except Exception as e:
        logging.error(f"Failed to send email for commit {commit_id[:7]}: {e}")