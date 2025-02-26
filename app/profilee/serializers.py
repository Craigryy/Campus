from rest_framework import serializers
from core.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'image', 'status','like_count', 'number']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Only show 'number' if the user has paid."""
        data = super().to_representation(instance)
        if not instance.is_paid:
            data.pop('number', None)  # Hide number field
        return data
