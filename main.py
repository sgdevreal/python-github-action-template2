import logging
import logging.handlers
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["EMAIL_ME"]
    EMAIL_PASSWORD_ME = os.environ["EMAIL_PASSWORD_ME"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise


if __name__ == "__main__":
    logger.info(f"Token value: {SOME_SECRET}")
    
    def send_email(sender_email, sender_password, receiver_email, subject, body):
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Add body to the email
        message.attach(MIMEText(body, "plain"))

        # Create SMTP session for sending the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Enable secure connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    # Provide the necessary information
    sender_email = SOME_SECRET
    sender_password = EMAIL_PASSWORD_ME
    receiver_email = SOME_SECRET
    subject = "Hello from Python!"
    body = "This is the body of the email."

    # Call the send_email function
    send_email(sender_email, sender_password, receiver_email, subject, body)
