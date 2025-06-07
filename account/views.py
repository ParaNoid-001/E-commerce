from .view_imports import *

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            
            if form.cleaned_data['role'] == "seller":
                user.is_seller = True
            else:
                user.is_customer = True
                
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'
            send_activation_email(user.email, activation_url)

            messages.success(request, 'We have sent an account activation link. Please check your email to activate your account!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'account/register.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(request, "Account already activated.")
            return redirect('login')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully.")
            return redirect('login')
        messages.warning(request, "Invalid activation link.")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link.")
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_seller:
            return redirect('seller_dashboard')
        return redirect('customer_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Account is inactive.")
                return redirect('login')
                
            login(request, user)
            if user.is_seller:
                return redirect('seller_dashboard')
            return redirect('customer_dashboard')
        messages.error(request, "Invalid email or password.")
    return render(request, 'account/login.html')

def password_reset_view(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse('password_reset_confirm', kwargs={
                                  'uidb64': uidb64, 'token': token})
                absolute_reset_url = f"{request.build_absolute_uri(reset_url)}"
                send_reset_password_email(user.email, absolute_reset_url)
                messages.success(request, "Password reset link sent to your email.")
                return redirect('login')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'account/password/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                
                # Send password reset confirmation email
                context = {
                    'user': user,
                    'timestamp': timezone.now(),
                    'site_name': settings.SITE_NAME   
                }
                subject = 'Your Password Has Been Reset'
                message = render_to_string('emails/password_reset_confirmation.html', context)
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                     html_message=message
                )
                
                
                messages.success(request, "Password reset successfully! A confirmation has been sent to your email.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'account/password/password_reset_confirm.html', {'form': form})
    messages.error(request, "Invalid password reset link.")
    return redirect('password_reset')

# Account Management Views
@login_required
def account_management_view(request):
    addresses = request.user.addresses.all().order_by('-is_default', '-created_at')
    return render(request, 'account/account_management.html', {
        'addresses': addresses
    })

# @login_required
# def account_management_view(request):
#     # Initialize forms
#     profile_form = UserProfileForm(instance=request.user)
#     password_form = CustomPasswordChangeForm(request.user)
#     address_form = AddressForm(user=request.user)

#     if request.method == 'POST':
#         # Handle profile update
#         if 'profile_submit' in request.POST:
#             profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
#             if profile_form.is_valid():
#                 profile_form.save()
#                 messages.success(request, "Profile updated successfully.")
#                 return redirect('account_management')
                
#         # Handle password change
#         elif 'password_submit' in request.POST:
#             password_form = CustomPasswordChangeForm(request.user, request.POST)
#             if password_form.is_valid():
#                 try:
#                     user = password_form.save()
#                     update_session_auth_hash(request, user)
                    
#                     # Send email notification
#                     context = {
#                         'user': user,
#                         'timestamp': timezone.now(),
#                         'site_name': 'Your Site Name'
#                     }
                    
#                     subject = 'Password Changed Successfully'
#                     message = render_to_string(
#                         'emails/password_change_notification.html',
#                         context
#                     )
                    
#                     send_mail(
#                         subject,
#                         message,
#                         None,  # Uses DEFAULT_FROM_EMAIL
#                         [user.email],
#                         html_message=message
#                     )
                    
#                     messages.success(request, "Your password was successfully updated!")
#                     return redirect('account_management')
#                 except Exception as e:
#                     messages.error(request, f"Error changing password: {str(e)}")
        
#         # Handle address addition
#         elif 'address_submit' in request.POST:
#             address_form = AddressForm(request.POST, user=request.user)
#             if address_form.is_valid():
#                 address = address_form.save(commit=False)
#                 address.user = request.user
                
#                 # If setting as default, unset any existing default
#                 if address.is_default:
#                     Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                
#                 address.save()
#                 messages.success(request, "Address added successfully.")
#                 return redirect('account_management')

#     context = {
#         'profile_form': profile_form,
#         'password_form': password_form,
#         'address_form': address_form,
#         'addresses': request.user.addresses.all(),
#     }
#     return render(request, 'account/account_management.html', context)

# Add Address View
@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If setting as default, unset any existing default
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('account_management')
    else:
        form = AddressForm(user=request.user)
    
    return render(request, 'account/address/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            # If setting as default, unset any existing default
            if form.cleaned_data['is_default']:
                Address.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)
            
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('account_management')
    else:
        form = AddressForm(instance=address, user=request.user)
    
    return render(request, 'account/address/edit_address.html', {'form': form, 'address': address})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('account_management')
    
    return render(request, 'account/address/confirm_delete_address.html', {'address': address})

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Set all addresses to non-default first
    Address.objects.filter(user=request.user).update(is_default=False)
    
    # Set this one as default
    address.is_default = True
    address.save()
    
    messages.success(request, f"'{address.address_name}' is now your default address")
    return redirect('account_management')

@login_required
def profile_update_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('account_management')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'account/profile_update.html', {'form': form})

# Password Change View
@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Send email notification
            context = {
               'user': user,
                'timestamp': timezone.now(),
                'site_name': settings.SITE_NAME
            }
            
            subject = 'Password Changed Successfully'
            message = render_to_string(
                'emails/password_change_notification.html',
                context
            )
            
            send_mail(
                subject,
                message,
                None,  # Uses DEFAULT_FROM_EMAIL
                [user.email],
                html_message=message
            )
                
                
            messages.success(request, "Your Password updated successfully!")
            return redirect('account_management')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'account/password/password_change.html', {'form': form})

# Delete Account View
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')
    
    return render(request, 'account/confirm_delete_account.html')


# @login_required
# def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Account deleted successfully.")
        return redirect('home')
    return redirect('account_management')

def admin_registration(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin account created successfully.")
            return redirect('/admin/login/')
    else:
        form = AdminRegistrationForm()
    return render(request, 'account/admin_registration.html', {'form': form})