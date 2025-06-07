from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading

class SendEmailThread(threading.Thread):
    def __init__(self, email):
        super().__init__()  # Initialize the thread using super
        self.email = email
        
    def run(self):
        self.email.send()

def send_activation_email(recipient_email, activation_url):
    subject = f"Activate Your Account on {settings.SITE_NAME}"
    from_email = "no_reply@ggeshop.com"
    to_email = [recipient_email]
    
    # Load the HTML template
    html_content = render_to_string('account/email_activation.html', {'activation_url': activation_url})
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    SendEmailThread(email).start()

def send_reset_password_email(recipient_email, reset_url):
    subject = f"Reset your Password on {settings.SITE_NAME}"
    from_email = "no_reply@ggeshop.com"
    to_email = [recipient_email]
    
    # Load the HTML template
    html_content = render_to_string('account/email_reset_password.html', {'reset_url': reset_url})
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    SendEmailThread(email).start()
