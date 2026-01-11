# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    

    # -------------------------
    # HOME
    # -------------------------
    path("", views.home, name="home"),

    # -------------------------
    # CATEGORY SHORTCUT PAGES
    # -------------------------
    path("seeds/", views.seeds, name="seeds"),
    path("tools/", views.tools_view, name="tools"),
    path("machines/", views.machines_view, name="machines"),

    # -------------------------
    # CATEGORY + SUBCATEGORY
    # -------------------------
    path("category/<slug:category_slug>/", 
         views.CategoryView.as_view(), 
         name="category"),

    path("category/<slug:category_slug>/<slug:subcategory_slug>/",
         views.CategoryView.as_view(),
         name="subcategory"),

    # -------------------------
    # PRODUCT
    # -------------------------
    path("product/<slug:slug>/",
         views.ProductDetailView.as_view(),
         name="product_detail"),

    # Quick View popup
    path("product/<int:pk>/quick-view/",
         views.quick_view,
         name="quick_view"),

    # -------------------------
    # SEARCH
    # -------------------------
    path("search/", views.search, name="search"),

    # -------------------------
    # CART
    # -------------------------
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/count/", views.get_cart_count_view, name="cart_count"),

    # -------------------------
    # BUY NOW (NEW)
    # -------------------------
    path("buy/<int:product_id>/", views.buy_now, name="buy_now"),

    # -------------------------
    # CHECKOUT + ORDERS
    # -------------------------
    path("checkout/", views.checkout, name="checkout"),
    path("order/confirmation/<str:order_number>/", 
         views.order_confirmation, 
         name="order_confirmation"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<str:order_number>/", 
         views.order_detail, 
         name="order_detail"),

    # -------------------------
    # USER PROFILE + ADDRESS
    # -------------------------
    path("profile/", views.user_profile, name="user_profile"),

    path("addresses/", views.address_book, name="address_book"),
    path("addresses/add/", views.add_address, name="add_address"),
    path("addresses/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),

    # -------------------------
    # WISHLIST (Better API)
    # -------------------------
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/", views.remove_from_wishlist, name="remove_from_wishlist"),

    # -------------------------
    # REVIEWS
    # -------------------------
    path("product/<int:product_id>/review/",
         views.add_review,
         name="add_review"),

    # -------------------------
    # COUPONS
    # -------------------------
    path("coupon/apply/", views.apply_coupon, name="apply_coupon"),
]
