"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object.
    This handles serialization and deserialization of User objects.
    """

    class Meta:
        """Configure the serializer.
        Specifies the model to use and the fields to expose.
        """
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            # Ensures password is not readable and enforces minimum length.
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        """Create and return a new user with an encrypted password.

        - Uses `create_user` method from the custom user model to ensure password hashing.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return the user.

        - If a password is provided, it's hashed before saving.
        - Calls `super().update()` to handle other field updates.
        """
        password = validated_data.pop(
            'password', None)  # Extracts password if provided, else None.
        # Calls the default update method.
        user = super().update(instance, validated_data)

        if password:
            # Hashes the new password before saving.
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token.

    - Handles validation of user credentials.
    - Returns the authenticated user if credentials are valid.
    """
    email = serializers.EmailField()  # Expects a valid email format.
    password = serializers.CharField(
        style={'input_type': 'password'},
        # Ensures password is masked when entered.
        trim_whitespace=False,
        # Avoids stripping spaces as some passwords may contain spaces.
    )

    def validate(self, attrs):
        """Validate and authenticate the user.

        - Uses Django's `authenticate` function to verify credentials.
        - Raises a validation error if authentication fails.
        - Adds the authenticated user to `attrs` for further processing.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            # Passes request context for authentication.
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            # Standard error message for failed authentication.
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        # Stores the authenticated user in attrs for use in views.
        attrs['user'] = user
        return attrs
