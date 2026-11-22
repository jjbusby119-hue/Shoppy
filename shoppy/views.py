from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django .contrib import messages
from django.core.mail import send_mail
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import status
import requests
import email
from django.http import JsonResponse
from .tweet import Tweet
from . import forms
from .forms import SignupForm
from .models import Store, Product, Review, Order, OrderItem, Profile, User
from .serializers import ProductSerializer, ReviewSerializer, StoreSerializer


# Decorators
def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.user_type != 'vendor':
            print("Vendor required: Not a vendor")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def buyer_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.user_type != 'buyer':
            print("Buyer required: Not a buyer")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


# Views
# Signup
def signup(request):

    form = SignupForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()

        user.profile.user_type = form.cleaned_data['user_type']
        user.profile.save()

        login(request, user)
        return redirect('home')

    return render(request, 'registration/signup.html', {'form': form})

# Vendor
@vendor_required
def create_store(request):

    form = forms.StoreForm(request.POST or None)
    
    # Create store
    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.owner = request.user
        store.save()

        # Create tweet
        tweet = Tweet()
        tweet.new_store_tweet = f"""A new store just arrived at Shoppy! Chaeck it out now!
        \nStore Name: {store.name}
        \nDescription: {store.description}"""

        if store.logo:
            tweet.new_store_tweet += f"\nLogo: {store.logo.url}"

        tweet_payload = {'text': tweet.new_store_tweet}
        try:
            Tweet._instance.make_tweet(tweet_payload)
        except Exception as e:
            print(f"Error sending tweet: {e}")


        print("Create store: Store created")
        return redirect("vendor_dashboard")
    
    return render(request, "store/create_store.html", {"form": form})


# Vendor
@vendor_required
def vendor_dashboard(request):

    stores = Store.objects.filter(owner=request.user)

    # Set user typw
    print("Vendor dashboard: Stores retrieved")
    return render(request, "store/vendor_dashboard.html", {
        "stores": stores
    })


# Vendor
@vendor_required
def edit_store(request, store_id):

    store = get_object_or_404(Store, id=store_id, owner=request.user)
    form = forms.StoreForm(request.POST or None, instance=store)
    products = Product.objects.filter(store=store)

    # Update store
    if request.method == "POST" and form.is_valid():
        form.save()
        print("Edit store: Store updated")
        return redirect("vendor_dashboard")

    return render(request, 'store/edit_store.html', {
        'store': store,
        'products': products
    })
    

@vendor_required
def delete_store(request, store_id):

    store = get_object_or_404(Store, id=store_id, owner=request.user)

    # Delete store
    if request.method == "POST":
        store.delete()
        print("Delete store: Store deleted")
        return redirect("vendor_dashboard")
    
    return render(request, "store/delete_store.html", {"store": store})


@vendor_required
def add_product(request, store_id):

    # This is the view for adding a product
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    form = forms.ProductForm(request.POST or None)

    # Add product
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()

        # Create tweet
        tweet = Tweet()
        tweet.new_product_tweet = f"""A new product just arrived at {store.name}
        Check it out now!
        \nProduct Name: {product.name}
        \nDescription: {product.description}"""

        if product.image:
            tweet.new_product_tweet += f"\nImage: {product.image.url}"

        tweet_payload = {'text': tweet.new_product_tweet}
        try:
            Tweet._instance.make_tweet(tweet_payload)
        except Exception as e:
            print(f"Error sending tweet: {e}")

        print("Add product: Product created")

        return redirect("vendor_dashboard")
    return render(request, "store/add_product.html", {"form": form,
                                                      "store": store})


@vendor_required
def edit_product(request, product_id):

    # View for editing a product
    product = get_object_or_404(Product,
                                id=product_id, store__owner=request.user
                                )
    
    form = forms.ProductForm(request.POST or None, instance=product)

    # Update product
    if request.method == "POST" and form.is_valid():
        form.save()
        print("Edit product: Product updated")
        return redirect("vendor_dashboard")
    
    return render(request, "store/edit_product.html", {"form": form,
                                                       "product": product})


@vendor_required
def delete_product(request, product_id):

    # View for deleting a product
    product = get_object_or_404(Product,
                                id=product_id, store__owner=request.user
                                )

    # Delete product
    if request.method == "POST":
        product.delete()
        print("Delete product: Product deleted")
        return redirect("vendor_dashboard")
    
    return render(request, "store/delete_product.html",
                  {"product": product}
                  )


