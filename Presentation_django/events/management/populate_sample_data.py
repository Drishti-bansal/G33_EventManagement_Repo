from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Category, Tag, Event
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **kwargs):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
            self.stdout.write(self.style.SUCCESS('Superuser created'))
        
        # Create some regular users
        user_names = ['john', 'sarah', 'michael', 'emma', 'david']
        users = []
        
        for name in user_names:
            if not User.objects.filter(username=name).exists():
                user = User.objects.create_user(
                    username=name,
                    email=f'{name}@example.com',
                    password=f'{name}password'
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'User {name} created'))
            else:
                users.append(User.objects.get(username=name))
        
        # Create categories
        categories_data = [
            {'name': 'Conference', 'description': 'Professional gatherings for networking and learning'},
            {'name': 'Workshop', 'description': 'Hands-on sessions to develop skills'},
            {'name': 'Seminar', 'description': 'Educational events with expert speakers'},
            {'name': 'Concert', 'description': 'Live music performances'},
            {'name': 'Exhibition', 'description': 'Displays of art, products, or information'},
            {'name': 'Social', 'description': 'Casual gatherings for socializing'},
            {'name': 'Sports', 'description': 'Athletic events and competitions'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category {category.name} created'))
        
        # Create tags
        tags_data = [
            'Technology', 'Business', 'Education', 'Art', 'Music', 'Science', 
            'Health', 'Culture', 'Food', 'Fashion', 'Environment', 'Politics',
            'Networking', 'Career', 'Personal Development', 'Innovation'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Tag {tag.name} created'))
        
        # Create events
        events_data = [
            {
                'title': 'Annual Tech Conference',
                'description': 'Join us for the biggest tech conference of the year, featuring keynotes from industry leaders, workshops, and networking opportunities.',
                'days_from_now': 30,
                'location': 'Convention Center, New York',
                'category': 'Conference',
                'tags': ['Technology', 'Networking', 'Innovation'],
            },
            {
                'title': 'Web Development Workshop',
                'description': 'A hands-on workshop to learn the latest web development techniques and frameworks.',
                'days_from_now': 14,
                'location': 'Tech Hub, San Francisco',
                'category': 'Workshop',
                'tags': ['Technology', 'Education', 'Career'],
            },
            {
                'title': 'Business Leadership Seminar',
                'description': 'Learn effective leadership strategies from experienced business executives.',
                'days_from_now': 21,
                'location': 'Business Center, Chicago',
                'category': 'Seminar',
                'tags': ['Business', 'Career', 'Personal Development'],
            },
            {
                'title': 'Classical Music Concert',
                'description': 'An evening of classical masterpieces performed by the Symphony Orchestra.',
                'days_from_now': 10,
                'location': 'Concert Hall, Boston',
                'category': 'Concert',
                'tags': ['Music', 'Culture', 'Art'],
            },
            {
                'title': 'Modern Art Exhibition',
                'description': 'Explore contemporary art pieces from emerging artists around the world.',
                'days_from_now': 5,
                'location': 'Art Gallery, Los Angeles',
                'category': 'Exhibition',
                'tags': ['Art', 'Culture'],
            },
            {
                'title': 'Networking Mixer',
                'description': 'Connect with professionals from various industries in a casual setting.',
                'days_from_now': 7,
                'location': 'The Grand Hotel, Miami',
                'category': 'Social',
                'tags': ['Networking', 'Business', 'Career'],
            },
            {
                'title': 'Health and Wellness Fair',
                'description': 'Discover the latest in health, fitness, and wellness products and services.',
                'days_from_now': 15,
                'location': 'Community Center, Seattle',
                'category': 'Exhibition',
                'tags': ['Health', 'Personal Development'],
            },
            {
                'title': 'Environmental Sustainability Conference',
                'description': 'Join experts and activists to discuss solutions for a sustainable future.',
                'days_from_now': 45,
                'location': 'Green Building, Portland',
                'category': 'Conference',
                'tags': ['Environment', 'Science', 'Education'],
            },
            {
                'title': 'Food Festival',
                'description': 'Taste culinary delights from local restaurants and food vendors.',
                'days_from_now': 12,
                'location': 'City Park, Austin',
                'category': 'Social',
                'tags': ['Food', 'Culture'],
            },
            {
                'title': 'Charity Basketball Tournament',
                'description': 'Watch exciting basketball games while supporting a good cause.',
                'days_from_now': 18,
                'location': 'Sports Arena, Houston',
                'category': 'Sports',
                'tags': ['Sports', 'Health'],
            },
        ]
        
        # Create events
        events_count = 0
        for event_data in events_data:
            # Find category
            category = next((c for c in categories if c.name == event_data['category']), None)
            if not category:
                continue
                
            # Calculate date
            event_date = timezone.now() + timedelta(days=event_data['days_from_now'])
            
            # Select random organizer
            organizer = random.choice(users)
            
            # Create event if it doesn't exist
            if not Event.objects.filter(title=event_data['title'], date=event_date).exists():
                event = Event.objects.create(
                    title=event_data['title'],
                    description=event_data['description'],
                    date=event_date,
                    location=event_data['location'],
                    organizer=organizer,
                    category=category
                )
                
                # Add tags
                for tag_name in event_data['tags']:
                    tag = next((t for t in tags if t.name == tag_name), None)
                    if tag:
                        event.tags.add(tag)
                
                events_count += 1
                self.stdout.write(self.style.SUCCESS(f'Event "{event.title}" created'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {events_count} events'))