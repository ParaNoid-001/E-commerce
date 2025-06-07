from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from wishlist.models import Wishlist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()


class WishlistView(LoginRequiredMixin, View):
    template_name = 'wishlist/wishlist.html'
    
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        
        # Pagination
        paginator = Paginator(wishlist_items, 10)  # Show 10 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, self.template_name, {
            'wishlist_items': page_obj,
            'wishlist_count': wishlist_items.count()
        })

class ToggleWishlist(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, 
            product=product
        )

        if not created:
            wishlist_item.delete()
            action = 'removed'
        else:
            action = 'added'

        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'wishlist_count': wishlist_count,
            'product_id': product.id
        })


class WishlistCountView(LoginRequiredMixin, View):
    def get(self, request):
        count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})