from django.shortcuts import render
import os, json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages


def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k,v in data.items():
            currency_data.append({'name': k, 'value':v})
        user_preferences = None
        is_exist = UserPreference.objects.filter(user=request.user).exists()
        if is_exist:
            user_preferences = UserPreference.objects.get(user=request.user)
    
    if request.method == 'POST':
        currency = request.POST['currency']
        if is_exist:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.add_message(request, messages.SUCCESS,'Currency has been saved successfully.')
        
    return render(request, 'preferences/index.html',{'currencies':currency_data,'user_preferences': user_preferences})