from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Source, Income
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.utils.timezone import now
import numbers





@login_required(login_url="/auth/login")
def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes = Income.objects.filter(
                    amount__istartswith= search_str  , owner=request.user) | Income.objects.filter(
                    date__istartswith=search_str     , owner=request.user) | Income.objects.filter(
                    source__icontains=search_str   , owner=request.user) | Income.objects.filter(
                    description__icontains=search_str, owner=request.user) 
        data = incomes.values() #Returns a list of all the values in the dictionary (Queryset)
        return JsonResponse(list(data), safe=False) # safe parameter for parsing list {not object} data without problems
    
    


@login_required(login_url="/auth/login")
def index(request):
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    pg_number = request.GET.get('page')
    pg_object = Paginator.get_page(paginator,pg_number)
    currency = UserPreference.objects.get(user= request.user).currency
    context ={
        'incomes': income,
        'currency': currency,
        "pg_object":pg_object,
    }
    return render(request,'income/index.html', context)


@login_required(login_url="/auth/login")
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source')
        date = request.POST.get('income_date')
        if not date : date = now()
        owner = request.user
        if not amount :
            messages.add_message(request, messages.ERROR,'Amount is required.')
            return render(request,'income/add.html', context=context)
        
        if not description:
            messages.add_message(request, messages.ERROR,'Description is required.')
            return render(request,'income/add.html', context=context)
        income = Income.objects.create(
            amount=amount, 
            source=source,
            date=date, 
            owner=owner, 
            description=description,
        )
        messages.add_message(request, messages.SUCCESS, 'Income is saved successfully')
        return redirect('income')
    return render(request,'income/add.html', context=context)


@login_required(login_url="/auth/login")
def edit_income(request,id):
    income = Income.objects.get(id=id)
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': income,
    }
    if request.method=='POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source')
        date = request.POST.get('income_date')
        owner = request.user
        
        if not amount:
            messages.add_message(request, messages.ERROR,'Amount is required.')
            return render(request,'income/edit.html', context=context)
            
        if not description:
            messages.add_message(request, messages.ERROR,'Description is required.')
            return render(request,'income/edit.html', context=context)
        
        income.amount = amount
        income.source = source
        income.date = date
        income.owner = owner
        income.description = description
        income.save()
        messages.add_message(request, messages.SUCCESS,'Income has been updated successfully.')
        return redirect('income')
    return render(request,'income/edit.html', context=context)




@login_required(login_url="/auth/login")
def delete_income(request,id):
    income = Income.objects.get(id=id)
    income.delete()
    messages.add_message(request, messages.SUCCESS, 'Income has been deleted.')
    return redirect('income')