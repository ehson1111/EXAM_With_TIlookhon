from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, Cart, Order, OrderItem, User
from django.shortcuts import get_object_or_404


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return HttpResponseRedirect(reverse('product_list'))
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return HttpResponseRedirect(reverse('home'))

def cart_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    user = get_object_or_404(User, id=user_id)
    cart_items = Cart.objects.filter(user=user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart_view.html', {'cart_items': cart_items, 'total': total})


def register_user(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        user = User.objects.create(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        return HttpResponseRedirect(reverse('login'))
    
    return render(request, 'register.html')






def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_detail.html', {'product': product})






def remove_from_cart(request, product_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    user = get_object_or_404(User, id=user_id)
    cart_item = get_object_or_404(Cart, user=user, product__id=product_id)
    cart_item.delete()

    return HttpResponseRedirect(reverse('cart_view'))


def add_to_cart(request, product_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    user = get_object_or_404(User, id=user_id)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return HttpResponseRedirect(reverse('cart_view'))


def checkout(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login')) 
    user = get_object_or_404(User, id=user_id)
    cart_items = Cart.objects.filter(user=user)

    if request.method == 'POST':
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=user, total_amount=total_amount)
        
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            item.delete()
        
        return HttpResponseRedirect(reverse('order_list'))

    return render(request, 'checkout.html', {'cart_items': cart_items})

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
    return render(request, 'home.html', {'message': 'Welcome to  Online Shop!'})