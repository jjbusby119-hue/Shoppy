from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Profile(models.Model):
    # User types
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('buyer', 'Buyer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class UserGroup(models.Model):
    # User groups
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name='user_groups')

    def __str__(self):

        return self.name


class Store(models.Model):
    # Store models
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # Product models
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    qty = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    # Cart models
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    # Cart item models
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Review(models.Model):
    # Review models
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    # Order models
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    # Order item models
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    