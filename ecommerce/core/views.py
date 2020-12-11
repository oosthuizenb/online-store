from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

import hashlib
import requests
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
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'path_info': request.path_info, # For redirecting back here in add_to_cart view TODO: is this being used?
    }
    return render(request, "core/product_detail.html", context)

# TODO password reset view
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username, password=password)
            messages.success(request, 'Your account has been registered.')
            return redirect('core:index')
        else:
            messages.error(request, 'Please fill in the form with valid information.')
            return render(request, "registration/register.html", {'form': form})
    else:
        form = RegisterForm()    
        return render(request, "registration/register.html", {'form': form})

@login_required
def view_cart(request):
    try: 
        order = Order.objects.get(user=request.user, is_active=True)
    except Order.DoesNotExist:
        return render(request, "core/cart.html")
    order_items = order.orderitem_set.all()
    if order_items.exists():
        context = {
            'order_items': order_items,
        }
        return render(request, "core/cart.html", context)
    return render(request, "core/cart.html")

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order_qs = Order.objects.filter(user=request.user, is_active=True)
    if order_qs.exists():
        # Order is active and only need to add/update item to cart
        order = order_qs[0]
        order_item, created = OrderItem.objects.get_or_create(item=product, order=order)
        if created:
            messages.success(request, 'The item has been added to your cart.')
        else:
            # Order item exists, so update quantity
            order_item.quantity += 1
            messages.success(request, 'The item quantity in your cart has been updated.') 
        order_item.save()
    else:
        # Order has not been created, so create order and add item
        order = Order(user=request.user)
        order.save()
        order_item = OrderItem(item=product, order=order)
        order_item.save()
        messages.success(request, 'The item has been added to your cart.')

    return redirect('core:cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order_qs = Order.objects.filter(user=request.user, is_active=True)
    if order_qs.exists():
        # Order is active 
        order = order_qs[0]
        order_item = get_object_or_404(OrderItem, item=product, order=order)
        order_item.delete()
        messages.success(request, 'The item has been removed from your cart.')
    else:
        # Order has not been created so raise Http404
        raise Http404
    
    return redirect('core:cart')

@login_required
def remove_single_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order_qs = Order.objects.filter(user=request.user, is_active=True)
    if order_qs.exists():
        # Order is active 
        order = order_qs[0]
        order_item = get_object_or_404(OrderItem, item=product, order=order)
        order_item.quantity -= 1
        if order_item.quantity == 0:
            # Remove the order item if the quantity is now 0
            order_item.delete()
            messages.success(request, 'The item has been removed from your cart.')
        else:
            order_item.save()
            messages.success(request, 'The item quantity has been updated.')
    else: 
        # Order has not been created so raise Http404
        raise Http404
    
    return redirect('core:cart')

@login_required
def checkout(request):
    # Check if order is active, otherwise raise 404
    # TODO optimise this
    order_qs = Order.objects.filter(user=request.user, is_active=True)
    if order_qs.exists():
        order = order_qs[0]
        if request.method == 'POST':
            # Check if address_id is None (this means the addresses radio value was not submitted, because the form disappears when new addres is selected), then create new address
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
                
            payment = Payment(amount=order.total_price, item_name=f"Order #{order.id}", address=address, order=order)
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
            existing_addresses = request.user.address_set.all()
            form = AddressForm()
            
        return render(request, "core/checkout.html", {
            'form': form,
            'existing_addresses': existing_addresses,
        })
    else:
        # TODO:If the order does not exist, maybe show a message?
        raise Http404()
    
def payment_notify(request):
    # Return 200 Header to PayFast after 4 security checks:
    
    # Security check 1: Verify signature
    payment_data = request.POST.dict() # TODO: Check if you can straight use QueryDict.urlencode()
    payment_data['passphrase'] = settings.PAYFAST_PASSHRASE
    payfast_signature = payment_data.pop('signature')
    signature_string = urlencode(payment_data, quote_via=quote_plus)
    generated_signature = hashlib.md5(signature_string.encode())
    if payfast_signature != generated_signature:
        # If they signatures are unequal, return the 200 Header to indicate that the page is reachable. TODO: What happens if security check fails? Return 404 for now..
        return Http404()
    
    # Security check 2: Verify the request is coming from a valid PayFast domain
    valid_hosts = settings.PAYFAST_DOMAINS
    request_host = request.META['HTTP_HOST']
    if not valid_hosts.__contains__(request_host):
        return Http404()
    
    # Security check 3: Confirm payment amount from PayFast is the same as amount in database
    payment = get_object_or_404(Payment, id=payment_data['m_payment_id'])
    expected_amount = str(payment.amount)
    requested_amount = payment_data['amount_gross']
    if expected_amount != requested_amount: # TODO types...
        return Http404()
    
    # Security check 4: Perform server request to confirm details
    r = requests.get(settings.PAYFAST_QUERY_URL)
    if r.content != 'VALID': # TODO make sure the r.content is correct way to go
        return Http404()
    
    # Return the default response with a 200 Header to indicate to PayFast the URL is reachable and set payment status to True
    # TODO check payment manually if security checks fail?
    # TODO implement payment status
    payment.successful = True
    payment.save()
    return HttpResponse()
    