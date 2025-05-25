from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, Cart, Order, OrderItem



def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_detail.html', {'product': product})



def cart_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart_view.html', {'cart_items': cart_items, 'total_amount': total_amount})

def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return render(request, 'cart_view.html', {'cart_items': Cart.objects.filter(user=user)})

def remove_from_cart(request, product_id):
    user = request.user
    cart_item = Cart.objects.get(user=user, product_id=product_id)
    cart_item.delete()
    
    return render(request, 'cart_view.html', {'cart_items': Cart.objects.filter(user=user)})


