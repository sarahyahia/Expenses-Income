from django.contrib import admin
from .models import Category, Expense
# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['amount', 'category','owner', 'description', 'date']
    search_fields = ( 'category','date','description',)
    list_per_page = 5
    
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)