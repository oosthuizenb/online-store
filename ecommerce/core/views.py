from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

import datetime
import hashlib
import requests
from urllib.parse import urlencode, quote_plus

from .models import Product, Order, OrderItem, Address, Payment, Review
from .forms import RegisterForm, AddressForm, ReviewForm

User = get_user_model()

def index(request):
    products = Product.objects.all()
    # TODO do something if there are no products..in the template?
    context = {
        'products': products,
        'user': request.user,
    }
    return render(request, "core/home.html", context)

def search(request):
    search_text = request.GET.get('search')
    if search_text:
        search_param = search_text.strip()
        products = Product.objects.filter(title__icontains=search_param)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
    }
    return render(request, "core/home.html", context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    form = ReviewForm()
    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, "core/product_detail.html", context)

@login_required
def review_submit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()

        return redirect('core:product-detail', product_id=product_id)
    else:
        reviews = Review.objects.filter(product=product)
        context = {
            'product': product,
            'reviews': reviews,
            'form': form,
        }
        
        return render(request, 'core/product_detail.html', context)

# TODO password reset view
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(email, password=password)
            messages.success(request, 'Your account has been registered.')
            return redirect('core:index')
        else:
            messages.error(request, 'Please fill in the form with valid information.')
            return render(request, "registration/register.html", {'form': form})
    else:
        form = RegisterForm()    
        return render(request, "registration/register.html", {'form': form})

def view_cart(request):
    order, new_obj = Order.objects.new_or_get(request)
    order_items = order.orderitem_set.all()
    if order_items.exists():
        context = {
            'order_items': order_items,
        }
        return render(request, "core/cart.html", context)
    return render(request, "core/cart.html")
        
def add_to_cart(request, product_id, redirect_url):
    product = get_object_or_404(Product, pk=product_id)
    order, new_obj = Order.objects.new_or_get(request)

    order_item, created = OrderItem.objects.get_or_create(item=product, order=order)
    if created:
        messages.success(request, 'The item has been added to your cart.')
    else:
        # Order item exists, so update quantity
        order_item.quantity += 1
        messages.success(request, 'The item quantity in your cart has been updated.') 
    order_item.save()

    if redirect_url == 'product-detail':
        return redirect('core:product-detail', product_id=product_id)
    
    return redirect('core:cart')

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order, new_obj = Order.objects.new_or_get(request)
    order_item = get_object_or_404(OrderItem, item=product, order=order)
    order_item.delete()
    messages.success(request, 'The item has been removed from your cart.')
    
    return redirect('core:cart')

def remove_single_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order, new_obj = Order.objects.new_or_get(request)
    order_item = get_object_or_404(OrderItem, item=product, order=order)
    order_item.quantity -= 1
    if order_item.quantity == 0:
        # Remove the order item if the quantity is now 0
        order_item.delete()
        messages.success(request, 'The item has been removed from your cart.')
    else:
        order_item.save()
        messages.success(request, 'The item quantity has been updated.')
    
    return redirect('core:cart')

@login_required
def checkout(request):
    # TODO optimise this
    order_qs = Order.objects.filter(user=request.user, is_active=True)
    if order_qs.exists():
        order = order_qs[0]
        order_items_qs = OrderItem.objects.filter(order=order)
        if order_items_qs.exists():
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
                        existing_addresses = request.user.address_set.all()
                        return render(request, "core/checkout.html", {
                            'form': form,
                            'existing_addresses': existing_addresses,
                        })
                else:
                    # If the address_id exists, then use that address for payment
                    # TODO return form error instead of 404 maybe? or not... this can't happen if user does normal stuff..
                    address = get_object_or_404(Address, pk=address_id)
                    
                payment = Payment(amount=order.total_price, address=address, order=order)
                payment.save()
                
                # Prepare data to be submitted to PayFast
                payment_data = {
                    'merchant_id': settings.PAYFAST_MERCHANT_ID,
                    'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                    'return_url': settings.PAYFAST_RETURN_URL,
                    'cancel_url': settings.PAYFAST_CANCEL_URL,
                    'notify_url': settings.PAYFAST_NOTIFY_URL,
                    'name_first': address.name.strip(), #TODO improve client side validation, and when instance is saved, strip then...?
                    'cell_number': address.mobile_number.strip(),
                    'm_payment_id': payment.id,
                    'amount': payment.amount,
                    'item_name': payment.item_name,
                    # 'email_confirmation': 1, 1=on 0=off
                    # 'passphrase': settings.PAYFAST_PASSPHRASE,
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
            return redirect('core:cart')
    else:
        # TODO:If the order does not exist, maybe show a message?
        return redirect('core:cart')
    
#TODO only POST method.. 
@csrf_exempt
def payment_notify(request):
    # Return 200 Header to PayFast after 4 security checks:
    payment_data = request.POST.dict() # TODO: Check if you can straight use QueryDict.urlencode()
    payment = get_object_or_404(Payment, id=payment_data['m_payment_id'])
    payment.status = 'S'
    
    # Security check 1: Verify signature
    # payment_data['passphrase'] = settings.PAYFAST_PASSPHRASE
    payfast_signature = payment_data.pop('signature')
    signature_string = urlencode(payment_data, quote_via=quote_plus)
    generated_signature = hashlib.md5(signature_string.encode()).hexdigest()
    if payfast_signature != generated_signature:
        # If they signatures are unequal, return the 200 Header to indicate that the page is reachable.
        payment.status = 'U'
    
    # Security check 2: Verify the request is coming from a valid PayFast domain
    valid_hosts = settings.PAYFAST_DOMAINS
    request_host = request.headers['REFERER']
    if not request_host in valid_hosts:
        payment.status = 'U'
    
    # Security check 3: Confirm payment amount from PayFast is the same as amount in database
    expected_amount = payment.amount
    requested_amount = float(payment_data['amount_gross'])
    if expected_amount != requested_amount: # TODO types...
        payment.status = 'U'
    
    # Security check 4: Perform server request to confirm details
    # payment_data['signature'] = generated_signature
    # payfast_parameter = urlencode(payment_data, quote_via=quote_plus)
    # r = requests.post(settings.PAYFAST_QUERY_URL, data=payfast_parameter)
    # if r.content != 'VALID': # TODO make sure the r.content is correct way to go
    #     payment.status = 'U'
    
    
    payment.save()
    if payment.status == 'S':
        # Place order if payment is successful. TODO: Maybe change the business logic?
        order = payment.order
        order.placement_date = datetime.date.today()
        order.is_active = False
        order.save()

        email_title = f'{payment.item_name} confirmation'
        email_message = f'Dear {payment.order.user.username} \n\nYour order has been placed.'

        # send_mail(email_title, email_message, settings.EMAIL_HOST_USER, ['berrieswebdev@gmail.com'], fail_silently=False)


    # Return 200 Header for PayFast    
    return HttpResponse()
    

def payment_cancel(request):
    print('cancelled')
    # send_mail('Order payment cancelled', 'Your payment was cancelled. You can try again.', settings.EMAIL_HOST_USER, ['berrieswebdev@gmail.com'], fail_silently=False)
    # TODO set payment to cancelled.
    messages.error(request, 'The payment has been cancelled. If you still want to place the order, you need to complete payment.')
    return redirect('core:index')

def payment_return(request):
    print('returned')
    # send_mail('Order confirmation', 'Your order has been placed.', settings.EMAIL_HOST_USER, ['berrieswebdev@gmail.com'], fail_silently=False)
    messages.success(request, 'The order has been placed. You will soon receive a payment confirmation email.')
    return redirect('core:index')
    