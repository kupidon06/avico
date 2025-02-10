from django.urls import path
from .views import (create_batch_allocation,delete_order_item,cancel_order,update_order_item
,user_order_list,product_list,cancel_order, apply_coupon, ecommerce ,filter_product_units, list_delivery_location,delete_delivery_location,
update_delivery_location,create_delivery_location,change_password,
order_list, create_order, update_order, delete_order, export_orders, bulk_delete_orders, make_payment, create_order_without_user)
from .test import initiate_payment,payment_webhook
urlpatterns = [
    path('pos/', product_list, name='pos'),
    path('ecommerce/',ecommerce , name='ecommerce'),
    path('apply_coupon/',apply_coupon , name='apply_coupon'),
    path('my-orders/',user_order_list , name='my-orders'),
    path('change-password/customer',change_password , name='change_password_customer'),
    path('my-account/',list_delivery_location , name='my-account'),
    path('delivery-location/create/',create_delivery_location , name='create_delivery_location'),
    path('delivery-location/update/<int:pk>/', update_delivery_location, name='update_delivery_location'),
    path('delivery-location/delete/<int:pk>/', delete_delivery_location, name='delete_delivery_location'),
    
    

    path('products/filter/', filter_product_units, name='filter_product_units'),
    path('orders/', order_list, name='order_list'),
    path('orders/bacthes/', create_batch_allocation, name='create_batch_allocation'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/<uuid:order_id>/update/', update_order, name='update_order'),
    path('orders/<uuid:id>/delete/', delete_order, name='delete_order'),
    path('orders/export/', export_orders, name='order_list_export'),
    path('orders/bulk_delete/', bulk_delete_orders, name='bulk_delete_orders'),
    path('orders/<uuid:order_id>/payments/create/', make_payment, name='make_payment'),
    path('orders/create_without_user/', create_order_without_user, name='create_order_without_user'),
    path('orders/item/delete/<int:item_id>/', delete_order_item, name='delete_order_item'),
    path('orders/item/update/<int:item_id>/', update_order_item, name='update_order_item'),
    path('orders/cancel/<uuid:order_id>/', cancel_order, name='cancel_order'),
    path('payments/create/<uuid:order_id>/',initiate_payment, name='test_payment'),
    path('webhook/',payment_webhook, name='webhook')
]
