from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] = quantity
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_cart_items(self):
        return self.cart

    def get_total_quantity(self):
        return sum(self.cart.values())

    def get_total_price(self):
        total = 0
        for product_id, quantity in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total += product.price * quantity
            except Product.DoesNotExist:
                continue
        return total
