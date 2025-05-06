from django.shortcuts import render
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout

from django.conf import settings
from .models import Event, Category, Tag, Booking, UserProfile  # Import UserProfile
from .forms import EventForm, UserRegistrationForm, RegistrationForm, LoginForm  # Import all forms
from django.contrib.auth.models import User  # Import the User model

from django.urls import reverse
from .forms import RegistrationForm # Import your forms
from django.contrib import messages

from .forms import LoginForm  
import requests  # Import the requests library

# Ensure you have this setting in your Django settings.py
FLASK_API_BASE_URL = getattr(settings, 'FLASK_API_BASE_URL', 'http://flask-api:5000')
def event_list(request):
    events = Event.objects.all().order_by('-date')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'tags': tags
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})


# Add the map view
def event_map(request):
    """Render the event map page"""
    return render(request, 'events/event_map.html')

def events_json(request):
    """Return events data as JSON for the map"""
    events = Event.objects.all()
    events_data = []

    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'location': event.location,  # Only send the location name
            'start': event.date.isoformat(),
            'url': reverse('event_detail', args=[event.pk])
        })

    return JsonResponse(events_data, safe=False)

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})

@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Check if the user is the organizer
    if event.organizer != request.user:
        messages.error(request, "You can only edit events you've organized.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'event': event, 'action': 'Edit'})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Check if the user is the organizer
    if event.organizer != request.user:
        messages.error(request, "You can only delete events you've organized.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})

def event_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    events = Event.objects.filter(category=category).order_by('-date')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'tags': tags,
        'current_category': category
    })

def event_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    events = Event.objects.filter(tags=tag).order_by('-date')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'tags': tags,
        'current_tag': tag
    })

def event_search(request):
    query = request.GET.get('q', '')
    if query:
        events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        ).order_by('-date')
    else:
        events = Event.objects.all().order_by('-date')

    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'tags': tags,
        'search_query': query
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F, Sum
from .models import Event, Cart, CartItem, Booking

@login_required
def cart_view(request):
    """Display the user's cart"""
    # Get or create cart for this user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get all items in the cart
    cart_items = cart.items.all().select_related('event')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
    }
    
    return render(request, 'events/cart.html', context)

@login_required
def add_to_cart(request, event_id):
    """Add an event to the user's cart"""
    event = get_object_or_404(Event, pk=event_id)
    
    # Default value for attendees
    attendees = int(request.POST.get('attendees', 1))
    
    # Get or create cart for this user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if this event is already in cart
    cart_item = cart.items.filter(event=event).first()
    
    if cart_item:
        # Update attendees if item already exists
        cart_item.attendees += attendees
        cart_item.save()
        messages.success(request, f"Updated {event.title} in your cart.")
    else:
        # Create new cart item
        CartItem.objects.create(
            cart=cart,
            event=event,
            attendees=attendees
        )
        messages.success(request, f"Added {event.title} to your cart.")
    
    # Redirect based on the source
    next_url = request.POST.get('next', 'cart_view')
    
    if next_url == 'cart_view':
        return redirect('cart_view')
    else:
        return redirect('event_detail', pk=event_id)

@login_required
def update_cart_item(request, item_id):
    """Update the quantity of an item in cart"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        attendees = int(request.POST.get('attendees', 1))
        
        if attendees > 0:
            cart_item.attendees = attendees
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
            
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    event_title = cart_item.event.title
    cart_item.delete()
    
    messages.success(request, f"Removed {event_title} from your cart.")
    return redirect('cart_view')

@login_required
def cart_checkout(request):
    """Process book from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    
    # Check if cart is empty
    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')
    
    # Process all items in cart
    cart_items = cart.items.all().select_related('event')
    total_amount = cart.get_total_price()
    
    # Calculate total attendees
    total_attendees = cart_items.aggregate(total=Sum('attendees'))['total'] or 0
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'total_attendees': total_attendees,
    }
    
    return render(request, 'events/cart_checkout.html', context)

