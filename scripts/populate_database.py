# scripts/populate_database.py
import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmer_ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def create_superuser():
    """Create superuser if not exists"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@agrimart.com',
            password='admin123'
        )
        print("Superuser created: admin / admin123")

def create_categories():
    """Create main categories"""
    categories_data = [
        {
            'name': 'Seeds',
            'icon': 'fas fa-seedling',
            'description': 'High quality seeds for various crops'
        },
        {
            'name': 'Pesticides',
            'icon': 'fas fa-spray-can',
            'description': 'Protect your crops from pests and diseases'
        },
        {
            'name': 'Tools',
            'icon': 'fas fa-tools',
            'description': 'Essential farming tools and equipment'
        },
        {
            'name': 'Machines',
            'icon': 'fas fa-tractor',
            'description': 'Modern farming machinery'
        },
        {
            'name': 'Fertilizers',
            'icon': 'fas fa-flask',
            'description': 'Organic and chemical fertilizers'
        },
        {
            'name': 'Irrigation',
            'icon': 'fas fa-tint',
            'description': 'Irrigation equipment and systems'
        },
    ]
    
    for data in categories_data:
        Category.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
    print("Categories created")

def create_pesticide_subcategories():
    """Create pesticide subcategories"""
    pesticides_category = Category.objects.get(name='Pesticides')
    
    subcategories = [
        'Insecticides',
        'Herbicides',
        'Fungicides',
        'Rodenticides',
        'Bactericides',
        'Nematicides',
    ]
    
    for name in subcategories:
        SubCategory.objects.get_or_create(
            name=name,
            category=pesticides_category,
            defaults={'description': f'{name} for crop protection'}
        )
    print("Pesticide subcategories created")

def create_sample_products():
    """Create sample products for all categories"""
    # Get categories
    seeds_category = Category.objects.get(name='Seeds')
    pesticides_category = Category.objects.get(name='Pesticides')
    tools_category = Category.objects.get(name='Tools')
    machines_category = Category.objects.get(name='Machines')
    
    # Get pesticide subcategories
    insecticides = SubCategory.objects.get(name='Insecticides')
    herbicides = SubCategory.objects.get(name='Herbicides')
    fungicides = SubCategory.objects.get(name='Fungicides')
    
    products_data = [
        # Seeds
        {
            'name': 'Hybrid Maize Seeds - Pioneer',
            'category': seeds_category,
            'product_type': 'seed',
            'price': 450,
            'discount_price': 420,
            'stock': 100,
            'description': 'High yield hybrid maize seeds, suitable for all seasons',
            'short_description': 'Premium maize seeds with high germination rate',
            'brand': 'Pioneer',
            'weight': '5kg',
            'unit': 'packet',
            'is_featured': True,
        },
        {
            'name': 'Basmati Rice Seeds',
            'category': seeds_category,
            'product_type': 'seed',
            'price': 380,
            'stock': 80,
            'description': 'Premium basmati rice seeds with aromatic grains',
            'short_description': 'Aromatic basmati rice seeds',
            'brand': 'Nirmaan',
            'weight': '4kg',
            'unit': 'packet',
        },
        {
            'name': 'Hybrid Tomato Seeds',
            'category': seeds_category,
            'product_type': 'seed',
            'price': 120,
            'discount_price': 99,
            'stock': 200,
            'description': 'Hybrid tomato seeds with disease resistance',
            'short_description': 'High yield tomato seeds',
            'brand': 'Namdhari',
            'weight': '50g',
            'unit': 'packet',
            'is_on_sale': True,
        },
        
        # Pesticides - Insecticides
        {
            'name': 'Crop Shield Insecticide',
            'category': pesticides_category,
            'subcategory': insecticides,
            'product_type': 'pesticide',
            'price': 799,
            'stock': 50,
            'description': 'Effective insecticide for all crop types. Provides long-lasting protection against harmful pests.',
            'short_description': 'Broad spectrum insecticide',
            'brand': 'Bayer',
            'weight': '1L',
            'unit': 'bottle',
            'is_featured': True,
        },
        {
            'name': 'Imidacloprid 17.8% SL',
            'category': pesticides_category,
            'subcategory': insecticides,
            'product_type': 'pesticide',
            'price': 650,
            'stock': 75,
            'description': 'Systemic insecticide for sucking pests',
            'short_description': 'Effective against aphids and leafhoppers',
            'brand': 'Syngenta',
            'weight': '500ml',
            'unit': 'bottle',
        },
        
        # Pesticides - Herbicides
        {
            'name': 'Glyphosate 41% SL',
            'category': pesticides_category,
            'subcategory': herbicides,
            'product_type': 'pesticide',
            'price': 850,
            'discount_price': 799,
            'stock': 40,
            'description': 'Non-selective herbicide for weed control',
            'short_description': 'Effective weed killer',
            'brand': 'Monsanto',
            'weight': '1L',
            'unit': 'bottle',
            'is_on_sale': True,
        },
        
        # Tools
        {
            'name': 'Steel Garden Hoe',
            'category': tools_category,
            'product_type': 'tool',
            'price': 250,
            'stock': 30,
            'description': 'Durable steel hoe for farming and gardening',
            'short_description': 'Heavy duty garden hoe',
            'brand': 'Kisan',
            'weight': '1.5kg',
            'unit': 'piece',
        },
        {
            'name': 'Professional Pruning Shears',
            'category': tools_category,
            'product_type': 'tool',
            'price': 450,
            'stock': 25,
            'description': 'Professional pruning shears for garden and farm',
            'short_description': 'Sharp pruning shears',
            'brand': 'Gardena',
            'weight': '300g',
            'unit': 'piece',
        },
        
        # Machines
        {
            'name': 'Electric Sprayer 20L',
            'category': machines_category,
            'product_type': 'machine',
            'price': 4500,
            'discount_price': 3999,
            'stock': 10,
            'description': 'Electric power sprayer for pesticide application',
            'short_description': 'Electric sprayer with 20L capacity',
            'brand': 'Agro',
            'weight': '8kg',
            'unit': 'piece',
            'is_featured': True,
        },
        {
            'name': 'Mini Tractor 25HP',
            'category': machines_category,
            'product_type': 'machine',
            'price': 285000,
            'stock': 3,
            'description': 'Compact tractor suitable for small farms',
            'short_description': '25HP mini tractor',
            'brand': 'Mahindra',
            'weight': '1200kg',
            'unit': 'piece',
        },
    ]
    
    for data in products_data:
        # Check if product exists
        if not Product.objects.filter(name=data['name']).exists():
            product = Product.objects.create(**data)
            
            # Add specifications
            if data['product_type'] == 'seed':
                product.specifications = {
                    'Germination Rate': '≥ 85%',
                    'Purity': '≥ 98%',
                    'Moisture Content': '≤ 12%',
                    'Suitable Season': 'Kharif/Rabi',
                    'Packaging': 'Vacuum sealed'
                }
            elif data['product_type'] == 'pesticide':
                product.specifications = {
                    'Active Ingredient': 'Imidacloprid 17.8%',
                    'Formulation': 'Soluble Liquid',
                    'Dosage': '2.5 ml per liter',
                    'Waiting Period': '7 days',
                    'Safety Class': 'II'
                }
            elif data['product_type'] == 'tool':
                product.specifications = {
                    'Material': 'Carbon Steel',
                    'Handle': 'Wooden/Plastic',
                    'Warranty': '1 year',
                    'Usage': 'Agriculture/Gardening'
                }
            
            product.save()
    
    print("Sample products created")

def create_sample_users():
    """Create sample users"""
    users_data = [
        {'username': 'farmer1', 'email': 'farmer1@example.com', 'password': 'password123'},
        {'username': 'farmer2', 'email': 'farmer2@example.com', 'password': 'password123'},
        {'username': 'farmer3', 'email': 'farmer3@example.com', 'password': 'password123'},
    ]
    
    for data in users_data:
        if not User.objects.filter(username=data['username']).exists():
            User.objects.create_user(**data)
    
    print("Sample users created")

def create_sample_orders():
    """Create sample orders for demonstration"""
    users = User.objects.filter(is_superuser=False)[:2]
    products = Product.objects.filter(stock__gt=0)[:5]
    
    if not users or not products:
        print("No users or products available for orders")
        return
    
    statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    
    for i, user in enumerate(users):
        for j in range(2):  # Create 2 orders per user
            order = Order.objects.create(
                user=user,
                shipping_address=f"Farm House {i+1}, Village Road",
                shipping_city="Bengaluru",
                shipping_state="Karnataka",
                shipping_pincode="560001",
                shipping_phone=f"98765432{10+i}",
                subtotal=1000 + (j * 500),
                shipping_charge=40,
                tax_amount=52,
                total_amount=1092 + (j * 500),
                payment_method='cod',
                payment_status='paid' if j == 0 else 'pending',
                status=statuses[j] if j < len(statuses) else 'pending',
            )
            
            # Add order items
            for k, product in enumerate(products[:3]):
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.current_price,
                    quantity=k + 1,
                    total_price=product.current_price * (k + 1)
                )
    
    print("Sample orders created")

def main():
    """Main function to populate database"""
    print("Starting database population...")
    
    create_superuser()
    create_categories()
    create_pesticide_subcategories()
    create_sample_products()
    create_sample_users()
    create_sample_orders()
    
    print("\nDatabase populated successfully!")
    print("\nLogin credentials:")
    print("Superuser: admin / admin123")
    print("Sample users: farmer1 / password123, farmer2 / password123")

if __name__ == '__main__':
    main()