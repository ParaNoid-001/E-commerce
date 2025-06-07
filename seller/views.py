from django.shortcuts import render, redirect
from core.decorators import login_role_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import logout
from core.decorators import login_role_required

# Create your views here.

@login_role_required("seller")
def seller_dashboard_view(request):
    return render(request, 'seller/seller_dashboard.html')

@login_role_required("seller")
def change_password_view(request):
    if request.method == 'POST':
        # Use request.POST, not request.data.POST
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)  # Log out the user after changing the password
            messages.success(request, "Password changed successfully. Please log in with your new password.")
            return redirect('login')  # Make sure to return the redirect
    
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'seller/password_change.html',{'form':form})