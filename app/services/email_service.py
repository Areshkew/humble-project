from app.utils.class_utils import Injectable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os


class EmailService(Injectable):
    def __init__(self):
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMPT_PASSWORD")
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port_ssl = 465

    def send_email(self, recipient, subject, body, html=False):
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = self.email
        message['To'] = recipient

        if html:
            html_part = MIMEText(body, 'html')
            message.attach(html_part)
        else:
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, recipient, message.as_string())