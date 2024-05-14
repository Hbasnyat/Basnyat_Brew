from django.contrib import admin

# Register your models here.


# Register your models here.
# admin.py


from .models import CustomUser,Subscription,Category, Location, Product, Cart, CartItem, Order,OrderItem,Flavour,Sweetener,Milk,Contact



admin.site.register(CustomUser)

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Flavour)
admin.site.register(Sweetener)
admin.site.register(Milk)
admin.site.register(Subscription)
admin.site.register(Contact)
