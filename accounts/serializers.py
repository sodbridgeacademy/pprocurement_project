from rest_framework import serializers
from .models import User


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'is_admin', 'is_procurement_officer', 'password')
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user

class AdminRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user registration.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            password=validated_data['password'],
            is_admin=True, 
        )
        return user


class ProcurementOfficerRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for procurement officer registration.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            password=validated_data['password'],
            is_procurement_officer=True 
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users with user type information.
    """
    user_type = serializers.SerializerMethodField()

    def get_user_type(self, obj):
        if obj.is_admin:
            return 'admin'
        elif obj.is_procurement_officer:
            return 'procurement_officer'
        else:
            return 'unknown user!' 

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile (excluding password).
    """

    class Meta:
        model = User
        fields = ('username', 'email')


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user password.
    """

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate_current_password(self, value):
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError('Incorrect current password')
        return value

    def save(self, validated_data):
        user = self.context.get('user')
        user.set_password(validated_data['new_password'])
        user.save()
        return user
