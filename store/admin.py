# store/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import *

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_available', 'is_featured', 'rating']
    list_filter = ['category', 'is_available', 'is_featured', 'is_on_sale', 'product_type']
    search_fields = ['name', 'description', 'sku']
    readonly_fields = ['sku', 'rating', 'total_reviews']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'product_type', 'category', 'subcategory')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'specifications')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'min_order_quantity', 'max_order_quantity', 'sku', 'barcode')
        }),
        ('Details', {
            'fields': ('brand', 'weight', 'unit', 'expiry_date', 'manufacturing_date')
        }),
        ('Instructions', {
            'fields': ('usage_instructions', 'safety_instructions')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured', 'is_on_sale', 'rating', 'total_reviews')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'total_price']
    can_delete = False
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'user__username', 'shipping_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_pincode', 'shipping_phone')
        }),
        ('Billing Details', {
            'fields': ('billing_address', 'billing_city', 'billing_state', 'billing_pincode')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'payment_id')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'shipping_charge', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional', {
            'fields': ('notes', 'delivered_at')
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'added_at']

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'get_total_items', 'get_total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"₹{obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ProductReview)
admin.site.register(Wishlist)
admin.site.register(ShippingAddress)
admin.site.register(Coupon)
admin.site.register(ProductImage)