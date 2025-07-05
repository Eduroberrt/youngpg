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
from django.core.mail import send_mail
from django.conf import settings
import json
from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.template.loader import render_to_string
from django.utils import timezone

class CustomPasswordResetView(PasswordResetView):
    template_name = 'forgot_password.html'
    html_email_template_name = 'reset_email.html'
    subject_template_name = 'reset_subject.txt'
    success_url = '/forgot-password/done/'

    def form_valid(self, form):
        email = form.cleaned_data["email"].strip().lower()  # <-- Lowercase and strip spaces
        if not User.objects.filter(email__iexact=email).exists():
            return self.form_invalid(form)
        
        form.cleaned_data["email"] = email
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(
            form=form,
            error="No user with that email address exists."
        ))

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
    account_details = None
    submitted_amount = None

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            if amount < 100:
                error = "Minimum amount is ₦100"
            else:
                submitted_amount = amount
                payload = {
                    "email": request.user.email,
                    "name": request.user.get_full_name() or request.user.username,
                    "phoneNumber": getattr(request.user.profile, 'phone', '08000000000'),
                    "bankCode": ["20946"],
                    "businessId": settings.PAYMENTPOINT_BUSINESS_ID
                }

                headers = {
                    "Authorization": f"Bearer {settings.PAYMENTPOINT_AUTH}",
                    "api-key": settings.PAYMENTPOINT_API_KEY,
                    "Content-Type": "application/json"
                }

                resp = requests.post(
                    "https://api.paymentpoint.co/api/v1/createVirtualAccount",
                    json=payload,
                    headers=headers,
                    timeout=20
                )

                if resp.status_code != 201:
                    error = f"PaymentPoint API error {resp.status_code}: {resp.text}"
                else:
                    data = resp.json()
                    if data.get("status") == "success":
                        account = data["bankAccounts"][0]
                        account_details = {
                            "account_name": account["accountName"],
                            "account_number": account["accountNumber"],
                            "bank_name": account["bankName"],
                        }
                        success = "Virtual account created. Please make payment. Your wallet will be automatically credited."
                    else:
                        error = data.get("message", "Account creation failed.")
        except Exception as e:
            error = f"Exception occurred: {str(e)}"

    return render(request, 'fund_wallet.html', {
        'error': error,
        'success': success,
        'account_details': account_details,
        'submitted_amount': submitted_amount,
    })


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
            # Send welcome email (HTML)
            subject = 'Welcome to YoungPG Media'
            plain_message = 'Thank you for registering at YoungPG Media!'
            html_message = render_to_string('welcome_email.html', {
                'username': username,
                'site_url': request.build_absolute_uri('/dashboard/'),
                'now': timezone.now().year,
            })
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(
                subject,
                plain_message,
                from_email,
                [email],
                html_message=html_message,
                fail_silently=True,
            )
            return redirect('product_list')
    return render(request, 'register.html', {'error': error})

def login_view(request):
    error = None
    next_url = request.GET.get('next', request.POST.get('next', ''))
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            # Try email
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('product_list')
        else:
            error = "Invalid username/email or password."
    return render(request, 'login.html', {'error': error, 'next': next_url})

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
    
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    categories = Category.objects.all()
    return render(request, 'category_products.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

@csrf_exempt
@require_POST
def paymentpoint_webhook(request):
    try:
        payload = json.loads(request.body)

        # Extract fields from webhook payload
        customer_email = payload.get('customer_email')
        amount_paid = float(payload.get('amount', 0))
        status = payload.get('status')
        reference = payload.get('reference') or ''  # Optional field

        # Only process successful transactions
        if status != "Success":
            return JsonResponse({"message": "Transaction ignored (not successful)"}, status=200)

        # Match the user by email
        user = User.objects.filter(email=customer_email).first()
        if not user:
            return JsonResponse({"message": "User not found"}, status=404)

        # Prevent duplicate credits
        if PaymentHistory.objects.filter(user=user, amount=amount_paid, status="Success").exists():
            return JsonResponse({"message": "Payment already processed"}, status=200)

        # Create payment history
        PaymentHistory.objects.create(
            user=user,
            amount=amount_paid,
            type="PaymentPoint",
            status="Success"
        )

        # Credit the wallet
        profile = user.profile
        profile.balance += amount_paid
        profile.total_deposits += amount_paid
        profile.save()

        return JsonResponse({"message": "Wallet credited successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)