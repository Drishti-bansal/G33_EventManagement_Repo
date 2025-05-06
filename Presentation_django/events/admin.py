from django.contrib import admin
from django.contrib import admin
from .models import Event, Category, Tag, Booking

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer', 'category')
    list_filter = ('date', 'category', 'tags')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Event, EventAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)



class Bookingpage(admin.ModelAdmin):
    list_display=['name','email','created_at']
admin.site.register(Booking,Bookingpage)