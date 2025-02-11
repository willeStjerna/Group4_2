# Email notifications

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import server

smtp_server = "smtp.mailersend.net"
port = 587
sender = "MS_EbrG0O@trial-pr9084zq8rj4w63d.mlsender.net"
pwd = "mssp.vezuVRd.0p7kx4xqk27g9yjr.m46V6sL"

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