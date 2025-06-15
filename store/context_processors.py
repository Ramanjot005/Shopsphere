from .cart import Cart

def cart_item_count(request):
    cart = Cart(request)
    total_items = sum(cart.cart.values()) if cart.cart else 0
    return {'cart_item_count': total_items}
