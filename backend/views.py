from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.decorators import login_required
from .models import Location, Product, Cart,Contact, CartItem,Category,Order,OrderItem
from django.http import Http404,JsonResponse
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from .models import CustomUser,Product,Subscription, Location, Cart, CartItem, Category, Milk, Sweetener, Flavour
from django.contrib.auth.models import User
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
from django.utils import timezone
from django.http import HttpResponse,HttpResponseRedirect
from django.db import IntegrityError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal

from django.db.models import F




def register_view(request):
    if request.method == 'POST':
        # Get the form data from the request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'create_account/index.html', {'error_message': 'Email already exists'})
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'create_account/index.html', {'error_message': 'Username already exists'})
        # Create the user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully!')
        login(request, user)
        return redirect('location_selection')  # Redirect to desired URL after successful registration
    else:
        # If it's a GET request, simply render the registration form
        return render(request, 'create_account/index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next')  # Retrieve next URL
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if next_url:  # Check if next URL exists
                return redirect(next_url)  # Redirect to next URL after successful login
            else:
                messages.success(request, 'You have successfully logged in!')
                return redirect('location_selection')
        else:
            error_message = "Invalid email or password. Please try again."
            messages.error(request, error_message)
            return render(request, 'login/index.html', {'next': next_url})  # Pass next URL to template
    else:
        return render(request, 'login/index.html', {'next': request.GET.get('next', '')})  # Pass next URL to template

def logout_view(request):
    logout(request)
    return redirect('login')

def location_selection(request):
    # Check if the user is coming from the cart
    from_cart = request.GET.get('from')

    # Fetch locations data
    locations = Location.objects.all()
    query = request.GET.get('query')

    if query:
        # Filter locations based on query
        locations = locations.filter(Q(cafe_name__icontains=query) | Q(address__icontains=query))

    if request.method == 'POST':
        # If it's a POST request, process the form submission
        location_id = request.POST.get('location')
        request.session['location_id'] = location_id

        # Check if the user is coming from the cart
        from_cart = request.POST.get('from_cart')
        if from_cart:
            location_id = request.session.get('location_id')
            if location_id:
                # Update the location for the cart
                cart = Cart.objects.get_or_create(user=request.user)[0]
                cart.location_id = location_id
                cart.save()

            # Redirect to the cart page
            return redirect('cart')
        else:
            # Redirect to drink selection
            return redirect('drink_selection')

    # Render the location selection template
    return render(request, 'location_page/location_selection.html', {'from_cart': from_cart, 'locations': locations})


def drink_selection(request):

    try:
        location = Location.objects.prefetch_related('drinks')
        # Retrieve distinct categories with drinks available at the specified location
        categories_with_drinks = Category.objects.prefetch_related('drinks').distinct()
        return render(request, 'menu/index.html', {'location': location, 'categories_with_drinks': categories_with_drinks})
    except Location.DoesNotExist:
        return redirect('location_selection')

def select_quantity(request, product_id):
    try:
        product = Product.objects.select_related('category').get(pk=product_id)
        location_id = request.session.get('location_id')
        if location_id:
            location = Location.objects.get(pk=location_id)
        else:
            return redirect('location_selection')
        
        # Define cup sizes
        cup_sizes = [
            {"name": "Sano(S)", "volume": "12"},
            {"name": "Thikkako(M)", "volume": "16"},
            {"name": "Thulo(L)", "volume": "24"}
        ]
        
        # Filter related products based on specific attributes of the selected product
        related_products = Product.objects.filter(
              category=product.category
        ).exclude(pk=product_id).distinct()[:5]  # Assuming you want to display 3 related products
        
        return render(request, 'add_to_cart/index.html', {'product': product, 'location': location, 'cup_sizes': cup_sizes, 'related_products': related_products})
    except Product.DoesNotExist:
        return redirect('drink_selection')
def add_more_to_cart(request, cart_item_id):
    if request.method == 'POST':
        try:
            # Retrieve cart item
            cart_item = get_object_or_404(CartItem, pk=cart_item_id)

            # Get form data
            quantity = int(request.POST.get('quantity', 1))

            # Check if the requested quantity exceeds the limit
            if cart_item.quantity + quantity <= 24:
                total_quantity = cart_item.quantity + quantity
                additional_drinks = 0
                if total_quantity == 5:
                    messages.success(request, 'You have earned a free drink!')
                    additional_drinks = 1
                elif total_quantity == 10:
                    messages.success(request, 'You have earned 2 free drink!')
                    additional_drinks = 2
                elif total_quantity == 15:
                    messages.success(request, 'You have earned 3 free drink!')
                    additional_drinks = 3
                elif total_quantity == 20:
                    messages.success(request, 'You have earned 4 free drink!')
                    additional_drinks = 4

                # Increase the quantity of the cart item by the main quantity plus additional drinks
                cart_item.quantity += quantity + additional_drinks
                cart_item.save()

                return redirect('cart')
            else:
                messages.error(request, 'You can only order up to 24 drinks.')
                return redirect('cart')

        except CartItem.DoesNotExist:
            messages.error(request, 'Cart item does not exist.')
            return redirect('cart')  # Redirect to the cart page if cart item does not exist

    else:
        return redirect('cart')

