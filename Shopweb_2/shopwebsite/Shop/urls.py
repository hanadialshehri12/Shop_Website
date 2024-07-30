from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('update_item', views.updateItem, name="update_item"),
    path('process_order', views.processOrder, name="process_order"),
    path('create_product', views.create_product, name="create_product"),
    path('product/<int:product_id>', views.get_product, name="get_product"),
    path('create_order', views.create_order, name="create_order"),
    path('create_order_item', views.create_order_item, name="create_order_item"),
    path('create_shipping_address', views.create_shipping_address, name="create_shipping_address"),
    path('get_shipping_address/<int:shipping_address_id>/', views.get_shipping_address, name='get_shipping_address'),
    path('list_shipping_addresses', views.list_shipping_addresses, name='list_shipping_addresses'),
    path('create_user', views.create_user, name='create_user'),

]