@login_required
def process_cart_checkout(request):
    """Complete the booking process"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all().select_related('event')
        
        # Get payment method
        payment_method = request.POST.get('payment_method', 'pay_later')
        payment_status = 'PENDING'
        
        # If online payment is selected, you could integrate with a payment gateway here
        if payment_method == 'pay_online':
            # This would be where you'd implement payment gateway logic
            # For now, we'll just mark it as pending
            payment_status = 'PENDING'
        
        # Create bookings for each item in cart
        bookings = []
        for item in cart_items:
            # Get user profile for user info
            try:
                user_profile = request.user.profile
                name = user_profile.full_name
                phone = user_profile.mobile_number
            except:
                name = request.user.username
                phone = ""
            
            # Create booking for this cart item
            booking = Booking.objects.create(
                event=item.event,
                name=name,
                user=request.user,
                user_email=request.user.email,
                user_phone=phone,
                user_attendees=item.attendees,
                user_column="N/A",  # These will be set in the booking view
                user_seat="N/A",    # These will be set in the booking view
                payment_status=payment_status,
                booking_status='BOOKED'
            )
            bookings.append(booking)
        
        # Clear the cart after checkout
        cart.items.all().delete()
        
        messages.success(request, "Please complete your bookings.")
        
        # If just one booking, go directly to that booking page
        if len(bookings) == 1:
            return redirect('booking', event_id=bookings[0].event.id)
        
        return redirect('my_tickets')
    
    return redirect('cart_view')


def django_login_view(request, role):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            flask_login_url = f"{FLASK_API_BASE_URL}/api/login"  # Added /api prefix
            data = {'email': email, 'password': password, 'role': role} # Sending role to Flask

            try:
                response = requests.post(flask_login_url, json=data)
                response.raise_for_status()
                flask_data = response.json()
                if flask_data.get('message') == 'Login successful!':
                    user_id = flask_data.get('user_id')
                    user_role = flask_data.get('role')
                    try:
                        # Assuming you might want to create/update a local Django user
                        # based on the Flask API response. Adjust this logic as needed.
                        user, created = User.objects.get_or_create(username=email, email=email)
                        # Optionally update user profile with role if you have a UserProfile model
                        if hasattr(user, 'userprofile'):
                            user.userprofile.role = user_role
                            user.userprofile.save()
                        django_login(request, user)
                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        return redirect('event_list')
                    except Exception as e:
                        messages.error(request, f"Error handling login response: {e}")
                        return render(request, 'home/login.html', {'form': form, 'role': role})
                else:
                    messages.error(request, flask_data.get('error', 'Login failed from API.'))
                    return render(request, 'home/login.html', {'form': form, 'role': role})
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to Flask API: {e}")
                return render(request, 'home/login.html', {'form': form, 'role': role})
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'home/login.html', {'form': form, 'role': role})
    else:
        form = LoginForm()
        return render(request, 'home/login.html', {'form': form, 'role': role})

def django_register_view(request, role):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            mobile = form.cleaned_data['mobile']

            flask_register_url = f"{FLASK_API_BASE_URL}/api/register" # Added /api prefix
            data = {'name': name, 'email': email, 'password': password, 'confirm_password': form.cleaned_data['confirm_password'], 'mobile': mobile, 'role': role}

            try:
                response = requests.post(flask_register_url, json=data)
                response.raise_for_status()
                flask_data = response.json()
                if flask_data.get('message') == 'Registration successful! Please log in.':
                    messages.success(request, 'Account created successfully! Please log in.')
                    return redirect(reverse('login', kwargs={'role': role}))
                else:
                    messages.error(request, flask_data.get('error', 'Registration failed from API.'))
                    return render(request, 'home/register.html', {'form': form, 'selected_role': role})
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to Flask API: {e}")
                return render(request, 'home/register.html', {'form': form, 'selected_role': role})
        else:
            return render(request, 'home/register.html', {'form': form, 'selected_role': role})
    else:
        form = RegistrationForm(initial={'role': role})
        return render(request, 'home/register.html', {'form': form, 'selected_role': role})

@login_required
def booking_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user
    
    try:
        user_profile = UserProfile.objects.get(user=user)
        initial_data = {
            'name': user_profile.full_name,
            'user_email': user.email,
            'user_phone': user_profile.mobile_number,
        }
    except UserProfile.DoesNotExist:
        initial_data = {
            'name': user.get_full_name() or user.username,
            'user_email': user.email,
            'user_phone': '',
        }
    
    if request.method == 'POST':
        attendees = request.POST.get('user_attendees')
        column = request.POST.get('user_column')
        seat = request.POST.get('user_seat')
        special_request = request.POST.get('user_request', '')
        
        if not attendees or not column or not seat:
            messages.error(request, "Please fill all required fields.")
            return render(request, 'events/booking.html', {'event': event, 'initial_data': initial_data})
        
        booking = Booking(
            event=event,
            name=initial_data['name'],
            user=user,  # Associate the booking with the logged-in user
            user_email=initial_data['user_email'],
            user_phone=initial_data['user_phone'],
            user_attendees=attendees,
            user_column=column,
            user_seat=seat,
            user_request=special_request,
            payment_status='PENDING',
            booking_status='BOOKED'
        )
        booking.save()
        
        return redirect('payment', booking_id=booking.id)
    
    return render(request, 'events/booking.html', {'event': event, 'initial_data': initial_data})

def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    event = booking.event
    
    price_per_ticket = event.price 
    total_amount = price_per_ticket * int(booking.user_attendees)
    
    context = {
        'booking': booking,
        'event': event,
        'total_amount': total_amount
    }
    return render(request, 'events/payment.html', context)

def send_confirmation_email(booking):
    """Send confirmation email to user"""
    subject = f"Confirmation: Your tickets for {booking.event.title}"
    message = f"""
    Congratulations,
    
    Your tickets are booked for the event {booking.event.title}. Enjoy!!!!
    
    Booking Details:
    - Event: {booking.event.title}
    - Date: {booking.event.date}
    - Number of Attendees: {booking.user_attendees}
    - Seat: Column {booking.user_column}, Seat {booking.user_seat}
    - Booking ID: {booking.id}
    
    Thank you for booking with Eventora.
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.user_email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"Email sent successfully to {booking.user_email} for booking {booking.id}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_cancellation_email(booking):
    """Send cancellation email to user"""
    subject = f"Cancellation Confirmation: {booking.event.title}"
    message = f"""
    Hello {booking.name},
    
    Your booking for {booking.event.title} has been successfully cancelled.
    
    Cancellation Details:
    - Event: {booking.event.title}
    - Date: {booking.event.date}
    - Number of Attendees: {booking.user_attendees}
    - Booking ID: {booking.id}
    
    Refund:
    Your payment of ${booking.total_amount()} will be refunded to your original payment method within 7-10 business days.
    
    If you have any questions, please contact our support team.
    
    Thank you for using Eventora.
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.user_email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"Cancellation email sent successfully to {booking.user_email} for booking {booking.id}")
        return True
    except Exception as e:
        print(f"Error sending cancellation email: {e}")
        return False

def confirm_payment(request, event_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=event_id)
        
        booking.payment_status = 'PAID'
        booking.save()
        
        email_sent = send_confirmation_email(booking)
        
        if email_sent:
            messages.success(request, "Payment confirmed! A confirmation email has been sent to your email address.")
        else:
            messages.warning(request, "Payment confirmed! However, there was an issue sending the confirmation email.")
        
        context = {
            'booking': booking,
            'event': booking.event,
            'email_sent': email_sent
        }
        
        return render(request, 'events/payment_confirmation.html', context)
    
    return redirect('event_list')


from django.utils import timezone

@login_required
def my_tickets(request):
    """Display all bookings for the logged-in user"""
    user = request.user
    
    # Get all bookings for this user
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')
    
    # Split bookings based on status and date
    upcoming_bookings = []
    past_bookings = []
    cancelled_bookings = []
    current_time = timezone.now()
    
    for booking in bookings:
        if booking.booking_status == 'CANCELLED':
            cancelled_bookings.append(booking)
        elif booking.event.date < current_time:
            past_bookings.append(booking)
        else:
            upcoming_bookings.append(booking)
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    
    return render(request, 'events/my_tickets.html', context)

@login_required 
def cancel_ticket(request, booking_id):
    """Cancel a booking/ticket"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if the booking can be cancelled (1 day before event)
    if not booking.can_cancel():
        messages.error(request, "Sorry, tickets can only be cancelled at least 1 day before the event.")
        return redirect('my_tickets')
    
    if request.method == 'POST':
        # Mark booking as cancelled
        booking.booking_status = 'CANCELLED'
        booking.payment_status = 'CANCELLED'
        booking.save()
        
        # Send cancellation email
        email_sent = send_cancellation_email(booking)
        
        if email_sent:
            messages.success(request, "Your booking has been cancelled successfully. A confirmation email has been sent.")
        else:
            messages.success(request, "Your booking has been cancelled successfully. However, there was an issue sending the confirmation email.")
        
        return redirect('my_tickets')
    
    return render(request, 'events/cancel_ticket.html', {'booking': booking})

