from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.utils.timezone import now
import datetime
import csv
import xlwt
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum





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



@login_required(login_url="/auth/login")
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=180)
    final_rep={}
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    
    def get_category(expense):
        return expense.category
    
    category_list = list(set(map(get_category,expenses)))
    
    def get_expense_category_amount(category):
        amount=0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
            
        return amount
    

    for y in category_list:
        final_rep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': final_rep}, safe=False)



def stats_view(request):
    return render(request, 'expenses/stats.html')



def export_csv(request):
    response = HttpResponse(content_type='text/csv',
        headers={'Content-Disposition': "attachment; filename=expenses "+str(datetime.datetime.now())+".csv"},)
    
    writer = csv.writer(response)
    writer.writerow(['Amount','Category','Description','Date'])
    expenses = Expense.objects.filter(owner=request.user)
    for exp in expenses:
        import pdb ; pdb.set_trace()
        writer.writerow([exp.amount, exp.category, exp.description, exp.date])
        
    return response



def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=expenses '+str(datetime.datetime.now())+'.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount','Category','Description','Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount','category','description','date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response



def export_pdf(request):
    response = HttpResponse(content_type='text/pdf',
        headers={'Content-Disposition': "attachment; filename=expenses "+str(datetime.datetime.now())+".pdf"},)
    response['Content-Transfer-Encoding'] = 'binary'
    
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))
    try:
        currency = UserPreference.objects.get(user= request.user).currency

    except:
        currency = None
    context = {'expenses':expenses, 'currency':currency, 'total': sum['amount__sum']}
    
    #rendered
    html_string = render_to_string('expenses/pdf-output.html',context)
    html = HTML(string=html_string)
    result = html.write_pdf()
    
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        # import pdb ; pdb.set_trace()
        output=open(output.name, 'rb')
        response.write(output.read())
    
    return response