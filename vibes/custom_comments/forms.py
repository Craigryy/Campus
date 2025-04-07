import dns.resolver
import cachetools
import email_validator
from email_validator import validate_email, EmailNotValidError

from django import forms
from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django_comments.forms import CommentForm

email_validator.TEST_ENVIRONMENT=settings.EMAIL_VALIDATOR_TEST_ENV
username_validator = UnicodeUsernameValidator()

# Create an LRU cache with a maximum size of 100 entries
dns_cache = cachetools.LRUCache(maxsize=200)

# Custom DNS resolver function that uses the LRU cache
def cached_dns_resolver(domain):
    try:
        # Check if the domain's MX records are cached
        if domain in dns_cache:
            return dns_cache[domain]
        else:
            # Perform DNS query and cache the result in the LRU cache
            answers = dns.resolver.resolve(domain, 'MX')
            dns_cache[domain] = answers
            return answers
    except dns.resolver.NoAnswer:
        return None
    except dns.resolver.NXDOMAIN:
        return None

# Function to validate email address and check DNS with LRU cache
def validate_email_with_lru_cache(email):
    try:
        # Validate the email's syntax and domain
        valid = validate_email(email)

        # Extract the domain from the validated email
        domain = valid.email.split('@')[1]

        # Perform DNS lookup with LRU cache
        mx_records = cached_dns_resolver(domain)
        if mx_records:
            return valid.normalized, "Valid email with MX records"
        else:
            return valid.normalized, "Valid email, but no MX records found"

    except EmailNotValidError as e:
        # Email not valid
        return None, str(e)


class CommentForm(CommentForm):
    name = forms.CharField(label="Username", max_length=50, validators=[username_validator])

    def __init__(self, *args, **kwargs):
        # Capture target_object from the kwargs
        super().__init__(*args, **kwargs)

        self.fields.pop('url', None)

    # Add clean_email method for email validation
    def clean_email(self):
        email = self.cleaned_data['email']

        # Validate the email address and check DNS records with LRUCache
        validated_email, message = validate_email_with_lru_cache(email)

        if not validated_email:
            raise forms.ValidationError(f"Invalid email: {message}")

        # Return the validated email if everything is correct
        return validated_email


    # Site ID should be sent from tbe form?
    def get_comment_create_data(self, **kwargs):
        """
        Override this method to customize the data sent when creating a comment.
        """

        data = super().get_comment_create_data(**kwargs)
        data['user_name'] = self.cleaned_data['name']
        return data
