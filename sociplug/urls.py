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

urlpatterns = [
    path('admin/', admin.site.urls),
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
    path('wallet-history/', wallet_history_view, name='wallet_history'),
    path('change-password/', change_password_view, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
