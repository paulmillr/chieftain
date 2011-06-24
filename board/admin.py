from django.contrib import admin
from board import models


class ThreadAdmin(admin.ModelAdmin):
    """Admin controller for threads."""
    exclude = ("html",)


class PostAdmin(admin.ModelAdmin):
    search_fields = ("pid", "thread__section__slug")
    exclude = ("html", "is_op_post")


class DeniedIPAdmin(admin.ModelAdmin):
    search_fields = ("ip",)

admin.site.register(models.Thread, ThreadAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.File)
admin.site.register(models.FileTypeGroup)
admin.site.register(models.FileType)
admin.site.register(models.Section)
admin.site.register(models.SectionGroup)
admin.site.register(models.UserProfile)
admin.site.register(models.Wordfilter)
admin.site.register(models.DeniedIP, DeniedIPAdmin)
