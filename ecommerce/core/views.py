from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect

import hashlib
from urllib.parse import urlencode, quote_plus

from .models import Product, Order, OrderItem, Address, Payment
from .forms import RegisterForm, AddressForm

def index(request):
    products = Product.objects.all()
    # TODO do something if there are no products..
    context = {
        'products': products,
        'user': request.user,
    }
    return render(request, "core/home.html", context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
        'path_info': request.path_info, # For redirecting back here in add_to_cart view
    }
    return render(request, "core/product_detail.html", context)

# TODO password reset view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # TODO unique username error... write custom field validation
            user = User.objects.create_user(username, password=password)
            messages.success(request, 'Your account has been registered.')
            return redirect('core:index')
        else:
            messages.error(request, 'Please fill in the form with valid information.')
            return render(request, "registration/register.html", {'form': form})
    elif request.method == 'GET':
        form = RegisterForm()    
        return render(request, "registration/register.html", {'form': form})
    else:
        raise Http404()
    
def view_cart(request):
    if request.user.is_authenticated:
        try: 
            order = request.user.order_set.get(is_active=True)
            order_items = order.orderitem_set.all()
            context = {
                'order_items': order_items,
            }
            return render(request, "core/cart.html", context)
        except Order.DoesNotExist:
            return render(request, "core/cart.html")
    return render(request, "core/cart.html")

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id) 
    try: # Order is active and only need to add/update item to cart
        order = request.user.order_set.get(is_active=True)
        try: # Check to see if order item already exists, then only update quantity
            order_item = order.orderitem_set.get(item=product)
            order_item.quantity += 1
            messages.success(request, 'The item quantity in your cart has been updated.')
        except OrderItem.DoesNotExist: # If order item does not yet exist, create new order item
            order_item = OrderItem(item=product, order=order)
            messages.success(request, 'The item has been added to your cart.')
        order_item.save()
    except Order.DoesNotExist: # Order has not been created, so create order and add item
        order = Order(user=request.user)
        order.save()
        order_item = OrderItem(item=product, order=order)
        order_item.save()
        messages.success(request, 'The item has been added to your cart.')

    return redirect('core:cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try: # Order is active 
        order = request.user.order_set.get(is_active=True)
        try: # Check to see if order item exists
            order_item = order.orderitem_set.get(item=product)
            order_item.delete()
            messages.success(request, 'The item has been removed from your cart.')
        except OrderItem.DoesNotExist: # If order item does not yet exist, create new order item
            raise Http404
    except Order.DoesNotExist: # Order has not been created so raise Http404
        raise Http404
    
    return redirect('core:cart')

@login_required
def remove_single_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try: # Order is active 
        order = request.user.order_set.get(is_active=True)
        try: # Check to see if order item exists
            order_item = order.orderitem_set.get(item=product)
            order_item.quantity -= 1
            if order_item.quantity == 0: # Remove the order item if the quantity is now 0
                order_item.delete()
                messages.success(request, 'The item has been removed from your cart.')
            else:
                order_item.save()
                messages.success(request, 'The item quantity has been updated.')
        except OrderItem.DoesNotExist: # If order item does not yet exist, create new order item
            raise Http404
    except Order.DoesNotExist: # Order has not been created so raise Http404
        raise Http404
    
    return redirect('core:cart')

@login_required
def checkout(request):
    # Check if order is active, otherwise raise 404
    # TODO optimise this
    if request.user.order_set.filter(is_active=True).exists():
        order = request.user.order_set.get(is_active=True)
    else:
        raise Http404
    if request.method == 'POST':
        # Check if address_id is None, then create new address
        address_id = request.POST.get('addresses')
        if address_id is None:
            form = AddressForm(request.POST)
            # If the form data is valid then create new address
            if form.is_valid():
                address = form.save(commit=False)
                address.user = request.user
                address.save()
        else:
            # If the address_id exists, then use that address for payment
            address = get_object_or_404(Address, pk=address_id)
            
        payment = Payment(amount=order.total_price, item_name="Order #{}".format(order.id), address=address, order=order)
        payment.save()
        
        # Prepare data to be submitted to PayFast
        payment_data = {
            'merchant_id': settings.PAYFAST_MERCHANT_ID,
            'merchant_key': settings.PAYFAST_MERCHANT_KEY,
            'return_url': settings.PAYFAST_RETURN_URL,
            'cancel_url': settings.PAYFAST_CANCEL_URL,
            'notify_url': settings.PAYFAST_NOTIFY_URL,
            'name_first': address.name.strip(), #TODO improve client side validation
            'cell_number': address.mobile_number.strip(),
            'm_payment_id': payment.id,
            'amount': payment.amount,
            'item_name': payment.item_name,
            # 'email_confirmation': 1, 1=on 0=off
            'passphrase': settings.PAYFAST_PASSPHRASE,
        }        
        
        # URL encode payment data and generate signature MD5 hash        
        signature_string = urlencode(payment_data, quote_via=quote_plus)
        signature = hashlib.md5(signature_string.encode())
        payment_data['signature'] = signature.hexdigest()

        # Render template showing payment methods
        return render(request, "core/payments.html", {
            'payment_data': payment_data, 'payfast_url': settings.PAYFAST_URL,
            })
        
    # If GET or any other method then create unbound form
    else:
        # Check if user has existing address
        if request.user.address_set.all().exists():
            existing_addresses = request.user.address_set.all()
        form = AddressForm()
        
    return render(request, "core/checkout.html", {
        'form': form,
        'existing_addresses': existing_addresses,
    })
    
def payment_notify(request):
    # Return 200 Header to PayFast after 4 security checks:
    
    # Security check 1: Verify signature
    payment_data = request.POST.dict() # TODO: Check if you can straight use QueryDict.urlencode()
    payment_data['passphrase'] = settings.PAYFAST_PASSHRASE
    signature_string = urlencode(payment_data, quote_via=quote_plus)
    payfast_signature = payment_data.pop('signature')
    generated_signature = hashlib.md5(signature_string.encode())
    if payfast_signature != generated_signature:
        # If they signatures are unequal, return the 200 Header to indicate that the page is reachable. TODO: What happens if security check fails?
        return HttpResponse()
    
    # Security check 2: Verify the request is coming from a valid PayFast domain
    
    # Security check 3: Confirm payment amount from PayFast is the same as amount in database
    
    # Security check 4: Perform server request to confirm details
    
    