"""
URL configuration for sociplug project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/products', permanent=True)),
    path('products/', product_list, name='product_list'),
    path('category/<slug:slug>/', category_products, name='category_products'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('fund-wallet/', fund_wallet_view, name='fund_wallet'),
    path('orders/', orders_view, name='orders'),
    path('support/', support_view, name='support'),
    path('rules/', rules_view, name='rules'),
    path('terms/', terms_view, name='terms'),
    path('paymentpoint/webhook/', paymentpoint_webhook, name='paymentpoint_webhook'),
    path('wallet-history/', wallet_history_view, name='wallet_history'),
    path('change-password/', change_password_view, name='change_password'),
    path('forgot-password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='reset_confirm.html',
        success_url='/login/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='reset_done.html'
    ), name='password_reset_complete'),

    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='forgot_password_done.html'
    ), name='password_reset_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
