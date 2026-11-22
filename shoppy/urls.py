from django.urls import path
from django.contrib.auth import views as auth_views
from shoppy import views


urlpatterns = [

    # API
    path('api/products/add/', views.api_add_product, name='api_add_product'),
    path('api/vendor-stores/', views.api_vendor_stores, name='api_vendor_stores'),
    path('api/stores/add/', views.api_add_store, name='api_add_store'),
    path('api/products/', views.api_store_products, name='api_store_products'),
    path('api/reviews/', views.api_reviews, name='api_reviews'),
    path('api/reviews/add/', views.api_add_review, name='api_add_review'),

    # Home
    path('', views.home, name='home'),

    # Signup
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    
    # Store management
    path('store/create/', views.create_store, name='create_store'),
    path('store/<int:store_id>/edit/', views.edit_store, name='edit_store'),
    path('store/<int:store_id>/product/add/', views.add_product, name='add_product'),
    path('store/<int:store_id>/delete/', views.delete_store, name='delete_store'),

    # Products
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    
    # Reviews
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
