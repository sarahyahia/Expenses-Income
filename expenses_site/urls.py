"""expenses_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', TemplateView.as_view(template_name='expenses/index.html')),
    path('', include('expenses.urls')),
    path('income/', include('income.urls')),
    path('auth/', include('authentication.urls')),
    path('pref/', include('userpreferences.urls')),
    path('accounts/', include('allauth.urls')),
]


# handler404 = 'helpers.views.handle_not_found'
# handler500 = 'helpers.views.handle_server_error'