def payment_expired(request):
    return render(request, 'events/payment_expired.html')

def index(request):
    return render(request, 'home/index.html')

from django.contrib import messages

def my_view(request):
    messages.success(request, "Your action was successful!")  # Shortcut for a success message
    messages.warning(request, "Something might be wrong.")
    messages.error(request, "An error occurred.")
    messages.info(request, "Here is some information.")
    
def help_center_view(request):
    featured_articles_data = [
        {'title': 'How to buy tickets'},
        {'title': 'Joining an online event'},
        {'title': 'What to do if an event is canceled'},
        {'title': 'Finding event details'},
        {'title': 'Using promo codes'},
        {'title': 'Managing your bookings'},
    ]
    context = {'featured_articles': featured_articles_data}
    return render(request, 'home/help_center.html', context)


def create_event(request):
    return render(request, 'home/create_event.html')

def find_events_view(request):
    return render(request, 'home/find_events.html')

def about_view(request):
    team_members = [
        {
            'name': 'John Smith',
            'description': 'CEO',
            'education': 'MBA, Harvard University',
            'skills': 'Leadership, Strategy, Management',
            'language': {'hindi': 90, 'english': 100},
            'image_path': 'images/john_smith.jpg',  
        },
        {
            'name': 'Jane Doe',
            'description': 'CTO',
            'education': 'Ph.D. in Computer Science, MIT',
            'skills': 'Software Development, AI, Cloud Computing',
            'language': {'hindi': 60, 'english': 100},
            'image_path': 'images/jane_doe.jpg',
        },
        {
            'name': 'David Lee',
            'description': 'Marketing Director',
            'education': 'BS in Marketing, Stanford University',
            'skills': 'Marketing Strategy, Digital Marketing, Communications',
            'language': {'hindi': 70, 'english': 95},
            'image_path': 'images/david_lee.jpg',
        },
    ]
    return render(request, 'home/about.html', {'team_members': team_members})
