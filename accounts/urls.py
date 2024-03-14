from django.urls import path
from .views import AdminRegistrationView, ProcurementOfficerRegistrationView, UserListView, UserLoginAPIView, \
	UserProfileUpdateView, UserPasswordUpdateView, UserLogoutView

urlpatterns = [
    path('admin/register/', AdminRegistrationView.as_view(), name='admin_register'),
    path('procurement-officer/register/', ProcurementOfficerRegistrationView.as_view(), name='procurement_officer_register'),
    path('users/', UserListView.as_view()),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('profile/update/', UserProfileUpdateView.as_view()),
    path('password/update/', UserPasswordUpdateView.as_view()),
    path('logout/', UserLogoutView.as_view()),
]
