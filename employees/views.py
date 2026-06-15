from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Employee
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.contrib.auth import logout as django_logout

# ==========================================================
# 1. CORE GATEWAY OPERATIONS
# ==========================================================

# SYSTEM HOME INTERFACE & LOCK GATEWAY NODE
def home_view(request):
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
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        username = email.split('@')[0] # Corporate email ka first part username banega

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


# LOGOUT GATEWAY HANDLER (FIXED LOOP)
def logout_view(request):
    django_logout(request)
    messages.info(request, "CONNECTION_TERMINATED // Core node safely disconnected from system.")
    return redirect('home')


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
            attrition=False,
            is_deleted=False
        )

        messages.success(request, f"SUCCESS // Agent record for '{name}' has been safely injected into core database.")
        return redirect('employee_list') 
        
    return render(request, 'employees/add_employee.html')


# READ - VIEW ALL LOGGED AGENT MATRIX LISTS (FIXED & COMPLETED)
@login_required
def employee_list(request):
    try:
        # Django mein order_index() nahi hota, order_by() hota hai. Fallback safe lagaya hai id par.
        employees = Employee.objects.filter(is_deleted=False).order_by('id')
    except Exception:
        employees = Employee.objects.filter(is_deleted=False)
    
    return render(request, 'employees/employee_list.html', {'employees': employees})


# UPDATE - EDIT AGENT STRUCTURAL RECONFIGURATIONS (TUNED TO PK KEYWORD)
@login_required
def update_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.department = request.POST.get('department')
        employee.salary = request.POST.get('salary')
        employee.performance_score = request.POST.get('performance_score')
        
        if request.FILES.get('profile_pic'):
            employee.profile_pic = request.FILES.get('profile_pic')

        if request.POST.get('attrition'):
            employee.attrition = True
        else:
            employee.attrition = False
        employee.save()

        messages.success(request, f"UPDATED // Core variables for '{employee.name}' modified successfully.")
        return redirect('employee_list')
    return render(request, 'employees/update_employee.html', {'employee': employee})


# DELETE - PURGE AN AGENT ROW INSTANCE COMPLETELY (SOFT DELETE LINKED)
@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_deleted = True
    employee.save()
    messages.success(request, f"MOVED // '{employee.name}' record shifted to recycle bin node.")
    return redirect('employee_list')


# READ - INDIVIDUAL PROFILE DETAILS HANDLER
@login_required
def employee_profile(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_profile.html', {'employee': employee})


# ==========================================================
# 4. DATA PIPELINE FILE COMPILATION
# ==========================================================

# EXPORT EXCEL DATAFRAME (FIXED TRY-EXCEPT LOGIC)
@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="matrix_active_employees.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Active Matrix Records"
    
    ws.views.sheetView[0].showGridLines = True
    
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid") 
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF") 
    data_font = Font(name="Segoe UI", size=10, color="111827")
    
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )
    
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    
    headers = ['Employee Name', 'Email Address', 'Department', 'Current Salary', 'Performance Score', 'System Status']
    ws.append(headers)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    
    ws.row_dimensions[1].height = 26
    
    active_employees = Employee.objects.filter(is_deleted=False)
    
    for row_idx, emp in enumerate(active_employees, start=2):
        # Salary Conversion Logic
        try:
            salary_val = float(emp.salary) if emp.salary else 0.0
        except (ValueError, TypeError):
            salary_val = 0.0

        # Performance Score Conversion Logic (Fixed Scope)
        try:
            score_val = float(emp.performance_score) if emp.performance_score else 0.0
        except (ValueError, TypeError):
            score_val = 0.0            
            
        status = "Left" if emp.attrition else "Active"
        
        ws.append([
            emp.name, 
            emp.email, 
            emp.department, 
            salary_val, 
            score_val, 
            status
        ])
        
        ws.row_dimensions[row_idx].height = 20
        
        row_cells = ws[row_idx]
        row_cells[0].alignment = left_align   
        row_cells[1].alignment = left_align   
        row_cells[2].alignment = center_align 
        row_cells[3].alignment = left_align   
        row_cells[4].alignment = center_align 
        row_cells[5].alignment = center_align 
        
        row_cells[3].number_format = '₹#,##0.00'
        
        for cell in row_cells:
            cell.font = data_font
            cell.border = thin_border
            
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                val_str = f"₹{cell.value:,.2f}" if isinstance(cell.value, (int, float)) and cell.column == 4 else str(cell.value)
                if len(val_str) > max_len:
                    max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    wb.save(response)
    return response


@login_required
def help_view(request):
    return render(request, 'employees/help.html')


@login_required
def recycle_bin_view(request):
    deleted_employees = Employee.objects.filter(is_deleted=True)
    return render(request, 'employees/recycle_bin.html', {'employees': deleted_employees})


@login_required
def restore_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_deleted = False
    employee.save()
    messages.success(request, f"RESTORED // Node '{employee.name}' has been safely re-allocated to active matrix.")
    return redirect('recycle_bin')