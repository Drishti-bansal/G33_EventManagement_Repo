from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Categories"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title

from django.core.validators import MinLengthValidator

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_price() for item in self.items.all())
    
    def get_item_count(self):
        """Get number of items in cart"""
        return self.items.count()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendees = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event.title} - {self.attendees} attendees"
    
    def get_price(self):
        """Calculate price for this cart item"""
        return self.event.price * self.attendees

class Booking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    members = models.IntegerField(null=True, blank=True)
    special = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)
    
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )
    
    BOOKING_STATUS_CHOICES = (
        ('BOOKED', 'Booked'),
        ('ATTENDED', 'Attended'),
        ('CANCELLED', 'Cancelled'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=15, validators=[MinLengthValidator(10)])
    user_attendees = models.PositiveIntegerField(null=True, blank=True)
    user_column = models.CharField(max_length=10, blank=True)
    user_seat = models.CharField(max_length=10, null=True)
    user_request = models.TextField(blank=True, null=True)
    booking_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    booking_status = models.CharField(max_length=10, choices=BOOKING_STATUS_CHOICES, default='BOOKED')

    def __str__(self):
        return f"{self.name} - {self.event.title}"
    
    def can_cancel(self):
        """Check if the booking can be cancelled (one day before the event)"""
        return self.event.date > timezone.now() + timedelta(days=1)
    
    def total_amount(self):
        """Calculate the total amount paid for the booking"""
        return self.event.price * (self.user_attendees or 0)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    booking_data = models.JSONField()  # To store booking data temporarily
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    role = models.CharField(max_length=20)
    # Add other fields as needed

    def __str__(self):
        return self.user.username