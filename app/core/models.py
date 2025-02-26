import uuid
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,  # Provides authentication features like password hashing.
    BaseUserManager,  # Manages user creation logic.
    PermissionsMixin,  # Adds permission-related functionality.
)


def profile_image_file_path(instance, filename):
    """Generate file path for new profile image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'profile', filename)


def blog_media_file_path(instance, filename):
    """Generate file path for blog media (images/videos)."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'blog', filename)


# List of predefined statuses for users to choose from
STATUS_CHOICES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('complicated', 'It’s Complicated'),
    ('engaged', 'Engaged'),
]


class UserManager(BaseUserManager):
    """Manager for user accounts, handling creation of users and superusers."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save, and return a new user.
        """
        if not email:
            raise ValueError('User must have an email address.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create and return a new superuser with admin privileges.
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports email-based authentication instead of usernames.
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Profile model for storing user profile details."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    image = models.ImageField(
        upload_to=profile_image_file_path,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='single'
    )

    def __str__(self):
        return f"{self.user.name}'s Profile"


class Relationship(models.Model):
    """
    Relationship model to track user connections (e.g., friends, followers).
    """
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Prevent duplicate relationships

    def __str__(self):
        return f"{self.from_user.name} follows {self.to_user.name}"


class Blog(models.Model):
    """
    Blog model to store blog posts.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BlogMedia(models.Model):
    """
    Model to store media files (images/videos) related to blog posts.
    """
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='media'
    )
    file = models.FileField(upload_to=blog_media_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for {self.blog.title}"
