from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .cart import Cart
from .models import Product, Category, Review, Order, OrderItem, UserActivity, WishlistItem, Profile
from dealsandoffers.models import Deal
from .forms import ReviewForm, ContactForm

from django.db.models import Avg, Q
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@require_POST
def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product_type = data.get('product_type')  # 'product' or 'deal'

    if product_type == 'deal':
        try:
            deal = Deal.objects.get(id=product_id)
            product = deal.products.first()  # Get first product in the deal
            if not product:
                return JsonResponse({'success': False, 'message': 'No product in the deal.'})
        except Deal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Deal not found.'})
    elif product_type == 'product':
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid product type.'})

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'type': product_type,
        }

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'message': 'Added to cart'})


@require_POST
def add_to_wishlist(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product_type = data.get('product_type')

    try:
        if product_type == 'deal':
            deal = Deal.objects.get(id=product_id)
            product = deal.products.first()
            if not product:
                return JsonResponse({'success': False, 'message': 'No product in the deal.'})
        else:
            product = Product.objects.get(id=product_id)
    except (Deal.DoesNotExist, Product.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Item not found.'})

    wishlist = request.session.get('wishlist', {})

    wishlist[str(product_id)] = {
        'name': product.name,
        'price': str(product.price),
        'type': product_type,
    }

    request.session['wishlist'] = wishlist
    return JsonResponse({'success': True, 'message': 'Added to wishlist'})


def thank_you(request):
    cart = request.session.get('cart', {})
    total = 0
    items = []

    for item_id, item in cart.items():
        try:
            if item['type'] == 'deal':
                deal = Deal.objects.get(id=item_id)
                base_price = 1000  # or use actual pricing logic
                price = base_price * (1 - deal.discount_percent / 100)
                subtotal = price * item['quantity']
                items.append({
                    'title': deal.title,
                    'quantity': item['quantity'],
                    'discount': deal.discount_percent,
                    'subtotal': int(subtotal)
                })
                total += subtotal
            else:
                product = Product.objects.get(id=item_id)
                subtotal = float(product.price) * item['quantity']
                items.append({
                    'title': product.name,
                    'quantity': item['quantity'],
                    'discount': 0,
                    'subtotal': int(subtotal)
                })
                total += subtotal
        except (Deal.DoesNotExist, Product.DoesNotExist):
            continue

    # Clear cart after rendering
    request.session['cart'] = {}

    return render(request, 'thank_you.html', {
        'total': int(total),
        'items': items,
        'order': {'id': 'SP-2025-001'},
    })


# ----------------------------
# AUTHENTICATION & USER VIEWS
# ----------------------------

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid username or password'})

    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, "store/signup.html")

        # If not exists, create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, "store/signup.html")
@login_required(login_url='login')
def update_profile(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        profile_image = request.FILES.get('profile_image')

        user = request.user
        user.username = username
        user.email = email
        user.save()

        if profile_image:
            profile.image = profile_image
            profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'store/update_profile.html', {'profile': profile})


@login_required
def profile_view(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    return render(request, 'store/profile.html', {'profile': profile})

# ----------------------------
# PRODUCT & STORE VIEWS
# ----------------------------

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': None
    })

def category_products(request, category_name):
    products = Product.objects.filter(category__name=category_name)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_name
    })

def search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)) if query else []
    return render(request, 'store/search_results.html', {
        'query': query,
        'results': results,
        'categories': Category.objects.all()
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    # Record the product view activity
    if request.user.is_authenticated:
        UserActivity.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'activity_type': 'view'}
        )
        recommended_products = get_recommended_products(request.user, product)
    else:
        recommended_products = []

    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'recommended_products': recommended_products
    })

def get_recommended_products(user, current_product):
    try:
        user_views = UserActivity.objects.filter(user=user, activity_type='view')
        viewed_products = [activity.product for activity in user_views]
        
        # Get products viewed by other users who viewed similar products
        recommended_activities = UserActivity.objects.filter(
            activity_type='view',
            product__in=viewed_products
        ).exclude(product=current_product).exclude(user=user).distinct()

        return [activity.product for activity in recommended_activities[:6]]
    except:
        return []

# ----------------------------
# CART VIEWS
# ----------------------------

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    messages.success(request, "Product added to cart successfully!")
    return redirect('home')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.success(request, "Product removed from cart!")
    return redirect('view_cart')

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product_id, quantity)
    messages.success(request, "Cart updated successfully!")
    return redirect('view_cart')

def clear_cart(request):
    request.session.pop('cart', None)
    messages.success(request, "Cart cleared successfully!")
    return redirect('home')

@login_required(login_url='login')
def view_cart(request):
    cart = Cart(request)
    cart_data = cart.get_cart_items()
    items = []
    total = 0

    for product_id, quantity in cart_data.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            subtotal = quantity * product.price
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue

    return render(request, 'store/cart.html', {
        'items': items, 
        'total': total,
        'cart_item_count': cart.get_total_quantity()
    })

# ----------------------------
# CHECKOUT & ORDER VIEWS
# ----------------------------

