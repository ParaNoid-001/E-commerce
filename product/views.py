# views.py
from .product_view_imports import *
# Read Operation
# @permission_required('product.view_product', raise_exception=True)

logger = logging.getLogger(__name__)


class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        wishlist_count = 0

        # Get sorting parameter
        sort_by = request.GET.get('sort', 'name')
        valid_sorts = ['name', 'price', '-price', '-created_at']
        sort_by = sort_by if sort_by in valid_sorts else 'name'

        # Get category filter by name
        category_name = request.GET.get('category')
        if category_name:
            # Filter by category name
            products = products.filter(categories__name=category_name)

        # Search functionality
        search_query = request.GET.get('q')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Sort products
        products = products.order_by(sort_by)

        # Get categories for the sidebar
        categories = Category.objects.all()
        
        # Pagination
        paginator = Paginator(products, 8)  # Show 10 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Check wishlist status for authenticated users
        '''if request.user.is_authenticated:
            wishlist_product_ids = Wishlist.objects.filter(
                user=request.user).values_list('product_id', flat=True)
            for product in page_obj:  # Note: using page_obj instead of products
                product.in_wishlist = product.id in wishlist_product_ids
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        else:
            for product in page_obj:  # Note: using page_obj instead of products
                product.in_wishlist = False'''

        return render(request, 'wishlist/product_list.html', {
            'products': page_obj,
            #'wishlist_count': wishlist_count,
            'categories': categories,
            'sort_by': sort_by,
            'selected_category': category_name,
            'search_query': search_query,
        })

# Create Operation
@permission_required('product.add_product', raise_exception=True)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        try:
            with transaction.atomic():
                if form.is_valid():
                    product = form.save()
                    messages.success(request, 'Product created successfully!')
                    return redirect('product_list')
                else:
                    # Display form errors to user
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    else:
        form = ProductForm()

    return render(request, 'wishlist/product_form.html', {
        'form': form,
        'title': 'Create Product'
    })


# Update Operation
@permission_required('product.change_product', raise_exception=True)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'wishlist/product_form.html', {'form': form})


def detail_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'wishlist/product_detail.html', {'product': product})

# Delete Operation


@permission_required('product.delete_product', raise_exception=True)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'wishlist/product_confirm_delete.html', {'product': product})


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category = Category.objects.create(name=name)
            return JsonResponse({'id': category.id, 'name': category.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)






@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        order_data = {
            "amount": int(product.price * 100),
            "currency": "INR",
            "payment_capture": "1"
        }
        razorpay_order = client.order.create(order_data)
        Order.objects.create(
            user=request.user,
            product=product,
            amount=product.price,
            razorpay_order_id=razorpay_order['id']
        )
        return JsonResponse({
            "order_id": razorpay_order['id'],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "product_name": product.name,
            "amount": order_data['amount'],
            "razorpay_callback_url": settings.RAZORPAY_CALLBACK_URL
        })


'''@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request):
        if "razorpay_signature" in request.POST:
            order_id = request.POST.get('razorpay_order_id')
            payment_id = request.POST.get('razorpay_payment_id')
            signature = request.POST.get('razorpay_signature')

            order = get_object_or_404(Order, razorpay_order_id=order_id)

            if client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }):

                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.is_paid = True
                order.save()
                return JsonResponse({"status": "success"})

            else:
                order.is_paid = False
                order.save()
                return JsonResponse({"status": "failed"})

        else:
            return JsonResponse({"status": "failed!"})'''
            

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request):
        try:
            # Verify the payment
            payment_data = {
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }
            
            if not all(payment_data.values()):
                return JsonResponse({'status': 'failed', 'error': 'Missing payment data'}, status=400)
            
            order = Order.objects.get(razorpay_order_id=payment_data['razorpay_order_id'])
            
            try:
                client.utility.verify_payment_signature(payment_data)
                order.status = 'completed'
                order.is_paid = True
                order.save()
                
                #order.send_confirmation_email()
                # Send email in a try block to prevent payment verification from failing due to email issues
                try:
                    self.send_confirmation_email(order)
                except Exception as email_error:
                    logger.error(f"Email failed but payment succeeded: {email_error}")
                
                return JsonResponse({'status': 'success'})
                
            except razorpay.errors.SignatureVerificationError:
                order.status = 'failed'
                order.save()
                return JsonResponse({'status': 'failed', 'error': 'Invalid signature'}, status=400)
                
        except Order.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Order not found'}, status=404)
        except Exception as e:
            logger.error(f"Payment callback error: {str(e)}")
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

    def send_confirmation_email(self):
        """Send order confirmation email with PDF receipt attached"""
        subject = f"Order Confirmation - #{self.razorpay_order_id}"
        context = {
            'order': self,
            'items': self.items.all(),
            'user': self.user,
            'support_email': settings.SUPPORT_EMAIL,
             'company_name': settings.COMPANY_NAME,
        }
        
        # Render email content
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Generate PDF receipt
        pdf_content = self.generate_receipt_pdf()
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        if pdf_content:
            email.attach(
                filename=f"Receipt-{self.razorpay_payment_id}.pdf",
                content=pdf_content,
                mimetype="application/pdf"
            )
        
        try:
            email.send()
            self.email_sent = True
            self.save(update_fields=['email_sent'])
            logger.info(f"Order confirmation email sent for order {self.id}")
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")
            raise


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, 
                                razorpay_order_id=order_id, 
                                user=request.user)
        
        # Mark order as paid if not already
        if order.status == 'created':
            order.status = 'paid'
            order.save()
        
        # Send confirmation email with receipt
        order.send_confirmation_email()
        
        return render(request, 'payment/success.html', {
            'order': order,
            'order_items': order.items.all()
        })
        

class GenerateOrderReceiptPDF(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        template = get_template('emails/order_receipt_pdf.html')
        context = {
            'order': order,
            'items': [order.product],  # Adjust if you have multiple items
            'date': order.created_at.strftime("%B %d, %Y")
        }
        html = template.render(context)
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Order_Receipt_{order.razorpay_order_id}.pdf"'
            return response
        return HttpResponse('Error generating PDF', status=400)   
        
class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/failed.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, razorpay_order_id=kwargs['order_id'], user=self.request.user)
        context['order'] = order
        context['product'] = order.product
        return context
    
# views.py
from django.utils import timezone
from datetime import datetime
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'payment/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10  # Optional: add pagination
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user).order_by('-created_at')
        
        # Get filter parameters from request
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        # Apply date filters if they exist
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date)
            except ValueError:
                # Handle invalid date format
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date)
            except ValueError:
                # Handle invalid date format
                pass
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the current filter values to context
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context