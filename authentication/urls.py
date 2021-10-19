from django.urls import path
from .views import RegistrationView, LoginView, UsernameValidationView, EmailValidationView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register/', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    ## ajax request for username and email validation
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"),
]