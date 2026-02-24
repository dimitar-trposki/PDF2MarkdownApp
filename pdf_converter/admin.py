from django.contrib import admin
from .models import OriginalModelOutput, UserChangedText


@admin.register(OriginalModelOutput)
class OriginalModelOutputAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'text_preview')
    list_filter = ('model',)
    search_fields = ('model', 'text')
    readonly_fields = ('id',)

    def text_preview(self, obj):

        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(UserChangedText)
class UserChangedTextAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_output', 'text_preview')
    search_fields = ('text',)
    readonly_fields = ('id',)

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'
