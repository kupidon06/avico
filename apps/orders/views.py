from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ValidationError
from openpyxl import Workbook
from .models import Order, OrderItem, Payment, Coupon, BatchAllocation,DeliveryLocation
from apps.profile.models import CompanyProfile
from apps.products.models import Product, ProductUnit, Discount, Category
from apps.management.models import Batch
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import datetime
from apps.users.decorators import role_required
import json

login_path = 'login'

@login_required(login_url=login_path)
def product_list(request):
    """Affiche les produits disponibles pour créer une commande."""
    categories = Category.objects.all()
    products = ProductUnit.objects.all()

    # Pagination
    paginator = Paginator(products, 10)  # 10 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/detail.html', {'categories': categories, 'page_obj': page_obj})
@csrf_exempt
@login_required(login_url=login_path)
def ecommerce(request):
    """Affiche les produits disponibles pour créer une commande."""
    categories = Category.objects.all()
    company_profile = CompanyProfile.objects.first()
    locations = DeliveryLocation.objects.filter(user=request.user)
    return render(request, 'apps/orders/ecom.html', {'categories': categories, 'company':company_profile,'locations':locations})



@csrf_exempt
def filter_product_units(request):
    """
    Filtre les unités de produits (ProductUnit) en fonction des critères envoyés via POST.
    Retourne les résultats sous forme JSON avec support de filtrage par nom et pagination.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)

    try:
        category_id = request.POST.get("category_id")
        min_price = request.POST.get("min_price")
        max_price = request.POST.get("max_price")
        name = request.POST.get("name", "").strip()
        page = int(request.POST.get("page", 1))
        page_size = int(request.POST.get("page_size", 5))
    except ValueError:
        return JsonResponse({"error": "Invalid input parameters"}, status=400)

    filters = Q()
    if category_id:
        filters &= Q(product__category_id=category_id)
    if min_price:
        try:
            filters &= Q(price__gte=Decimal(min_price))
        except:
            return JsonResponse({"error": "Invalid min_price format"}, status=400)
    if max_price:
        try:
            filters &= Q(price__lte=Decimal(max_price))
        except:
            return JsonResponse({"error": "Invalid max_price format"}, status=400)
    if name:
        filters &= Q(name__icontains=name)

    product_units = ProductUnit.objects.filter(filters).select_related("product").prefetch_related("medias")
    
    product_units = product_units[(page - 1) * page_size: page * page_size]

    data = [
        {
            "id": unit.id,
            "name": unit.name,
            "quantity": unit.quantity,
            "price": float(unit.price),
            "photos": [media.file.url for media in unit.medias.all()]  # Liste de toutes les images
        }
        for unit in product_units
    ]

    return JsonResponse({
        "product_units": data,
        
        "page": page,
        "page_size": page_size,
    }, status=200)




@login_required(login_url='login')
@role_required(excluded_roles=['customer', 'veterinarian', 'employee', 'farmer'])
def order_list(request):
    """Affiche la liste des commandes avec pagination."""
    order_id = request.GET.get('order_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    coupon_code = request.GET.get('coupon')

    orders_query = Q()
    if order_id:
        orders_query &= Q(id=order_id)
    if date_from and date_to:
        orders_query &= Q(created_at__range=[date_from, date_to])
    elif date_from:
        orders_query &= Q(created_at__gte=date_from)
    elif date_to:
        orders_query &= Q(created_at__lte=date_to)
    if coupon_code:
        orders_query &= Q(coupon__code=coupon_code)

    orders = Order.objects.filter(orders_query).order_by('-created_at')
    batches = Batch.objects.all().order_by('id')
    allocations = BatchAllocation.objects.all().order_by('id')

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/list.html', {'page_obj': page_obj, 'batches': batches, 'allocations': allocations})

@csrf_exempt
@role_required(excluded_roles=['customer', 'veterinarian', 'employee', 'farmer'])
def create_batch_allocation(request):
    """Crée une allocation de lot pour un article de commande."""
    if request.method == 'POST':
        try:
            order_item_id = request.POST.get('order_item_id')
            batch_id = request.POST.get('batch_id')
            quantity_eggs = int(request.POST.get('quantity_eggs', 0))
            quantity_poultry = int(request.POST.get('quantity_poultry', 0))

            order_item = get_object_or_404(OrderItem, id=order_item_id)
            batch = get_object_or_404(Batch, id=batch_id)

            batch_allocation = BatchAllocation(
                order_item=order_item,
                batch=batch,
                quantity_eggs=quantity_eggs,
                quantity_poultry=quantity_poultry
            )
            batch_allocation.save()

            return JsonResponse({'status': 'success', 'message': 'Batch allocation created successfully', 'batch_allocation_id': str(batch_allocation.id)})

        except ValidationError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required(login_url=login_path)
def create_order(request):
    """Crée une nouvelle commande avec des articles."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                customer=request.user,
                delivery_address=data.get('delivery_address'),
                coupon=data.get('coupon')
            )

            coupon_code = data.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(Coupon, code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            items = data.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                product_unit = get_object_or_404(ProductUnit, id=product_id)

                OrderItem.objects.create(
                    order=order,
                    product_unit=product_unit,
                    quantity=quantity
                )

            order.calculate_total()
            order.save()

            return JsonResponse({'message': 'Order created successfully', 'order_id': str(order.id)})

        except Exception as e:
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer', 'cashier', 'veterinarian', 'accountant', 'employee', 'farmer'])
def update_order(request, order_id):
    """Met à jour une commande existante."""
    order = get_object_or_404(Order, id=order_id)

    if request.method in ['POST', 'PUT']:
        try:
            order.status = request.POST.get('status', order.status)
            order.delivery_address = request.POST.get('delivery_address', order.delivery_address)
            discount_str = request.POST.get('discount', order.discount)
            order.discount_type = request.POST.get('discount_type', order.discount_type)

            try:
                discount_str = discount_str.replace(',', '.')
                order.discount = Decimal(discount_str)
            except InvalidOperation:
                return JsonResponse({'error': 'Invalid discount value'}, status=400)

            coupon_code = request.POST.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(
                    Coupon,
                    code=coupon_code,
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            order.save()
            return redirect('order_list')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return redirect('order_list')

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer', 'cashier', 'veterinarian', 'accountant', 'employee', 'farmer'])
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('order_list')

@login_required(login_url=login_path)
def export_orders(request):
    """Exporte les commandes au format Excel."""
    orders = Order.objects.all().order_by('-created_at')
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["Order ID", "Customer", "Status", "Total Amount", "Created At"])

    for order in orders:
        ws.append([str(order.id), order.customer.username if order.customer else 'Anonymous', order.status, order.total_amount, order.created_at])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Orders.xlsx'
    wb.save(response)
    return response

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer', 'cashier', 'veterinarian', 'accountant', 'employee', 'farmer'])
def bulk_delete_orders(request):
    """Supprime plusieurs commandes en une seule requête."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            if not order_ids:
                return JsonResponse({'status': 'error', 'message': 'No orders selected.'}, status=400)

            deleted, _ = Order.objects.filter(id__in=order_ids).delete()
            return JsonResponse({'status': 'success', 'message': f'{deleted} orders deleted.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)

@csrf_exempt
@login_required(login_url=login_path)
def make_payment(request, order_id):
    """Enregistre un paiement pour une commande."""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        payment_method = data.get('payment_method')
        transaction_id = data.get('transaction_id', None)
        remark = data.get('remark', '')

        try:
            Payment.objects.create(
                order=order,
                amount=amount,
                payment_status='paid',
                payment_method=payment_method,
                transaction_id=transaction_id,
                remark=remark
            )
            return JsonResponse({'message': 'Payment recorded successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'apps/ecommerce/make_payment.html', {'order': order})

@csrf_exempt
def create_order_without_user(request):
    """Crée une commande sans utilisateur."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                status=data.get('status', 'pending'),
                delivery_address=data.get('delivery_address'),
                discount=data.get('discount', 0.00),
                discount_type=data.get('discount_type', 'percentage')
            )

            coupon_code = data.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(Coupon, code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            items = data.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                try:
                    product_unit = ProductUnit.objects.get(id=product_id)
                except ProductUnit.DoesNotExist:
                    return JsonResponse({'error': f'ProductUnit with id={product_id} does not exist'}, status=400)

                OrderItem.objects.create(
                    order=order,
                    product_unit=product_unit,
                    quantity=quantity
                )

            order.calculate_total()
            order.save()

            return JsonResponse({'message': 'Order created successfully', 'order_id': str(order.id)})
        except Exception as e:
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                return JsonResponse({'success': True, 'percentage': coupon.percentage})
            else:
                return JsonResponse({'success': False, 'message': 'Coupon expiré ou inactif.'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Coupon invalide.'})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Order, OrderItem

@csrf_exempt
@login_required(login_url=login_path)
def user_order_list(request):
    """Récupère les commandes d'un utilisateur avec pagination et filtres."""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status= request.GET.get('status')

    orders_query = Q(customer=request.user)
    if date_from and date_to:
        orders_query &= Q(created_at__range=[date_from, date_to])
    elif date_from:
        orders_query &= Q(created_at__gte=date_from)
    elif date_to:
        orders_query &= Q(created_at__lte=date_to)
    if status and status in dict(Order.STATUS_CHOICES):  
        orders_query &= Q(status=status)

    orders = Order.objects.filter(orders_query).order_by('-created_at')
    paginator = Paginator(orders, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/main.html', {'page_obj': page_obj})
@csrf_exempt
@login_required(login_url=login_path)
def delete_order_item(request, item_id):
    """Supprime un item de commande."""
    order_item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user)
    order_item.delete()
    order_item.order.save() 
    return redirect('my-orders')

@csrf_exempt
@login_required(login_url=login_path)
def update_order_item(request, item_id):
    """Met à jour la quantité d'un item dans la commande."""
    order_item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user)
    new_quantity = request.POST.get('quantity')
    
    if new_quantity and int(new_quantity) > 0:
        order_item.quantity = int(new_quantity)
        order_item.save()
        order_item.order.save() 
        return redirect('my-orders')
    
    return redirect('my-orders')
@csrf_exempt
@login_required(login_url=login_path)
def cancel_order(request, order_id):
    """Annule une commande si elle n'est pas encore traitée."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status not in ['completed', 'canceled']:  
        order.status = 'canceled'
        order.save()
        return redirect('my-orders')
    
    return redirect('my-orders')



from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm

@csrf_exempt
@login_required(login_url=login_path)
def change_password(request):
    """Permet à un utilisateur de modifier son mot de passe."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Pour éviter la déconnexion après le changement de mot de passe
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('profile')  # Redirige vers la page du profil ou une autre page
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})



