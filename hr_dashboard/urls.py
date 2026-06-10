from django.contrib import admin
from django.contrib import messages
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from employees import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-employees/', views.add_employee, name='add_employee'),
    path('employees/', views.employee_list, name='employee_list'),
    path('update-employee/<int:pk>/', views.update_employee, name='update_employee'),
    path('delete-employee/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('about/', views.about_view, name='about'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('profile/<int:pk>/',views.employee_profile,name='employee_profile'),
    path('help/', views.help_view, name='help'),
    path('recycle-bin/', views.recycle_bin_view, name='recycle_bin'),
    path('system/login-auth/', views.login_page, name='login'),
    path('system/register-node/', views.register_page, name='register'),
    path('system/logout/', views.logout_view, name='logout'),
    path('recycle-bin/restore/<int:pk>/', views.restore_employee, name='restore_employee')
]

# CRITICAL NODE APPEND: Allows local server matrix execution to stream media file paths
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)