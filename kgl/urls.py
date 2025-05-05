"""
URL configuration for kgl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from home import views
from django.contrib.auth import views as auth_views
from home.views import StockDeleteView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.Login, name='login'),  # custom
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.homepage, name='index'),
    path('receipt/', views.receipt, name='receipt'),
    path('receipt_detail/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    path('reports/', views.reports, name='reports'),
    path('allsales/', views.allsales, name='allsales'),
    path('sale_detail/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('addsales/<int:pk>/add/', views.addsales, name='addsales'),
    
    path('allstock/', views.allstock, name='allstock'),
    path('stock_detail/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:pk>/delete/', StockDeleteView.as_view(), name='stock_delete'),
    path('issue_item/<str:pk>/', views.issue_item, name='issue_item'),
    path('addstock/<str:pk>/', views.addstock, name='addstock'),

    path('procurement/', views.procurement_list, name='procurement_list'),
    path('procurements/add/', views.procurement_create, name='procurement_create'),
    path('procurements/<int:pk>/edit/', views.procurement_edit, name='procurement_edit'),
    path('procurements/<int:pk>/delete/', views.procurement_delete, name='procurement_delete'),
    path('procure/', views.procure, name='procure'),

    path('creditsale/', views.creditsale, name='creditsale'),
    path('credit_list/', views.credit_list, name='credit_list'),
    path('credit_detail/<int:credit_id>/', views.credit_detail, name='credit_detail'),
    path('add_credit_sale/', views.add_credit_sale, name='add_credit_sale'),

    path('dashboard/', views.manager, name='dashboard'),
    path('dashboard2/', views.salesagent, name='dashboard2'),
    path('dashboard3/', views.owner, name='dashboard3'),
]