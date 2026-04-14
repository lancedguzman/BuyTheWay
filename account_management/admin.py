from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import UserProfile, SellerIDVerification


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


@admin.register(SellerIDVerification)
class SellerIDVerificationAdmin(admin.ModelAdmin):
    list_display = ('seller_email', 'get_id_type_display',
                    'status', 'submitted_at',
                    'reviewed_at', 'id_photo_preview',
                    'selfie_preview')
    list_filter = ('status', 'id_type')
    search_fields = ('seller__email', 'seller__first_name', 
                     'seller__last_name')
    readonly_fields = ('seller', 'id_type',
                       'id_photo_preview', 'selfie_preview',
                       'submitted_at')
    fields = ('seller', 'id_type',
              'id_photo_preview', 'selfie_preview',
              'status', 'reviewer_notes',
              'submitted_at', 'reviewed_at')
    ordering = ('-submitted_at',)
    actions = ['approve_submissions', 'reject_submissions']

    def seller_email(self, obj):
        return obj.seller.email
    seller_email.short_description = 'Seller'

    def get_id_type_display(self, obj):
        return obj.get_id_type_display()
    get_id_type_display.short_description = 'ID Type'

    def id_photo_preview(self, obj):
        if obj.id_photo:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:80px; border-radius:4px;" />'
                '</a>',
                obj.id_photo.url, obj.id_photo.url
            )
        return '—'
    id_photo_preview.short_description = 'ID Photo'

    def selfie_preview(self, obj):
        if obj.selfie_with_id:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:80px; border-radius:4px;" />'
                '</a>',
                obj.selfie_with_id.url, obj.selfie_with_id.url
            )
        return '—'
    selfie_preview.short_description = 'Selfie with ID'

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description='Approve selected submissions')
    def approve_submissions(self, request, queryset):
        updated = queryset.update(status='approved', reviewed_at=timezone.now())
        self.message_user(request, f'{updated} submission(s) approved.')

    @admin.action(description='Reject selected submissions')
    def reject_submissions(self, request, queryset):
        updated = queryset.update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f'{updated} submission(s) rejected.')
