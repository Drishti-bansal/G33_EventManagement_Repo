from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, Category, Location, Tag
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seed the database with sample events'

    def handle(self, *args, **kwargs):
        if Event.objects.exists():
            self.stdout.write(self.style.WARNING('Events already exist. Skipping seeding.'))
            return

        user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'password': 'admin'})
        category, _ = Category.objects.get_or_create(name='Technology')
        location, _ = Location.objects.get_or_create(
            name='Innovation Hub',
            address='456 Future Blvd',
            city='Metropolis',
            state='Progressia',
            country='Techland'
        )

        tag_names = ['AI', 'Web3', 'Data Science', 'DevOps', 'Cloud']
        tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]

        now = timezone.now()
        sample_titles = [
            'Future Tech Conference',
            'DevOps Mastery Workshop',
            'AI & Ethics Forum',
            'Cloud Native Days',
            'Data Analytics Bootcamp',
            'Cybersecurity Essentials',
            'Machine Learning 101',
            'Startup Pitch Night'
        ]

        for i, title in enumerate(sample_titles):
            is_free = random.choice([True, False])
            price = 0.00 if is_free else round(random.uniform(10, 100), 2)

            event = Event.objects.create(
                title=title,
                description=f"{title} is a premier event in the field.",
                short_description=f"Join us for {title}.",
                start_date=now + timedelta(days=5 + i * 3),
                end_date=now + timedelta(days=6 + i * 3),
                image=f"events/default_event_{i%3+1}.jpg",
                banner_image=f"events/banners/default_banner_{i%3+1}.jpg",
                organizer=user,
                category=category,
                location=location,
                capacity=200,
                price=price,
                is_free=is_free,
                registration_deadline=now + timedelta(days=4 + i * 3),
                status='upcoming',
                featured=bool(i % 2),
                website='https://example.com',
                contact_email='info@example.com',
                contact_phone='+1234567890',
            )
            event.tags.set(random.sample(tags, k=random.randint(1, 3)))
            event.save()

        self.stdout.write(self.style.SUCCESS('✅ Multiple sample events created successfully!'))
