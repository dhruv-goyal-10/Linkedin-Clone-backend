from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException
import re

class CustomValidation(APIException):
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        
        if status_code is None:
            self.status_code = self.default_status_code
        else:
            self.status_code = status_code
            
        if detail is None:
            self.detail = {'detail': force_str(self.default_detail)}
        else: 
            if(field == 'multiple'):
                self.detail = {"non_field_errors": force_str(detail)}
            else:
                self.detail = {field: force_str(detail)}
                 
                
def normalize_email(email):
        
        email = email or ''
        try:
            email_name, domain_part = email.lower().strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email
    
    
def check_strong_password(password):
        if (len(password) < 8 or 
            (not re.findall('\d', password)) or 
            (not re.findall('[A-Z]', password)) or 
            (not re.findall('[a-z]', password))or 
            (not re.findall('[!@#$%&*]', password))):
            return False
        else:
            return True