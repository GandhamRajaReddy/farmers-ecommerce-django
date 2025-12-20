# store/context_processors.py
from .utils import get_cart_count, get_wishlist_count
from .models import Category
from store.models import Category


def ecommerce_context(request):
    """Add e-commerce data to all templates"""
    context = {
        'cart_count': get_cart_count(request),
        'categories': Category.objects.filter(is_active=True),
    }
    
    if request.user.is_authenticated:
        context['wishlist_count'] = get_wishlist_count(request)
    
    return context
from .utils import get_cart_count

def cart(request):
    """
    Adds cart count to all templates.
    """
    try:
        cart_count = get_cart_count(request)
    except:
        cart_count = 0

    return {
        "cart_count": cart_count
    }


def global_categories(request):
    return {
        "categories": Category.objects.all()
    }
