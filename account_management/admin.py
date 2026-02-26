from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    # The columns that will be displayed in the admin list view
    list_display = (
        'email', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'gender', 
        'image_preview'
    )
    
    # Adds a search bar to search by these specific fields
    search_fields = ('email', 'first_name', 
                     'last_name', 'phone_number')
    
    # Adds a filter sidebar to filter users by gender
    list_filter = ('gender',)
    
    # Orders the records alphabetically by email by default
    ordering = ('email',)

    # Custom method to display a thumbnail of the profile picture
    def image_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', 
                obj.profile_picture.url
            )
        return "No Image"
    
    # Sets the column name for the custom method in the admin panel
    image_preview.short_description = 'Profile Picture'


admin.site.register(UserProfile, UserProfileAdmin)
