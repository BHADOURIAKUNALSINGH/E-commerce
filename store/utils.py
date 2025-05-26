from decimal import Decimal

def get_cart(request):
    """Get the cart from the session or create a new one."""
    cart = request.session.get('cart', {})
    return cart

def add_to_cart(request, product_id, quantity=1):
    """Add a product to the cart."""
    cart = get_cart(request)
    product_id = str(product_id)  # Convert to string for session storage

    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {'quantity': quantity}

    request.session['cart'] = cart

def remove_from_cart(request, product_id):
    """Remove a product from the cart."""
    cart = get_cart(request)
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart

def get_cart_total(request):
    """Calculate the total price of items in the cart."""
    cart = get_cart(request)
    total = Decimal('0.00')
    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * item['quantity']
    return total 