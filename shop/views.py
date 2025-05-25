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



def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items:
        return render(request, 'checkout.html', {'message': 'Your cart is empty.'})
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    order = Order.objects.create(user=user, total_amount=total_amount)
    
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        item.delete()
    
    return render(request, 'checkout.html', {'order': order})

def order_list(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    return render(request, 'order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})

def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
    
    return render(request, 'order_detail.html', {'order': order, 'order_items': OrderItem.objects.filter(order=order)})

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        return render(request, 'product_detail.html', {'product': product})
    
    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, product_id):
    
    product = Product.objects.get(id=product_id)
    product.delete()
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        product = Product.objects.create(name=name, description=description, price=price, image=image)
        return render(request, 'product_detail.html', {'product': product})
    
    return render(request, 'add_product.html')

def home(request):
    return render(request, 'home.html', {'message': 'Welcome to the Online Shop!'})