from decimal import Decimal
from django.conf import settings
from django.db import models
from carts.models import Cart
from django.db.models.signals import pre_save
# Create your models here.


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,null=True,blank=True)#not required
    email = models.EmailField(unique=True) #--> required
    #merchant_id

    def __unicode__(self):
        return self.email


ADDRESS_TYPE =(
    ('billing','Billing'),
    ('shipping','Shipping'),
)

class UserAddress(models.Model):
    user = models.ForeignKey(UserCheckout)
    type = models.CharField(max_length=120,choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zip_code = models.CharField(max_length=120)

    def __unicode__(self):
        return self.street

class Order(models.Model):
    cart = models.ForeignKey(Cart)
    user = models.ForeignKey(UserCheckout,null=True)
    billing_address = models.ForeignKey(UserAddress,related_name="billing_address",null=True)
    shipping_address = models.ForeignKey(UserAddress,related_name="shiping_address",null=True)
    shipping_total_price = models.DecimalField(max_digits=50,decimal_places=2,default=5.95)
    order_total = models.DecimalField(max_digits=50,decimal_places=2)
    #order_id

    def __unicode__(self):
        return str(self.cart.id)


def order_pre_save(sender,instance,*args, **kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)

#class Order(models.Model):
    #cart
    #usercheckout--> required
    #shipping address
    #billing address
    #shipping total price
    #order total (cart total+ shipping)
    #order_id --> custom id
