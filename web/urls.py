from django.urls import path
from . import views

urlpatterns = [
    path('submit/expense/', views.submit_expense, name = 'submit_expense'),
    path('submit/income/', views.submit_income, name = 'submit_income'),
    path('accounts/register/', views.register, name = 'register'),
    path('', views.index, name = 'index'),
    path('q/generalstat/', views.generalstat, name = 'generalstat'),
    path('accounts/login/', views.login, name = 'login'),
    path('accounts/whoami/', views.whoami, name = 'whoami'),
    path('news/', views.news, name = 'news'),
    path('q/expense/', views.query_expense, name = 'query_expense'),
    path('q/income/', views.query_income, name = 'query_income'),
]
