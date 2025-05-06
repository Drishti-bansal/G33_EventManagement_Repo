from .models import Category, Tag

def common_data(request):
    """
    Adds commonly used data to the context of all templates
    """
    return {
        'all_categories': Category.objects.all(),
        'all_tags': Tag.objects.all()[:15],  
    }