from django.urls import path
from .views import RegistrationView, LoginView, UsernameValidationView, EmailValidationView, activate_user, SetNewPassword, LogoutView, RequestPasswordResetEmailView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register/', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('reset-password', RequestPasswordResetEmailView.as_view(), name="request-password"),
    path('set-new-password/<slug:uidb64>/<slug:token>/', SetNewPassword.as_view(), name="set-new-password"),
    
    ## ajax request for username and email validation
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"),
    ## activation url
    path('activate/<slug:uidb64>/<slug:token>/',activate_user, name='activate'),
    
]