def add_new_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            # Retrieve product and location
            product = Product.objects.get(pk=product_id)
            location_id = request.session.get('location_id')
            if not location_id:
                return redirect('location_selection')
            location = get_object_or_404(Location, pk=location_id)

            # Get form data
            quantity = int(request.POST.get('quantity', 1))
            milk = request.POST.get('milks')
            flavour = request.POST.get('flavour')
            sweetener = request.POST.get('sweetener')
            cup_size = request.POST.get('cup_size')

            # Create or get the user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.location = location
            cart.save()

            # Calculate extra drinks for the initial quantity
            extra_drinks = quantity // 5

            # Create cart item
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity + extra_drinks,
                milk=milk,
                flavour=flavour,
                sweetener=sweetener,
                cup_size=cup_size
            )

            return redirect('cart')  # Redirect to the cart page after adding to cart

        except Product.DoesNotExist:
            messages.error(request, 'Product does not exist.')
            return redirect('drink_selection')  # Redirect to the drink selection page if product does not exist

    else:
        return redirect('drink_selection')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        cart = Cart.objects.get_or_create(user=request.user)[0]
        # Retrieve the last cart item associated with the product
        cart_item = cart.cartitem_set.filter(product=product).order_by('-id').first()
        if cart_item:
            cart_item.delete()  # Remove the last cart item associated with the product
            # Check if the cart is empty after removing the item
            if cart.cartitem_set.count() == 0:
                cart.delete()  # Delete the cart if it is empty
        return redirect('cart')

def cart(request):
    cart = Cart.objects.select_related('location').get_or_create(user=request.user)[0]
    cart_items = cart.cartitem_set.all().select_related('product')
    
    for item in cart_items:
        # Determine the cup size multiplier based on the cup size
        
        if item.cup_size == "Thulo(L)":
            cup_multiplier = 3
          
        elif item.cup_size == "Thikkako(M)":
            cup_multiplier = 2
        elif item.cup_size == "Sano(S)":
            cup_multiplier = 1
        else:
            print("Cup size not recognized")
            cup_multiplier = 1
           

        # Calculate the total price for each item with cup size adjustment
        if item.quantity > 0:
            extra_drinks = item.quantity // 5
            item.total_quantity = (item.product.dollarprice * cup_multiplier * (item.quantity - extra_drinks)) 
      
    total_price = sum(item.total_quantity for item in cart_items)
    
    location = cart.location
    
    return render(request, 'cart/index.html', {'cart_items': cart_items, 'total_price': total_price, 'location': location, 'Decimal': Decimal})
def create_checkout_session(request):
    try:
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')

        line_items = []

        # Create line items with adjusted prices based on cup size and decreased quantity if it exceeds 6
        for item in cart_items:
            # Apply logic to decrease quantity if it exceeds 6
            if item.quantity >= 1:
                quantity = item.quantity - item.quantity // 5
            else:
                quantity = item.quantity  # Keep the original quantity
            
            # Adjust price based on cup size
            if item.cup_size == 'Sano(S)':
                price_multiplier = 1
            elif item.cup_size == 'Thulo(L)':
                price_multiplier = 3
            elif item.cup_size == 'Thikkako(M)':
                price_multiplier = 2
            else:
                price_multiplier = 1  # Default to 1 if cup size is not recognized

            line_item = {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.product.dollarprice * price_multiplier * 100),  # Adjusted price
                },
                'quantity': quantity,  # Updated quantity
            }
            line_items.append(line_item)

        cart = Cart.objects.select_related('location').get(user=request.user)
        order_date = timezone.now()

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
            metadata={
                'cart_id': cart.id,
                'order_date': order_date.isoformat(),
            }
        )

        return redirect(session.url)
    except stripe.error.StripeError as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('cart')
