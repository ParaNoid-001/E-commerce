from django.contrib import admin

# Register your models here.
from .models import Contact
from django.utils.html import format_html

class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'message_preview', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at')
    date_hierarchy = 'created_at'

    def phone(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)
    phone.short_description = 'Phone'
    
    def message_preview(self, obj):
        return format_html(
            '<span style="max-width: 200px; display: inline-block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{}</span>',
            obj.message
        )
    message_preview.short_description = 'Message'
    
admin.site.register(Contact, ContactAdmin)