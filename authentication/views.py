from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_str, force_text
from .utils import generate_token
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator




class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        print(data)
        username = data['username']
        if not str(username).isalpha():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        
        return JsonResponse({'username_valid': True})
    
    
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Inavalid email'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use,choose another one '}, status=409)
        
        return JsonResponse({'email_valid': True})
    
    


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()




################### send activation mail ######################
def send_activation_email(user, request):
    current_site = get_current_site(request)
    ######################### send mail with email template ####################################
    htmly = get_template('authentication/Email.html')
    context = {
        'user':user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    }
    subject, from_email,to = 'Activate your account', settings.EMAIL_HOST_USER, user.email
    html_content = htmly.render(context)
    email = EmailMultiAlternatives(subject, html_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")

    if not settings.TESTING:
        EmailThread(email).start()

    
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        context = {'data': request.POST}
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.add_message(request, messages.ERROR,'Password should be at least 6 characters')
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()
                send_activation_email(user, request)
                messages.add_message(request, messages.SUCCESS,'We sent you an email to verify your account, check your inbox.')
                return redirect('login')
        return render(request, 'authentication/register.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        context = {'data': request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username= username, password= password)
        if user and not user.is_active:
            messages.add_message(request, messages.ERROR,'Email is not verified, please check your email inbox')
            return render(request, 'authentication/login.html', context, status=401)
        if not user:
            messages.add_message(request, messages.ERROR,'wrong user or password')
            return render(request, 'authentication/login.html', context, status=401)
        
        login(request, user)
        messages.add_message(request, messages.SUCCESS,f'Welcome {user.username}')
        return redirect(reverse('expenses'))
    


def activate_user (request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id = uid)
    except Exception as e:
        user = None
    if user and generate_token.check_token(user,token):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.SUCCESS,'Email has been verified, you can now login')
        return redirect(reverse('login'))
    
    messages.add_message(request, messages.Error,'expired link , do you want to resend another one')
    return redirect(reverse('login'))


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS,'Logged out successfully')
        return redirect('login')
        



################### send reset password mail ######################
def send_reset_password_email(user, request):
    current_site = get_current_site(request)
    ######################### send mail with email template ####################################
    htmly = get_template('authentication/resetEmail.html')
    context = {
        'user':user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': PasswordResetTokenGenerator().make_token(user)
    }
    subject, from_email,to = 'Reset your password', settings.EMAIL_HOST_USER, user.email
    html_content = htmly.render(context)
    email = EmailMultiAlternatives(subject, html_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")

    if not settings.TESTING:
        EmailThread(email).start()

        
        
class RequestPasswordResetEmailView(View):
    def get(self, request):
        return render(request, 'authentication/password_reset.html')
    
    def post(self, request):
        email = request.POST.get('email')
        if not validate_email(email):
            messages.add_message(request, messages.ERROR,'Please, supply a valid email address.')
            return render(request, 'authentication/password_reset.html', context={'values': request.POST})
        
        user = User.objects.filter(email=email)
        if not user:
            messages.add_message(request, messages.ERROR,"You don't have an account with this email address")
            return render(request, 'authentication/password_reset.html', context={'values': request.POST})
        send_reset_password_email(user[0],request)
        messages.add_message(request, messages.SUCCESS,"We sent you a reset link , please check your inbox.")
        return render(request, 'authentication/password_reset.html', context={'values': request.POST})



class SetNewPassword(View):
    def get(self,request, uidb64, token):
        try:
            uid= force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id = uid)
            # import pdb ; pdb.set_trace()
            
            context = {'uidb64': uidb64, 'token': token}
        except Exception as e:
            user = None
        if user and PasswordResetTokenGenerator().check_token(user,token): # check_token is for not using the link again after resetting once
            
            messages.add_message(request, messages.SUCCESS,'Now, You can set a new password.')
            return render(request, 'authentication/set_newPassword.html', context)
        else:
            messages.add_message(request, messages.ERROR,'Something went  wrong. Please try again')
            return redirect('request-password')
        
        
    def post(self, request, uidb64, token):
        uid= force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id = uid)
        context = {'uidb64': uidb64, 'token': token}
        password = request.POST.get('password')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,'Password should be at least 6 characters')
            return render(request, 'authentication/set_newPassword.html', context)
        user.set_password(password)
        user.save()
        messages.add_message(request, messages.SUCCESS,'password has been set successfully.')
        return redirect('login')