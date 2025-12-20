# store/utils.py
import uuid
from .models import Cart,Wishlist

def get_cart(request):
    """Get or create cart for user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Create a unique session ID if not exists
        if not request.session.get('guest_session_id'):
            request.session['guest_session_id'] = str(uuid.uuid4())
        
        session_id = request.session['guest_session_id']
        cart, created = Cart.objects.get_or_create(
            session_id=session_id,
            user=None
        )
    
    return cart

def get_cart_count(request):
    """Get cart item count"""
    try:
        cart = get_cart(request)
        return cart.get_total_items()
    except:
        return 0

def get_wishlist_count(request):
    """Get wishlist count for authenticated users"""
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).count()
    return 0