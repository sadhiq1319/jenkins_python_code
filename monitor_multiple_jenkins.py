import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Jenkins and Email Configuration
jenkins_servers = [
    {
        "url": "http://localhost:8080/",  # Jenkins server URL
        "user": "admin",                 # Jenkins username
        "token": "110127711e6a24a04a83fd7b5e2c727ae2",  # Jenkins API token
        "aws_jobs": ["Launch_AWS_Instance", "Launch_AWS_VPC"],  # AWS-related jobs
    }
]

import smtplib

# Mailtrap SMTP Configuration
smtp_server = "sandbox.smtp.mailtrap.io"  # Mailtrap SMTP server
smtp_port = 2525  # Default port for Mailtrap
mailtrap_user = "f5d62e0f4803bf"  # Mailtrap username
mailtrap_password = "af20674b5fddf7"  # Mailtrap password

# Email Configuration
sender = "AWS Monitor <no-reply@aws.com>"
receiver = "Admin <sadhiq1329@gmail.com>"

# Function to send email notifications using Mailtrap
def send_email(subject, body):
    message = f"""\
Subject: {subject}
To: {receiver}
From: {sender}

{body}"""

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(mailtrap_user, mailtrap_password)
            server.sendmail(sender, receiver, message)
        print(f"Email sent to {receiver}")
    except Exception as e:
        print(f"Error sending email: {e}")



# Function to check the status of Jenkins jobs
def check_job_status(jenkins_url, jenkins_user, jenkins_token, job_name):
    # Job-level API URL
    job_url = f"{jenkins_url}/job/{job_name}/api/json"
    response = requests.get(job_url, auth=(jenkins_user, jenkins_token))

    if response.status_code == 200:
        job_info = response.json()
        last_build = job_info.get('lastBuild')  # Safely get lastBuild

        if not last_build:
            print(f"{job_name} has no builds yet.")
            return

        # Fetch details from the build-level API
        build_url = last_build['url'] + 'api/json'
        build_response = requests.get(build_url, auth=(jenkins_user, jenkins_token))

        if build_response.status_code == 200:
            build_info = build_response.json()
            build_status = build_info.get('result')  # Safely get result

            if build_status == "SUCCESS":
                print(f"{job_name} completed successfully.")
                send_email(f"{job_name} - Success", f"The AWS job {job_name} completed successfully.")
            elif build_status == "FAILURE":
                print(f"{job_name} failed.")
                send_email(f"{job_name} - Failure", f"The AWS job {job_name} failed.")
            elif build_status is None:
                print(f"{job_name} is still running or has no result yet.")
            else:
                print(f"{job_name} has an unexpected status: {build_status}")
        else:
            print(f"Error accessing build details for {job_name}: {build_response.status_code}")
    else:
        print(f"Error accessing job {job_name}: {response.status_code}")

# Main function to monitor all Jenkins servers and their AWS-related jobs
def monitor_aws_jobs():
    print("Starting AWS job monitoring...")
    for server in jenkins_servers:
        print(f"Checking server: {server['url']}")
        for job in server['aws_jobs']:
            print(f"Checking job: {job}")
            check_job_status(server['url'], server['user'], server['token'], job)
    print("AWS job monitoring completed.")

# Entry point
if __name__ == "__main__":
    monitor_aws_jobs()