def home(request):
    # View for the home page
    # Get all products
    products = Product.objects.all()

    print("Home: Products retrieved")
    return render(request, "store/home.html", {
        "products": products
    })


def product_detail(request, product_id):

    # View for product detail
    product = get_object_or_404(Product, id=product_id)
    
    print("Product detail: Product retrieved")
    return render(request, "store/product_detail.html", {
        "product": product
    })


@buyer_required
def add_review(request, product_id):

    # View for adding a review
    product = get_object_or_404(Product, id=product_id)

    # Add review
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Check if user purchased this product
        has_bought = Order.objects.filter(
            user=request.user,
            products=product
        ).exists()

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
            verified=has_bought
        )
        print("Add review: Review created")
        return redirect("product_detail", product_id=product.id)
    return render(request, 'store/add_review.html', {'product': product})


@buyer_required
def add_to_cart(request, product_id):

    # Add product to cart
    cart = request.session.get("cart", {})
    quantity = request.POST.get("quantity", "1")

    if not quantity:
        quantity = "1"

    try:
        quantity = int(quantity)
    except ValueError:
        print("Add to cart: Invalid quantity")
        return redirect("view_cart")

    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    # Stock check
    product = Product.objects.get(id=product_id)

    if product.qty <= 0:
        messages.error(request, "This product is out of stock.")

    if cart[str(product_id)] > product.qty:
        cart[str(product_id)] = product.qty
        messages.warning(request, f"Only {product.qty} items available. Cart updated.")

    # Update session
    request.session["cart"] = cart
    print("Add to cart: Cart updated")
    return redirect("view_cart")


@buyer_required
def view_cart(request):

    # View for cart
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        product.quantity = qty
        product.subtotal = product.price * qty
        total += product.subtotal
        products.append(product)

    print("View cart: Cart retrieved")
    return render(request, "cart/view_cart.html", {
        "products": products,
        "total": total
    })


@buyer_required
# Checkout
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        print("Checkout: Cart is empty")
        return redirect("view_cart")

    order = Order.objects.create(user=request.user)

    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty
        )

    total = 0
    invoice_items = []
    
    # Calculate total
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * qty
        total += subtotal

        invoice_items.append(f"{product.name} x {qty} = {subtotal}")

    # Send email
    send_mail(
        subject="Your Invoice",
        message=f"Items:\n" + "\n".join(invoice_items) + f"\n\nTotal: {total}",
        from_email="your@email.com",
        recipient_list=[request.user.email],
    )
    
    Review.objects.filter(
        user=request.user,
        product__in=order.products.all(),
        verified=False
    ).update(verified=True)

    print("reviews verified: Reviews updated")

    # CLEAR SESSION CART
    request.session["cart"] = {}

    print("Checkout: Order created")
    return render(request, "cart/checkout_success.html", {"total": total})


# API's
@api_view(['GET'])
def api_reviews(request):
    product_id = request.GET.get('product')

    if product_id:
        reviews = Review.objects.filter(product_id=product_id)
    else:
        reviews = Review.objects.all()

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_vendor_stores(request):
    vendor_id = request.GET.get('vendor_id')
    
    if vendor_id:
        stores = Store.objects.filter(owner_id=vendor_id)
    else:
        # If no vendor specified, return all stores
        return Response(
            {"error": "Please provide vendor_id parameter"},
            status=400
        )
    
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_store_products(request):
    store_id = request.GET.get('store_id')
    
    if not store_id:
        return Response(
            {"error": "Please provide store_id parameter"},
            status=400
        )
    
    # Verify store exists
    if not Store.objects.filter(id=store_id).exists():
        return Response(
            {"error": "Store not found"},
            status=404
        )
    
    products = Product.objects.filter(store_id=store_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_add_product(request):

    store_id = request.data.get("store")

    # Check if store exists and user owns it
    try:
        store = Store.objects.get(id=store_id)
        if store.owner != request.user:
            return Response(
                {"error": "You do not own this store."},
                status=403
            )
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found."},
            status=404
        )

    serializer = ProductSerializer(data=request.data)
    # An API for adding a product
    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_add_review(request):

    # Check if product exists
    product_id = request.data.get("product")
    if not Product.objects.filter(id=product_id).exists():
        return Response(
            {"error": "Product not found."},
            status=404
        )
    
    # An API for adding a review
    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_add_store(request):

    serializer = StoreSerializer(data=request.data)

    # An API for adding a store

    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
