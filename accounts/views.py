from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import logout
from .models import User
from .serializers import UserListSerializer, ProcurementOfficerRegistrationSerializer, AdminRegistrationSerializer, \
	UserProfileUpdateSerializer, UserPasswordUpdateSerializer


# views here

class AdminRegistrationView(APIView):
    """
    API endpoint for admin user registration.
    """

    def post(self, request):
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcurementOfficerRegistrationView(APIView):
    """
    API endpoint for procurement officer registration.
    """

    def post(self, request):
        serializer = ProcurementOfficerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """
    API endpoint for listing users (requires admin privileges).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('username')
        if hasattr(self, 'serializer_class'):  # Use optional serializer if defined
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data)
        else:
            user_data = []
            for user in users:
                user_type = 'admin' if user.is_admin else (
                    'procurement_officer' if user.is_procurement_officer else 'unknown'
                )
                user_data.append({
                	'user_id':user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user_type,
                })
            return Response(user_data)


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Validate username and password are provided
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid username!'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using Django's check_password method
        if not user.check_password(password):
            return Response({'error': 'Invalid password!'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and return auth token and user type
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user_id':user.id,
        	'token': token.key,
        	'is_procurement_officer':user.is_procurement_officer,
        	'is_admin':user.is_admin
        	}, 
        	status=status.HTTP_200_OK)


class UserProfileUpdateView(APIView):
    """
    API endpoint for authenticated users to update their profile.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordUpdateView(APIView):
    """
    API endpoint for authenticated users to update their password.
    """
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = UserPasswordUpdateSerializer(user, data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout.
    """

    def post(self, request):
        logout(request)  # Logs out the user using DRF's logout function

        # Optional token invalidation (consider if using tokens)
        # token, _ = Token.objects.get_or_create(user=request.user)
        # token.delete()

        return Response({'message': 'Successfully logged out'})
