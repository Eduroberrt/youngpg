from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
import uuid
from django.contrib import messages
from django.http import JsonResponse

@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity
        if product.stock < quantity:
            return JsonResponse({'error': "Not enough stock available."})
        elif request.user.profile.balance < total_price:
            return JsonResponse({'error': "Insufficient wallet balance."})
        else:
            # Deduct from wallet
            profile = request.user.profile
            profile.balance -= total_price
            profile.total_orders += 1
            profile.save()
            # Reduce stock
            product.stock -= quantity
            product.save()
            # Create order
            order = Order.objects.create(
                user=request.user,
                product=product,
                transaction_id=str(uuid.uuid4()).replace('-', '')[:12].upper(),
                amount=total_price,
                quantity=quantity
            )
            return JsonResponse({'success': True})
    return render(request, 'product_detail.html', {'product': product})

@login_required
def fund_wallet_view(request):
    error = None
    success = None
    show_bank_details = False
    amount = None

    if request.method == 'POST':
        if 'continue' in request.POST:
            try:
                amount = float(request.POST.get('amount'))
                if amount < 100:
                    error = "Minimum amount is ₦100"
                else:
                    show_bank_details = True
            except:
                error = "Enter a valid amount."
        elif 'fund' in request.POST:
            amount = request.POST.get('amount')
            sender_name = request.POST.get('sender_name')
            proof = request.FILES.get('proof')
            if not sender_name or not proof or not amount:
                error = "All fields are required."
                show_bank_details = True
            else:
                # Save payment request for admin review
                payment = PaymentHistory.objects.create(
                    user=request.user,
                    amount=amount,
                    type="Deposit",
                    status="Pending"
                )
                # Save proof image
                payment.proof = proof
                payment.save()
                success = "Your payment has been submitted and is pending admin approval."
    context = {
        'error': error,
        'success': success,
        'show_bank_details': show_bank_details,
        'amount': amount
    }
    return render(request, 'fund_wallet.html', context)

@login_required
def change_password_view(request):
    error = None
    success = None
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user
        if not user.check_password(current_password):
            error = "Current password is incorrect."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        elif len(new_password) < 8:
            error = "New password must be at least 8 characters."
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            success = "Password updated successfully."
    return render(request, 'change_password.html', {'error': error, 'success': success})

@login_required
def dashboard_view(request):
    latest_payments = request.user.payments.order_by('-date')[:10]
    return render(request, 'dashboard.html', {
        'latest_payments': latest_payments,
    })

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def support_view(request):
    return render(request, 'support.html')

def terms_view(request):
    return render(request, 'terms.html')

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        elif User.objects.filter(email=email).exists():
            error = "Email already exists."
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('product_list')
    return render(request, 'register.html', {'error': error})

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            error = "Invalid username or password."
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def product_list(request):
    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'product_list.html', {'categories': categories})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    categories = Category.objects.all()
    return render(request, 'category_products.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

@login_required
def wallet_history_view(request):
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-date')

    # Filtering
    status = request.GET.get('status')
    tx_type = request.GET.get('type')
    if status:
        payments = payments.filter(status=status)
    if tx_type:
        payments = payments.filter(type=tx_type)

    # Pagination
    paginator = Paginator(payments, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'wallet_history.html', {
        'page_obj': page_obj,
        'status': status,
        'tx_type': tx_type,
    })


def rules_view(request):
    return render(request, 'rules.html')




