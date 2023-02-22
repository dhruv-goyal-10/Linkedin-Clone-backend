from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from django.conf import settings
from . models import *


class EMAIL:
    @staticmethod
    def send_otp_via_email(mailaddress, otp):
        
        html_content = render_to_string(
            "email_otp.html", {"otp": otp,})

        
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            "Profolio Email Verification",
            text_content,
            settings.EMAIL_HOST,
            [mailaddress]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        
        
    


   