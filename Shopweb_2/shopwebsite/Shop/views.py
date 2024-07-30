from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from .models import *


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Create User
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data.get('email', '')
            )

            # Create Customer
            customer = Customer.objects.create(
                user=user,
                name=data['name'],
                email=data.get('email', '')
            )

            return JsonResponse({
                'message': 'User and Customer created successfully',
                'user_id': user.id,
                'customer_id': customer.id
            })
        except KeyError as e:
            return JsonResponse({'message': f'Missing field: {e.args[0]}'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.order_items.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.order_items.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.order_items.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)  # Use request.body to get the raw request data
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItems.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
            order.save()

            if order.shipping == True:
                ShippingAdderss.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],

                )
    else:
        print('User is not logged in ')
    return JsonResponse('payment complete!', safe=False)


@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(
            name=data['name'],
            price=data['price'],
            digital=data['digital'],
            descripation=data['descripation'],
        )
        return JsonResponse({'message': 'Product created successfully', 'product_id': product.id})


def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'digital': product.digital,
            'descripation': product.descripation,
            'image_url': product.imageURL,
        }
        return JsonResponse(product_data, safe=False)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer = Customer.objects.get(id=data['customer_id'])
        order = Order.objects.create(
            customer=customer,
            complete=data['complete'],
            transaction_id=data['transaction_id']
        )
        return JsonResponse({'message': 'Order created successfully', 'order_id': order.id})

@csrf_exempt
def create_order_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = Order.objects.get(id=data['order_id'])
        product = Product.objects.get(id=data['product_id'])
        order_item = OrderItems.objects.create(
            order=order,
            product=product,
            quantity=data['quantity']
        )
        return JsonResponse({'message': 'Order item created successfully', 'order_item_id': order_item.id})


@csrf_exempt
def create_shipping_address(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer = Customer.objects.get(id=data['customer_id'])
        order = Order.objects.get(id=data['order_id'])
        shipping_address = ShippingAdderss.objects.create(
            customer=customer,
            order=order,
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zipcode=data['zipcode']
        )
        return JsonResponse({'message': 'Shipping address created successfully', 'shipping_address_id': shipping_address.id})


@csrf_exempt
def get_product(request, product_id):
    if request.method == 'GET':
        try:
            product = Product.objects.get(id=product_id)
            product_data = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'digital': product.digital,
                'descripation': product.descripation,
                'imageURL': product.imageURL,
            }
            return JsonResponse(product_data)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)



@csrf_exempt
def get_shipping_address(request, shipping_address_id):
    if request.method == 'GET':
        try:
            shipping_address = ShippingAdderss.objects.get(id=shipping_address_id)
            data = {
                'id': shipping_address.id,
                'customer_id': shipping_address.customer.id if shipping_address.customer else None,
                'order_id': shipping_address.order.id if shipping_address.order else None,
                'address': shipping_address.address,
                'city': shipping_address.city,
                'state': shipping_address.state,
                'zipcode': shipping_address.zipcode,
                'date_added': shipping_address.date_added.isoformat()
            }
            return JsonResponse(data)
        except ShippingAdderss.DoesNotExist:
            return JsonResponse({'message': 'Shipping address not found'}, status=404)



@csrf_exempt
def list_shipping_addresses(request):
    if request.method == 'GET':
        shipping_addresses = ShippingAdderss.objects.all()
        data = [{
            'id': sa.id,
            'customer_id': sa.customer.id if sa.customer else None,
            'order_id': sa.order.id if sa.order else None,
            'address': sa.address,
            'city': sa.city,
            'state': sa.state,
            'zipcode': sa.zipcode,
            'date_added': sa.date_added.isoformat()
        } for sa in shipping_addresses]
        return JsonResponse(data, safe=False)
