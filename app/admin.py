from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    fields = ('category', 'title', 'slug', 'image', 'price', 'stock', 'description')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_orders', 'total_deposits')
    search_fields = ('user__username', 'user__email')

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'type', 'status')
    list_filter = ('status', 'type')
    search_fields = ('user__username', 'user__email')

    def save_model(self, request, obj, form, change):
        # Only credit wallet if status is being set to "Success" and wasn't already "Success"
        if change:
            old_obj = PaymentHistory.objects.get(pk=obj.pk)
            if old_obj.status != "Success" and obj.status == "Success":
                profile = obj.user.profile
                profile.balance += obj.amount
                profile.total_deposits += obj.amount
                profile.save()
        elif obj.status == "Success":
            profile = obj.user.profile
            profile.balance += obj.amount
            profile.total_deposits += obj.amount
            profile.save()
        super().save_model(request, obj, form, change)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'transaction_id', 'ordered_at', 'amount', 'quantity', 'fulfilled')
    list_filter = ('fulfilled', 'product')
    search_fields = ('user__username', 'transaction_id', 'product__title')
    readonly_fields = ('user', 'product', 'transaction_id', 'ordered_at', 'amount', 'quantity')
    fields = ('user', 'product', 'transaction_id', 'ordered_at', 'amount', 'quantity', 'fulfilled', 'digital_product')

@admin.register(PaymentPointTransaction)
class PaymentPointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reference', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'reference')
    list_filter = ('status',)