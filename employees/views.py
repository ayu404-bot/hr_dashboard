from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm
import openpyxl
from django.contrib.auth import logout as django_logout

# ==========================================================
# 1. CORE GATEWAY OPERATIONS
# ==========================================================

# SYSTEM HOME INTERFACE & LOCK GATEWAY NODE
def home_view(request):
    # Agar user already logged in hai, toh direct dynamic cockpit dashboard load hoga
    if request.user.is_authenticated:
        return render(request, 'employees/home.html')
    
    # Agar login nahi hai, toh base.html automatic is par login window render karega
    return render(request, 'employees/home.html')


# LOGIN SUBMISSION HANDLER
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"ACCESS_GRANTED // Secure handshake initialized for node: {username}")
            return redirect('home')
        else:
            messages.error(request, "ACCESS_DENIED // Invalid security access keys detected.")
    return redirect('home')


# REGISTER PERSONNEL SUBMISSION HANDLER
def register_page(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        username = request.POST.get('email').split('@')[0] # Corporate email ka first part username banega
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check agar user account already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "REGISTRATION_FAILED // Identity node already mapped in matrix system.")
            return redirect('home')

        # New user account create karna
        new_user = User.objects.create_user(username=username, email=email, password=password)
        
        # Full name setup karne ke liye splitting approach
        name_parts = fullname.split(' ', 1)
        new_user.first_name = name_parts[0]
        if len(name_parts) > 1:
            new_user.last_name = name_parts[1]
        new_user.save()

        # Account creation ke baad system automatic login kara dega
        login(request, new_user)
        messages.success(request, f"NODE_DEPLOYED // Welcome to Matrix Network, {fullname}.")
        return redirect('home')
        
    return redirect('home')


# LOGOUT GATEWAY HANDLER
def logout_view(request):
    django_logout(request)
    messages.info(request, "CONNECTION_TERMINATED // Core node safely disconnected from system.")
    return redirect('login')


# SYSTEM ABOUT Specs NODE
@login_required
def about_view(request):
    return render(request, 'employees/about.html')


# ==========================================================
# 2. MAIN METRICS DATA AGGREGATION
# ==========================================================

@login_required
def dashboard(request):
    active_employees = Employee.objects.filter(is_deleted=False)
    total = active_employees.count()
    active_count = active_employees.filter(attrition=False).count()
    left_count = active_employees.filter(attrition=True).count()

    context = {
        'total': total,
        'active': active_count,
        'left': left_count,
    }
    return render(request, 'employees/dashboard.html', context)


# ==========================================================
# 3. DATABASE SYSTEM CRUD UTILITIES
# ==========================================================

# CREATE - REGISTER NEW EMPLOYEE AGENT
@login_required
def add_employee(request):
    if request.method == "POST":
        # Direct capture from the form fields to avoid validation lockups
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        salary = request.POST.get('salary')
        performance_score = request.POST.get('performance_score')
        profile_pic = request.FILES.get('profile_pic')

        # Directly force insert row instance into SQLite database
        Employee.objects.create(
            name=name,
            email=email,
            department=department,
            salary=salary,
            performance_score=performance_score,
            profile_pic=profile_pic,
            attrition=False
        )

        # Trigger Pop-up and instantly clear memory registry route
        messages.success(request, f"SUCCESS // Agent record for '{name}' has been safely injected into core database.")
        return redirect('employee_list') 
        
    return render(request, 'employees/add_employee.html')


# READ - VIEW ALL LOGGED AGENT MATRIX LISTS
@login_required
def employee_list(request):
    all_employees = Employee.objects.filter(is_deleted=False)
    return render(request, 'employees/employee_list.html', {'employees': all_employees})


# UPDATE - EDIT AGENT STRUCTURAL RECONFIGURATIONS
@login_required
def update_employee(request, pk):
    employee = get_object_or_404(Employee, id=pk)
    if request.method == "POST":
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.department = request.POST.get('department')
        employee.salary = request.POST.get('salary')
        employee.performance_score = request.POST.get('performance_score')
        
        # Request context parsing correct bugs fixed
        if request.FILES.get('profile_pic'):
            employee.profile_pic = request.FILES.get('profile_pic')

        if request.POST.get('attrition'):
            employee.attrition = True
        else:
            employee.attrition = False
        employee.save()

        messages.success(request, f"UPDATED // Core variables for '{employee.name}' modified successfully.")
        return redirect('employee_list')
    return render(request, 'employees/update_employee.html', {'form': employee})


# DELETE - PURGE AN AGENT ROW INSTANCE COMPLETELY
@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, id=pk)
    employee.is_deleted = True
    employee.save()
    messages.success(request, f"MOVED// '{employee.name}' record shifted to recycle bin node.")
    return redirect('employee_list')


# READ - INDIVIDUAL PROFILE DETAILS HANDLER
@login_required
def employee_profile(request, pk):
    employee = get_object_or_404(Employee, id=pk)
    return render(request, 'employees/employee_profile.html', {'employee': employee})


# ==========================================================
# 4. DATA PIPELINE FILE COMPILATION
# ==========================================================

@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="employee_report.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Employees"
    
    headers = ['Name', 'Email', 'Department', 'Salary', 'Performance Score']
    ws.append(headers)
    
    for emp in Employee.objects.all():
        # Added a fallback if salary node is non-numeric string
        try:
            salary_val = float(emp.salary)
        except (ValueError, TypeError):
            salary_val = 0.0
        ws.append([emp.name, emp.email, emp.department, salary_val, emp.performance_score])
        
    wb.save(response)
    return response


@login_required
def help_view(request):
    return render(request,'employees/help.html')


@login_required
def recycle_bin_view(request):
    deleted_employees = Employee.objects.filter(is_deleted=True)
    return render(request,'employees/recycle_bin.html', {'employees': deleted_employees})

@login_required
def restore_employee(request, pk):
    employee = get_object_or_404(Employee, id=pk)
    
    # is_deleted ko wapas False kar do taaki ye active ho jaye
    employee.is_deleted = False
    employee.save()
    
    messages.success(request, f"RESTORED // Node '{employee.name}' has been safely re-allocated to active matrix.")
    return redirect('recycle_bin') # Ya jo bhi aapke recycle bin ka URL name hai