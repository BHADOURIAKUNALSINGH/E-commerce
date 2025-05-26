from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal
from .models import Product, Category, Order, OrderItem, UserProfile
from .forms import UserRegisterForm, UserProfileForm
from .utils import add_to_cart, get_cart, get_cart_total, remove_from_cart

# Create your views here.

def product_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '')
    page = request.GET.get('page', 1)
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category_id:
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass
    
    if min_price:
        try:
            min_price = Decimal(min_price)
            if min_price >= 0:
                products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = Decimal(max_price)
            if max_price >= 0:
                products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    # Apply sorting
    valid_sort_options = ['price_asc', 'price_desc', 'name_asc', 'name_desc']
    if sort_by in valid_sort_options:
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
    
    # Pagination
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
        
    paginator = Paginator(products, 9)  # Show 9 products per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'paginator': paginator
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})

def cart(request):
    cart_items = get_cart(request)
    cart_total = get_cart_total(request)
    # Get product details for each item in the cart
    cart_items_with_products = {}
    for product_id, item in cart_items.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items_with_products[product_id] = {
            'product': product,
            'quantity': item['quantity']
        }
    return render(request, 'store/cart.html', {'cart_items': cart_items_with_products, 'cart_total': cart_total})

def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        add_to_cart(request, product_id, quantity)
    return redirect('cart')

def remove_from_cart_view(request, product_id):
    remove_from_cart(request, product_id)
    return redirect('cart')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cart_items = get_cart(request)
    if not cart_items:
        return redirect('cart')
    cart_total = get_cart_total(request)
    cart_items_with_products = {}
    for product_id, item in cart_items.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items_with_products[product_id] = {
            'product': product,
            'quantity': item['quantity']
        }
    if request.method == 'POST':
        # Create Order
        order = Order.objects.create(user=request.user, total_price=cart_total)
        for product_id, item in cart_items.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])
            # Optionally, decrease stock
            product.stock -= item['quantity']
            product.save()
        # Clear cart
        request.session['cart'] = {}
        return render(request, 'store/checkout_success.html', {'order': order})
    return render(request, 'store/checkout.html', {'cart_items': cart_items_with_products, 'cart_total': cart_total})

def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'store/profile.html', {'form': form})
