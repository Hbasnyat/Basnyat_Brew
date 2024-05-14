from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('location/', views.location_selection, name='location_selection'),
    path('drink/', views.drink_selection, name='drink_selection'),
    path('add-more-to-cart/<int:cart_item_id>/', views.add_more_to_cart, name='add_more_to_cart'),
    path('add-new-to-cart/<int:product_id>/', views.add_new_to_cart, name='add_new_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('select_quantity/<int:product_id>/',views.select_quantity, name='select_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('', views.home, name='home'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('subscribe_from_footer/', views.subscribe_from_footer, name='subscribe_from_footer'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path("password_reset/",auth_views.PasswordResetView.as_view(template_name='password_reset.html'),name='password_reset'),
    path('password_rest/done/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_email.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name="password_reset_complete"),
    path('rewards', views.Reward, name='rewards'),
    path('username/', views.username_view, name='username'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about_us, name='about'),
]