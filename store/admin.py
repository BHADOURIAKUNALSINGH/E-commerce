from django.contrib import admin
from .models import Category, Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'image_preview')
    list_filter = ('category', 'stock')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return 'No Image'
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'item_count')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

    def item_count(self, obj):
        return obj.orderitem_set.count()
    item_count.short_description = 'Number of Items'