def contact_view(request):
    return render(request, 'home/contact.html')

from django.urls import reverse
from .forms import RegistrationForm 
from django.contrib import messages

from .forms import LoginForm  

def login_view(request, role):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password) 
            if user is not None:
                login(request, user)
                return redirect('event_list') 
            else:
                messages.error(request, "Invalid email or password.")
                return render(request, 'home/login.html', {'form': form, 'role': role})
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'home/login.html', {'form': form, 'role': role})  
    else:
        form = LoginForm()  
        return render(request, 'home/login.html', {'form': form, 'role': role})

def register_view(request, role):
    print(f"Signup Role: {role}")
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            mobile = form.cleaned_data['mobile']
            print(f"Name: {name}, Email: {email}, Password: {password}, Mobile: {mobile}, Role: {role}")

            if User.objects.filter(username=email).exists():
                messages.error(request, "An account with this email address already exists. Please log in.")
                return render(request, 'home/register.html', {'form': form, 'selected_role': role})
            else:
                user = User.objects.create_user(username=email, email=email, password=password)
                UserProfile.objects.create(user=user, full_name=name, mobile_number=mobile, role=role)
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect(reverse('login', kwargs={'role': role})) # Pass role
        else:
            return render(request, 'home/register.html', {'form': form, 'selected_role': role})
    else:
        form = RegistrationForm(initial={'role': role})
        return render(request, 'home/register.html', {'form': form, 'selected_role': role})


FLASK_API_BASE_URL = "http://127.0.0.1:5000"  # Adjust as needed

def help_center_list(request):
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/featured_articles")
        response.raise_for_status()
        featured_articles = response.json()
        return render(request, 'home/integrated_help/help_center_list.html', {'featured_articles': featured_articles})
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch help data: {e}"
        return render(request, 'home/integrated_help/error.html', {'error_message': error_message})

def help_center_detail(request, item_id):
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/help_center/{item_id}") # Or your specific endpoint
        response.raise_for_status()
        help_item = response.json()
        return render(request, 'home/integrated_help/help_detail.html', {'help_item': help_item})
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch help item details: {e}"
        return render(request, 'home/integrated_help/error.html', {'error_message': error_message})
    except ValueError:
        error_message = "Invalid help item ID."
        return render(request, 'home/integrated_help/error.html', {'error_message': error_message})

def integrated_help_center(request):
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/help")
        response.raise_for_status()
        flask_help_content = response.text
        return render(request, 'home/integrated_help/help_center.html', {'flask_help_content': flask_help_content})
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch help center data from Flask: {e}"
        return render(request, 'home/integrated_help/error.html', {'error_message': error_message})
def django_logout_view(request):
    django_logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home') 
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        return redirect('home/submit_contact')
    return render(request, 'home/contact.html')




def submit_contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        flask_url = 'http://127.0.0.1:5000/api/contact'
        try:
            response = requests.post(
                flask_url,
                json={'name': name, 'email': email, 'message': message},  # <-- use json=
                timeout=5  # optional: avoids hanging
            )

            if response.status_code == 200:
                return render(request, 'home/submit_contact.html', {'message': 'Thank you! Your message has been sent.'})
            else:
                print("Flask error response:", response.text)
                return JsonResponse({"error": "Failed to submit the form."}, status=500)

        except Exception as e:
            print("Connection error:", e)
            return JsonResponse({"error": "Connection to Flask API failed."}, status=500)

    return render(request, 'home/contact.html')