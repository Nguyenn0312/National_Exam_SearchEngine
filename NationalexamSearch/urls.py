"""
URL configuration for NationalexamSearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from .views import StudentListAPI, FilterAPI, StudentDetailAPI
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.search_results, name='home'), 
    path('search/<str:search_query>/', views.search_results, name='search_clean'), 
    path('api/search/<int:sbd>/', StudentDetailAPI.as_view(), name='api-student-detail'),
    path('api/filter/', FilterAPI.as_view(), name='api-filter'),
]