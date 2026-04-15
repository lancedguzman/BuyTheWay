from django.contrib import admin
from .models import Group, GroupMember


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 0
    readonly_fields = ('joined_at', 'order')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product',
                    'creator', 'target_size',
                    'member_count', 'status',
                    'created_at')
    list_filter = ('status',)
    readonly_fields = ('invite_token', 'created_at')
    inlines = [GroupMemberInline]

    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.member_count


class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group',
                    'buyer', 'quantity',
                    'address', 'order',
                    'joined_at')
    readonly_fields = ('joined_at',)

admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(Group, GroupAdmin)