def payment_success(request):
    try:
        # Retrieve cart items and calculate total amount
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart = Cart.objects.get(user=request.user)
        
        # Create the order date
        order_date = timezone.now()

        # Create the order
        user = request.user
        status = 'Completed'
        order = Order.objects.create(user=user, status=status, cart=cart, date_ordered=order_date)

        # Process each cart item
        for cart_item in cart_items:
            # Calculate extra drinks
            extra_drinks = cart_item.quantity // 5
            
            # Determine the cup size multiplier
            if cart_item.cup_size == 'Sano(S)':
                cup_multiplier = 1
            elif cart_item.cup_size == 'Thulo(L)':
                cup_multiplier = 3
            elif cart_item.cup_size == 'Thikkako(M)':
                cup_multiplier = 2
            else:
                cup_multiplier = 1  # Default to 1 if cup size is not recognized
            
            # Calculate the total quantity including the free extra drinks
            total_quantity = cart_item.quantity 
            
            # Calculate the total amount based on cup size multiplier and extra drinks
            total_amount = (cart_item.product.dollarprice * cup_multiplier * 
                            (cart_item.quantity - extra_drinks))
            
            # Create the order item
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=total_quantity,
                milk=cart_item.milk,
                flavour=cart_item.flavour,
                sweetener=cart_item.sweetener,
                cup_size=cart_item.cup_size,
                location=cart_item.product.locations.first(),  # Assuming product can have multiple locations, taking the first one
                total_amount=total_amount
            )

        # Delete the cart items after successfully creating the order and order items
        cart_items.delete()

        # Delete the cart after successful payment
        cart.delete()

        # Send confirmation email
        subject = 'Order Confirmation'
        html_message = render_to_string('email/order_confirmation.html', {'order': order})
        plain_message = strip_tags(html_message)
        from_email = 'basnyatbrewhub@gmail.com'  # Update with your email
        to_email = [user.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('home')

    except Cart.DoesNotExist:
        messages.error(request, "Cart does not exist for the user.")
        return redirect('cart')
    except stripe.error.StripeError as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('cart')


    except Cart.DoesNotExist:
        messages.error(request, "Cart does not exist for the user.")
        return redirect('cart')
    except stripe.error.StripeError as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('cart')

def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    # Get the product associated with the cart item
    product = cart_item.product

    # Retrieve flavors, sweeteners, and milk related to the product
    product_flavours = product.flavour.all()
    product_sweeteners = product.sweeteners.all()
    product_milks = product.milk.all()

    # Define the cup sizes
    cup_sizes = [
        {"name": "Sano(S)", "volume": "12"},
        {"name": "Thikkako(M)", "volume": "16"},
        {"name": "Thulo(L)", "volume": "24"}
    ]

    if request.method == 'POST':
        # Process form submission
        quantity = int(request.POST.get('quantity', cart_item.quantity))
        milk_id = request.POST.get('milk')
        sweetener = request.POST.get('sweetener')
        flavour = request.POST.get('flavour')
        cup_size = request.POST.get('cup_size')
        
        # Update cart item details
        cart_item.quantity = quantity
        cart_item.milk = milk_id
        cart_item.sweetener = sweetener
        cart_item.flavour = flavour
        cart_item.cup_size = cup_size
        
        # Check if the new quantity is a multiple of 5 and adjust it accordingly
        
        extra_drinks = cart_item.quantity // 5
        messages.success(request, f'You have earned a {extra_drinks} free drink!')
        cart_item.quantity += extra_drinks
        
        cart_item.save()
            
        return redirect('cart')
    
    # Render the form with product details
    return render(request, 'update_cart/update_cart.html', {
        'cart_item': cart_item,
        'product': product,
        'product_flavours': product_flavours,
        'product_sweeteners': product_sweeteners,
        'product_milks': product_milks,
        'cup_sizes': cup_sizes,
    })


def home(request):
    return render(request, 'index.html')

def subscribe_from_footer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                # Check if the email already exists in the database
                if Subscription.objects.filter(email=email).exists():
                    messages.error(request, 'You have already subscribed!')
                    return redirect('home')
                # Create subscription record
                Subscription.objects.create(email=email)
                
                # Send confirmation email
                subject = 'Subscription Confirmation'
                html_message = render_to_string('email/subscription_confirmation.html', {'email': email})
                plain_message = strip_tags(html_message)
                from_email = 'basnyatbrewhub@gmail.com'  # Update with your email
                to_email = [email]
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
                
                messages.success(request, 'You have successfully subscribed!')
                return redirect('home')
            except IntegrityError:
                message = 'An error occurred. Please try again later.'
                return render(request, 'subscription_error.html', {'message': message})
    # If the request is not POST or if email is not provided
    return render(request, 'subscription_error.html', {'message': 'Invalid request.'})
def payment_cancel(request):
    return HttpResponse("Payment was canceled.")

def Reward(request):
    return render(request, 'reward_page/index.html')

@login_required
def username_view(request):
    username = request.user.username
    return render(request, 'navbar.html', {'username': username})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Create a new Contact object and save it to the database
        Contact.objects.create(name=name, email=email, phone=phone, subject=subject, message=message)
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')  # Redirect to a success page after form submission
    return render(request, 'contact_page/index.html')

def about_us(request):
    return render(request, 'about_us/index.html')