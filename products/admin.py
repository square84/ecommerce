from django.contrib import admin

#importamos el modelo
from .models import Product,Variation,ProductImage,Category,ProductFeatured


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    max_num = 10

#Pone en Product las Variaciones del Producto
class VariationInline(admin.TabularInline):
    model = Variation
    #Para poner cuantas opciones
    extra = 0
    max_num = 10


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','price']
    inlines = [
        VariationInline,
    ]
    class Meta:
        model = Product



# Register your models here.


admin.site.register(Product,ProductAdmin)
admin.site.register(Variation)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(ProductFeatured)