from app.utils.class_utils import Injectable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

class EmailService(Injectable):
    def __init__(self):
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port_ssl = 465

    def send_email(self, recipient, subject, template_path, html=False, template_data=None):
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = self.email
        message['To'] = recipient

        if html:
            html_content = self.load_template_from_file(template_path)
            if template_data:
                html_content = self.render_template(html_content, template_data)
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
        else:
            text_content = self.load_template_from_file(template_path)
            text_part = MIMEText(text_content, 'plain')
            message.attach(text_part)

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, recipient, message.as_string())

    def load_template_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def render_template(self, template_string, data):
        for key, value in data.items():
            template_string = template_string.replace(f"{{{{{key}}}}}", str(value))
        return template_string