from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Existing URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('booking/<int:event_id>/', views.booking_view, name='booking'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:event_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('cart/checkout/process/', views.process_cart_checkout, name='process_cart_checkout'),


    # path('login/<str:role>/', views.login_view, name='login'),
    # path('register/<str:role>/', views.register_view, name='register'),
    path('event_list/', views.event_list, name='event_list'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/new/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('category/<int:category_id>/', views.event_by_category, name='event_by_category'),
    path('tag/<int:tag_id>/', views.event_by_tag, name='event_by_tag'),
    path('search/', views.event_search, name='event_search'),
    path('map/', views.event_map, name='event_map'),
    path('events-json/', views.events_json, name='events-json'),
    
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('events/booking/<int:event_id>/', views.booking_view, name='booking'),
    path('process_booking/<int:event_id>/', views.booking_view, name='process_booking'),
    path('events/payment/<int:booking_id>/', views.payment_view, name='payment'),
    path('events/confirm_payment/<int:event_id>/', views.confirm_payment, name='confirm_payment'),
    path('events/payment_expired/', views.payment_expired, name='payment_expired'),
    
    # New URLs for ticket management
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('cancel-ticket/<int:booking_id>/', views.cancel_ticket, name='cancel_ticket'),
    
    path('', views.index, name='index'),
    
    path('create/', views.create_event, name='create_event'),
    path('find/', views.find_events_view, name='find_events'),
   
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

     path('help/', views.help_center_list, name='help_center_list'),
    path('help/<int:item_id>/', views.help_center_detail, name='help_center_detail'),
    path('integrated-help/', views.integrated_help_center, name='integrated_help_center'), 


     path('login/<str:role>/', views.django_login_view, name='login'),  # Expect a string for role
    path('register/<str:role>/', views.django_register_view, name='register'), 
    path('logout/', views.django_logout_view, name='logout'),# Added missing comma
    path('submit_contact/', views.submit_contact_view, name='submit_contact'),
]