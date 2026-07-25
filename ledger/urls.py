from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry_view, name='entry'),
    path('weekly/', views.weekly_view, name='weekly'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('income/', views.income_view, name='income'),
    path('entry/<int:pk>/edit/', views.entry_edit_view, name='entry_edit'),
    path('income/<int:pk>/edit/', views.profit_edit_view, name='profit_edit'),
    path('signin/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('import-csv/', views.import_view, name='import_csv'),
]
