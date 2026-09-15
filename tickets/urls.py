from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/new/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    path('admin-panel/stats/', views.admin_stats, name='admin_stats'),
    path('admin-panel/agents/', views.manage_agents, name='manage_agents'),
    path('admin-panel/agents/<int:user_id>/toggle/', views.toggle_agent_active, name='toggle_agent_active'),
    path('admin-panel/categories/', views.manage_categories, name='manage_categories'),
    path('admin-panel/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
]
