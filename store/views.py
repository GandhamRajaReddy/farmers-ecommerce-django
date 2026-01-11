# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Count, Avg, Sum
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
import json
import uuid
from .models import *
from .forms import *
from .utils import get_cart, get_cart_count
from decimal import Decimal


def seeds(request):
    products = Product.objects.filter(category__name__iexact="Seeds")
    return render(request, "store/seeds.html", {"products": products})

# Home page
def home(request):
    # Get featured categories
    categories = Category.objects.filter(is_active=True)[:8]
    
    # Get featured products
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_available=True
    ).order_by('-created_at')[:8]
    
    # Get new arrivals
    new_products = Product.objects.filter(
        is_available=True
    ).order_by('-created_at')[:6]
    
    # Get products on sale
    sale_products = Product.objects.filter(
        is_on_sale=True,
        is_available=True
    ).order_by('-created_at')[:6]
    
    # Get best selling products
    best_selling = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(
        total_sold__gt=0,
        is_available=True
    ).order_by('-total_sold')[:6]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
        'sale_products': sale_products,
        'best_selling': best_selling,
    }
    return render(request, 'store/home.html', context)
# CATEGORY VIEW (fix for slug-based categories)
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)

    products = Product.objects.filter(
        category=category,
        is_available=True
    ).order_by('-created_at')

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/product_list.html', context)

# Product category views
class CategoryView(ListView):
    model = Product
    template_name = 'store/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        queryset = Product.objects.filter(is_available=True)
        
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        
        if subcategory_slug:
            self.subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
            queryset = queryset.filter(subcategory=self.subcategory)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-rating')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = getattr(self, 'category', None)
        context['subcategory'] = getattr(self, 'subcategory', None)
        context['sort_by'] = self.request.GET.get('sort', 'newest')
        return context

# Product detail view
class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get related products
        related_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        
        # Get product reviews
        reviews = product.reviews.all().order_by('-created_at')[:5]
        
        # Get average rating
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        context.update({
            'related_products': related_products,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_form': ProductReviewForm(),
        })
        return context

# Search view
def search(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(is_available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__icontains=query)
        )
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'relevance')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-rating')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    context = {
        'products': products_page,
        'query': query,
        'categories': Category.objects.filter(is_active=True),
        'total_results': products.count(),
    }
    return render(request, 'store/search.html', context)

# Cart views
def cart_page(request):
    cart = get_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    subtotal = sum((item.get_total_price() for item in cart_items), Decimal('0.00'))

    shipping = Decimal('40.00') if subtotal < Decimal('500.00') else Decimal('0.00')

    tax = subtotal * Decimal('0.05')

    total = subtotal + shipping + tax

    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock} items available in stock'
            })
        
        cart = get_cart(request)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot add more. Total would exceed available stock of {product.stock}'
                })
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Calculate cart totals
        cart_count = cart.get_total_items()
        cart_total = cart.get_total_price()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item_total': float(cart_item.get_total_price()),
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity <= 0:
            cart_item.delete()
            removed = True
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {cart_item.product.stock} items available'
                })
            cart_item.quantity = quantity
            cart_item.save()
            removed = False
        
        # Recalculate cart totals
        cart_items = cart.items.all()
        subtotal = sum((item.get_total_price() for item in cart_items), Decimal('0.00'))

        cart_count = cart.get_total_items()
        
        return JsonResponse({
            'success': True,
            'removed': removed,
            'cart_count': cart_count,
            'subtotal': float(subtotal),
            'item_total': 0 if removed else float(cart_item.get_total_price()),
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        # Recalculate cart totals
        cart_items = cart.items.all()
        subtotal = sum((item.get_total_price() for item in cart_items), Decimal('0.00'))

        cart_count = cart.get_total_items()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_count': cart_count,
            'subtotal': float(subtotal),
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def clear_cart(request):
    try:
        cart = get_cart(request)
        cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0,
            'subtotal': 0.0,
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Checkout views
@login_required
def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} has only {item.product.stock} items in stock')
            return redirect('cart')
    
    # Calculate totals
    subtotal = sum((item.get_total_price() for item in cart_items), Decimal('0.00'))

    shipping = Decimal('40.00') if subtotal < Decimal('500.00') else Decimal('0.00')

    tax = subtotal * Decimal('0.05')

    total = subtotal + shipping + tax

    
    # Get user addresses
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'].address_line_1,
                shipping_city=form.cleaned_data['shipping_address'].city,
                shipping_state=form.cleaned_data['shipping_address'].state,
                shipping_pincode=form.cleaned_data['shipping_address'].pincode,
                shipping_phone=form.cleaned_data['shipping_address'].phone,
                subtotal=subtotal,
                shipping_charge=shipping,
                tax_amount=tax,
                total_amount=total,
                payment_method=form.cleaned_data['payment_method'],
                notes=form.cleaned_data.get('notes', ''),
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.current_price,
                    quantity=cart_item.quantity,
                    total_price=cart_item.get_total_price(),
                )
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Clear cart
            cart.clear()
            
            # Redirect to payment or order confirmation
            if order.payment_method == 'cod':
                return redirect('order_confirmation', order_number=order.order_number)
            else:
                # Handle online payment
                return redirect('payment', order_number=order.order_number)
    else:
        form = CheckoutForm(request.user)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

