from django.contrib import admin
from .models import Product, Category, Order, OrderItem, Review, UserActivity

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(UserActivity)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'status', 'approval_status')
    list_filter = ('status', 'approval_status', 'created_at')
    inlines = [OrderItemInline]
    actions = ['approve_orders', 'reject_orders']

    def approve_orders(self, request, queryset):
        updated = queryset.update(approval_status='Approved')
        self.message_user(request, f"{updated} orders marked as Approved.")

    def reject_orders(self, request, queryset):
        updated = queryset.update(approval_status='Rejected')
        self.message_user(request, f"{updated} orders marked as Rejected.")


from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
