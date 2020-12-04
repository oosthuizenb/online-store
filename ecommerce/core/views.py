from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect

import hashlib
import requests

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
            
        # TODO create payment instance
        payment = Payment()
        # Prepare data to be submitted to PayFast
        payment_data = {
            'merchant_id': settings.PAYFAST_MERCHANT_ID,
            'merchant_key': settings.PAYFAST_MERCHANT_KEY,
            'return_url': settings.RETURN_URL,
            'cancel_url': settings.CANCEL_URL,
            'notify_url': settings.NOTIFY_URL,
            'name_first': address.name,
            'cell_number': address.mobile_number,
            'm_payment_id': payment.id,
            'amount': payment.amount,
            'item_name': payment.item_name,
            # 'email_confirmation': 1, 1=on 0=off
            'passphrase': 'password',
        }        
        # TODO move hash generation to separate file
        # Concatenate key and value pairs for MD5 hash
        signature_string = ''
        for k, v in payment_data.items():
            signature_string = signature_string + k + '=' + v.strip()
            if k != 'passphrase':
                signature_string = signature_string + '&'
                
        # Replace each space with a + and make all characters uppercase TODO: not sure about uppercase?
        signature_string = signature_string.replace(' ', '+')
        # signature_string = signature_string.upper()
        
        signature = hashlib.md5(signature_string.encode())
        payment_data['signature'] = signature.hexdigest()
        
        # Submit POST request to PayFast
        r = requests.post('payfast url', data=payment_data)
        r_response = r.json()
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