from app.utils.class_utils import Injectable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import os
import qrcode
from io import BytesIO

class EmailService(Injectable):
    def __init__(self):
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port_ssl = 465

    def send_email(self, recipient, subject, template_path, html=False, template_data=None, qrCode=None):
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = self.email
        message['To'] = recipient

        if html:
            html_content = self.load_template_from_file(template_path)
            if template_data:
                html_content = self.render_template(html_content, template_data)

            if qrCode:
                qr_code_img = self.generate_qr_code(qrCode)
                qr_code_cid = 'qr_code_cid'
                html_content = html_content.replace('{{code}}', f'<img src="cid:{qr_code_cid}" alt="QR Code" />')

                html_part = MIMEText(html_content, 'html')
                message.attach(html_part)

                img_part = MIMEImage(qr_code_img)
                img_part.add_header('Content-ID', f'<{qr_code_cid}>')
                message.attach(img_part)
            else:
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
    
    def generate_qr_code(self, url):
        """
        Genera un código qr para la devolución

        """
        qr = qrcode.QRCode(
            version=1,  
            error_correction=qrcode.constants.ERROR_CORRECT_L,  
            box_size=10,  
            border=4,  
        )

        # Agregar la URL al objeto QRCode
        qr.add_data(url)
        qr.make(fit=True)

        # Crear una imagen del código QR en formato de bytes
        img = qr.make_image(fill='black', back_color='white')
        byte_arr = BytesIO()
        img.save(byte_arr)
        byte_arr.seek(0)

        return byte_arr.read()