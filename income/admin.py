from django.contrib import admin
from .models import Source, Income
# Register your models here.


class IncomeAdmin(admin.ModelAdmin):
    list_display = ['amount', 'source','owner', 'description', 'date']
    search_fields = ( 'source','date','description',)
    list_per_page = 5
    
admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)