@csrf_exempt
@login_required(login_url=login_path)
def list_delivery_location(request):
    """Vue pour lister les adresses de livraison de l'utilisateur connecté."""
    locations = DeliveryLocation.objects.filter(user=request.user)
    return render(request, "apps/delivery_locations/location_list.html", {"locations": locations})


from django.http import JsonResponse
@csrf_exempt
@login_required(login_url=login_path)
def create_delivery_location(request):
    """Vue pour créer une adresse de livraison sans formulaire."""
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        is_default = request.POST.get("is_default") == "true"  # Convertir en booléen

        if name and address:
            location = DeliveryLocation.objects.create(
                user=request.user,
                name=name,
                address=address,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None,
                is_default=is_default
            )
            return redirect('my-account')
        
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
@login_required(login_url=login_path)
def update_delivery_location(request, pk):
    """Vue pour modifier une adresse de livraison sans formulaire."""
    location = get_object_or_404(DeliveryLocation, pk=pk, user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", location.name)
        address = request.POST.get("address", location.address)
        latitude = request.POST.get("latitude", location.latitude)
        longitude = request.POST.get("longitude", location.longitude)
        is_default = request.POST.get("is_default", str(location.is_default)) == "true"

        # Mise à jour des champs
        location.name = name
        location.address = address
        location.latitude = latitude if latitude else None
        location.longitude = longitude if longitude else None
        location.is_default = is_default
        location.save()

        return redirect('my-account')

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
@login_required(login_url=login_path)
def delete_delivery_location(request, pk):
    """Vue pour supprimer une adresse de livraison."""
    location = get_object_or_404(DeliveryLocation, pk=pk, user=request.user)

    if request.method == "POST":
        location.delete()
        return redirect("my-account")  # Redirection après suppression

    return render(request, "delivery_locations/location_confirm_delete.html", {"location": location})

