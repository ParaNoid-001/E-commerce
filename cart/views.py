from .view_imports import *

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Cart Views
@login_required
def cart_summary(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_summary.html', {'cart': cart})

@login_required
def cart_add(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'item_quantity': cart_item.quantity,
            'item_total': cart_item.total_price,
            'cart_total_price': cart.total_price
        })
    return JsonResponse({'success': False}, status=400)

@login_required
def cart_delete(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'cart_total_price': cart.total_price
        })
    return JsonResponse({'success': False}, status=400)

@login_required
def cart_update(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'item_quantity': cart_item.quantity,
            'item_total': cart_item.total_price,
            'cart_total_price': cart.total_price
        })
    return JsonResponse({'success': False}, status=400)

# Checkout Views
@method_decorator(csrf_exempt, name='dispatch')
class CreateCartOrderView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            cart = Cart.objects.filter(user=request.user).last()
            if not cart or not cart.items.exists():
                return JsonResponse({'error': 'Your cart is empty'}, status=400)
            
            total_amount = cart.total_price

            # Create order in your database first
            order = Order.objects.create(
                user=request.user,
                amount=total_amount,
                status='created'  # Now this will work
            )

            # Create order items
            for cart_item in cart.items.all():
                order.items.create(
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Now create Razorpay order
            razorpay_order = client.order.create({
                "amount": int(total_amount * 100),  # Convert to paise
                "currency": "INR",
                "payment_capture": "1"
            })
            
            # Update order with Razorpay ID
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            
            return JsonResponse({
                "order_id": razorpay_order['id'],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount": int(total_amount * 100),
                "currency": "INR",
                "callback_url": settings.RAZORPAY_CALLBACK_URL
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_id = data.get('razorpay_order_id')
            payment_id = data.get('razorpay_payment_id')
            signature = data.get('razorpay_signature')

            order = get_object_or_404(Order, razorpay_order_id=order_id)
            
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            if client.utility.verify_payment_signature(params_dict):
                # Update order status
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.is_paid = True
                order.status = 'paid'
                order.save()
                
                # Delete the cart
                Cart.objects.filter(user=order.user).delete()
                
                # Send confirmation email
                self.send_order_confirmation_email(order)
                
                return JsonResponse({"status": "success"})
            else:
                order.status = 'failed'
                order.save()
                return JsonResponse({"status": "signature verification failed"}, status=400)
                
        except Exception as e:
            logger.error(f"Payment callback error: {str(e)}")
            if 'order' in locals():
                order.status = 'failed'
                order.save()
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    def send_order_confirmation_email(self, order):
        subject = f"Order Confirmation - #{order.razorpay_order_id}"
        
        # Generate the receipt download URL
        receipt_url = f"{settings.SITE_DOMAIN}/order/receipt/{order.id}/"
        # Render HTML template
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all(),
            'user': order.user,
            'receipt_url': receipt_url
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False
        )
 
import logging    
logger = logging.getLogger(__name__)
class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        order = Order.objects.filter(user=request.user, is_paid=True).order_by('-created_at').first()
        
        order.send_confirmation_email()
        
        if order and not order.email_sent:  # Add email_sent field to Order model
            try:
                self.send_order_confirmation_email(order)
                order.email_sent = True
                order.save()
            except Exception as e:
                logger.error(f"Failed to send order email: {str(e)}")
        
        return render(request, 'cart/order_success.html', {
            'order': order,
            'cart_empty': not Cart.objects.filter(user=request.user).exists(),
            'receipt_url': reverse('cart:order-receipt', args=[order.id])
        })
    
    def send_order_confirmation_email(self, order):
        # Same implementation as in PaymentCallbackView
        subject = f"Order Confirmation - #{order.razorpay_order_id}"
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all(),
            'user': order.user
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message
        )
    
    
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def verify_payment(request):
    """
    Verify Razorpay payment (works for all payment modes in test mode)
    """
    if request.method == 'POST':
        try:
            # Get payment details from request
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            # In test mode, we can skip actual verification if needed
            if settings.DEBUG:
                verification = True  # Skip verification in test mode
            else:
                verification = client.utility.verify_payment_signature(params_dict)

            if verification:
                # Get the order from database
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                
                # Update order status
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.is_paid = True
                order.status = 'paid'
                order.save()
                
                # Clear the cart
                Cart.objects.filter(user=order.user).delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'order_id': str(order.id)
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Payment verification failed'
                }, status=400)
                
        except Order.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Order not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return redirect('cart:cart_summary')
        
        context = {
            'cart': cart,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': settings.RAZORPAY_CALLBACK_URL
        }
        return render(request, 'cart/checkout.html', context)
    
    


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