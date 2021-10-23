from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.utils.timezone import now





@login_required(login_url="/auth/login")
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
                    amount__istartswith= search_str  , owner=request.user) | Expense.objects.filter(
                    date__istartswith=search_str     , owner=request.user) | Expense.objects.filter(
                    category__icontains=search_str   , owner=request.user) | Expense.objects.filter(
                    description__icontains=search_str, owner=request.user) 
        data = expenses.values() #Returns a list of all the values in the dictionary (Queryset)
        return JsonResponse(list(data), safe=False) # safe parameter for parsing list {not object} data without problems


@login_required(login_url="/auth/login")
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    pg_number = request.GET.get('page')
    pg_object = Paginator.get_page(paginator,pg_number)
    try:
        currency = UserPreference.objects.get(user= request.user).currency

    except:
        currency = None
    context ={
        'expenses': expenses,
        'currency': currency,
        "pg_object":pg_object,
    }
    return render(request,'expenses/index.html', context=context)



@login_required(login_url="/auth/login")
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('expense_date')
        if not date : date = now()
        owner = request.user
        if not amount :
            messages.add_message(request, messages.ERROR,'Amount is required.')
            return render(request,'expenses/add.html', context=context)
        
        if not description:
            messages.add_message(request, messages.ERROR,'Description is required.')
            return render(request,'expenses/add.html', context=context)
        expense = Expense.objects.create(
            amount=amount, 
            category=category,
            date=date, 
            owner=owner, 
            description=description,
        )
        messages.add_message(request, messages.SUCCESS, 'Expense is saved successfully')
        return redirect('expenses')
    return render(request,'expenses/add.html', context=context)


@login_required(login_url="/auth/login")
def edit_expense(request,id):
    expense = Expense.objects.get(id=id)
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': expense,
    }
    if request.method=='POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('expense_date')
        owner = request.user
        
        if not amount:
            messages.add_message(request, messages.ERROR,'Amount is required.')
            return render(request,'expenses/edit.html', context=context)
        
        if not description:
            messages.add_message(request, messages.ERROR,'Description is required.')
            return render(request,'expenses/edit.html', context=context)
        
        expense.amount = amount
        expense.category = category
        expense.date = date
        expense.owner = owner
        expense.description = description
        expense.save()
        messages.add_message(request, messages.SUCCESS,'Expense has been updated successfully.')
        return redirect('expenses')
    return render(request,'expenses/edit.html', context=context)




@login_required(login_url="/auth/login")
def delete_expense(request,id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    messages.add_message(request, messages.SUCCESS, 'Expense has been deleted.')
    return redirect('expenses')