@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        # Create order
        cart_data = cart.get_cart_items()
        total = 0
        
        # Calculate total
        for product_id, quantity in cart_data.items():
            try:
                product = Product.objects.get(id=product_id)
                total += quantity * product.price
            except Product.DoesNotExist:
                continue
        
        # Create order
        order = Order.objects.create(
            user=request.user, 
            total_price=total,
            approval_status='Pending'
        )
        
        # Create order items
        for product_id, quantity in cart_data.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
            except Product.DoesNotExist:
                continue
        
        cart.clear()
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('thank_you')

    # GET request - show checkout page
    cart_data = cart.get_cart_items()
    items = []
    total = 0
    
    for product_id, quantity in cart_data.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            subtotal = quantity * product.price
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue
    
    return render(request, 'store/checkout.html', {'items': items, 'total': total})

@login_required(login_url='login')
def thank_you(request):
    return render(request, 'store/thank_you.html')

@login_required(login_url='login')
def order_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})

@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

@login_required(login_url='login')
def order_delete(request, order_id):
    """
    View to handle order deletion/cancellation
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be deleted (e.g., only pending orders)
    if hasattr(order, 'approval_status') and order.approval_status in ['Pending', 'Processing']:
        order_number = order.id
        order.delete()
        messages.success(request, f'Order #{order_number} has been cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled as it has already been processed.')
    
    return redirect('order_view')

@login_required(login_url='login')
def order_cancel(request, order_id):
    """
    View to handle order cancellation (marking as cancelled instead of deleting)
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be cancelled
    if hasattr(order, 'approval_status') and order.approval_status in ['Pending', 'Processing']:
        order.approval_status = 'Cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled as it has already been processed.')
    
    return redirect('order_view')

# ----------------------------
# WISHLIST VIEWS
# ----------------------------

@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"{product.title} added to wishlist!")
    else:
        messages.info(request, f"{product.title} is already in your wishlist!")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    try:
        wishlist_item = WishlistItem.objects.get(user=request.user, product_id=product_id)
        product_title = wishlist_item.product.title
        wishlist_item.delete()
        messages.success(request, f"{product_title} removed from wishlist!")
    except WishlistItem.DoesNotExist:
        messages.error(request, "Item not found in wishlist!")
    
    return redirect('wishlist')

# ----------------------------
# DASHBOARD VIEWS
# ----------------------------

@login_required(login_url='login')
def user_dashboard(request):
    # Get user statistics
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, approval_status='Pending').count()
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'store/user_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_dashboard(request):
    users = User.objects.all()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(approval_status='Pending').count()
    
    context = {
        'users': users,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'store/admin_dashboard.html', context)

# ----------------------------
# OTHER VIEWS
# ----------------------------

def contact_view(request):
    if request.method == 'POST':
        try:
            form = ContactForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your message has been sent!')
                return redirect('contact')
        except:
            messages.error(request, 'There was an error sending your message. Please try again.')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})

def about_view(request):
    return render(request, 'store/about.html')

def faq_view(request):
    faqs = [
        {"question": "What is ShopSphere?", "answer": "ShopSphere is an all-in-one e-commerce platform offering everything from fashion to gadgets."},
        {"question": "How can I track my order?", "answer": "You can track your order from the 'My Orders' section in your account dashboard."},
        {"question": "What payment methods are supported?", "answer": "We support UPI, credit/debit cards, net banking, Razorpay, Stripe, and more."},
        {"question": "Can I cancel or return my order?", "answer": "Yes. You can request a cancellation or return within 7 days of delivery."},
        {"question": "Is my payment information secure?", "answer": "Absolutely. We use SSL encryption and industry-standard payment gateways."},
        {"question": "How do I contact customer support?", "answer": "Click on 'Contact Us' in the footer or email us at support@shopsphere.com."},
    ]
    return render(request, 'store/faq.html', {'faqs': faqs})

@login_required
def submit_review(request):
    if request.method == 'POST':
        try:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                messages.success(request, 'Review submitted successfully!')
                return redirect('review_success')
        except:
            messages.error(request, 'There was an error submitting your review. Please try again.')
    else:
        form = ReviewForm()
    return render(request, 'store/submit_review.html', {'form': form})

def review_success(request):
    return render(request, 'store/review_success.html')

def track_order_view(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number)
        status_updates = getattr(order, 'status_updates', None)
        if status_updates:
            status_updates = status_updates.all()
        else:
            status_updates = []

        context = {
            'order': order,
            'status_updates': status_updates,
        }
        return render(request, 'store/track_order.html', context)
    except:
        messages.error(request, 'Order not found!')
        return redirect('order_number')

def order_number_view(request):
    error = None
    if 'order_number' in request.GET:
        order_number = request.GET.get('order_number').strip()
        try:
            order = Order.objects.get(order_number=order_number)
            return redirect('track_order', order_number=order_number)
        except Order.DoesNotExist:
            error = "Order not found. Please check your order number."

    return render(request, 'store/order_number.html', {'error': error})

# ----------------------------
# ERROR HANDLERS
# ----------------------------

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'store/404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, 'store/500.html', status=500)