# User profile views
@login_required
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    addresses = ShippingAddress.objects.filter(user=user)
    wishlist_items = Wishlist.objects.filter(user=user).select_related('product')[:6]
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'orders': orders,
        'addresses': addresses,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/user_profile.html', context)

@login_required
def address_book(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully')
            return redirect('address_book')
    else:
        form = ShippingAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'store/address_book.html', context)

@login_required
def edit_address(request, pk):
    address = get_object_or_404(ShippingAddress, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully')
            return redirect('address_book')
    else:
        form = ShippingAddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'store/edit_address.html', context)

@login_required
def delete_address(request, pk):
    address = get_object_or_404(ShippingAddress, id=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully')
    return redirect('address_book')

# Wishlist views
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
@require_POST
def add_to_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return JsonResponse({
                'success': False,
                'error': 'Product already in wishlist'
            })
        
        Wishlist.objects.create(user=request.user, product=product)
        
        return JsonResponse({
            'success': True,
            'message': 'Added to wishlist'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_POST
def remove_from_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Removed from wishlist'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Review views
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified_purchase = has_purchased
            review.save()
            
            # Update product rating
            product.rating = product.get_average_rating()
            product.save()
            
            messages.success(request, 'Review submitted successfully')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductReviewForm()
    
    context = {
        'product': product,
        'form': form,
        'has_purchased': has_purchased,
    }
    return render(request, 'store/add_review.html', context)

# Utility views
def get_cart_count_view(request):
    cart_count = get_cart_count(request)
    return JsonResponse({'cart_count': cart_count})

def apply_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            try:
                coupon = Coupon.objects.get(code=code)
                
                # Get cart total
                cart = get_cart(request)
                subtotal = cart.get_total_price()
                
                if coupon.is_valid(order_amount=subtotal):
                    discount = coupon.calculate_discount(subtotal)
                    
                    # Store coupon in session
                    request.session['applied_coupon'] = {
                        'code': coupon.code,
                        'discount': float(discount),
                    }
                    
                    messages.success(request, f'Coupon applied! You saved ₹{discount:.2f}')
                else:
                    messages.error(request, 'Coupon is not valid')
            
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code')
    
    return redirect('cart')
# SUBCATEGORY FIXES
def insecticides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Insecticides",
        is_available=True,
    )
    return render(request, "store/pesticides/insecticides.html", {"products": products})

def herbicides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Herbicides",
        is_available=True,
    )
    return render(request, "store/pesticides/herbicides.html", {"products": products})

def fungicides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Fungicides",
        is_available=True,
    )
    return render(request, "store/pesticides/fungicides.html", {"products": products})

def rodenticides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Rodenticides",
        is_available=True,
    )
    return render(request, "store/pesticides/rodenticides.html", {"products": products})

def bactericides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Bactericides",
        is_available=True,
    )
    return render(request, "store/pesticides/bactericides.html", {"products": products})

def nematicides(request):
    products = Product.objects.filter(
        subcategory__name__iexact="Nematicides",
        is_available=True,
    )
    return render(request, "store/pesticides/nematicides.html", {"products": products})

def quick_view(request, pk):
    product = get_object_or_404(Product, id=pk, is_available=True)
    html = render(
        request,
        "store/components/quick_view.html",
        {"product": product},
    ).content.decode("utf-8")

    return JsonResponse({"html": html})

def tools_view(request):
    products = Product.objects.filter(
        category__slug="tools",
        is_available=True
    )
    return render(request, "store/tools.html", {"products": products})
def machines_view(request):
    products = Product.objects.filter(
        category__slug="machines",
        is_available=True
    )
    return render(request, "store/machines.html", {"products": products})

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)

    # Create a temporary single-item cart
    cart = get_cart(request)
    cart.items.all().delete()

    CartItem.objects.create(cart=cart, product=product, quantity=1)

    return redirect("checkout")
@login_required
def add_address(request):
    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect("address_book")
    else:
        form = ShippingAddressForm()

    return render(request, "store/add_address.html", {"form": form})
def cart_view(request):
    return cart_page(request)

