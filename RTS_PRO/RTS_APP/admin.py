from django.contrib import admin, messages
from django.utils.html import format_html
from .models import User, Resume, Score, Job, ScoringCriteria, ResumeHistory
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    
    model=User
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    def role(self, obj):
        return obj.role
    role.admin_order_field = 'role'  # Allows column order sorting
    role.short_description = 'Role'  # Column header name

    def delete_model(self, request, obj):
        if obj.is_superuser:
            self.message_user(request, "You cannot delete a superuser.", level=messages.ERROR)
        else:
            super().delete_model(request, obj)

admin.site.register(User, CustomUserAdmin)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'provider_link', 'description_short', 'postDate', 'seats', 'is_closed')
    list_editable = ('seats', 'is_closed')
    search_fields = ('title', 'description', 'provider__username')
    list_filter = ('postDate', 'is_closed', 'provider')
    ordering = ('-postDate',)

    def provider_link(self, obj):
        url = f'/admin/yourapp/user/{obj.provider.id}/change/'  # Adjust 'yourapp' as per your app name
        return format_html('<a href="{}">{}</a>', url, obj.provider.username)
    provider_link.short_description = 'Provider'

    def description_short(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    description_short.short_description = 'Description'


class ScoreInline(admin.StackedInline):
    model = Score
    extra = 0
    readonly_fields = ('score', 'feedback')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'job_link', 'resume_file_link', 'uploadDate', 'status')
    search_fields = ('user__username', 'job__title')
    list_filter = ('uploadDate', 'status', 'job')
    inlines = [ScoreInline]
    ordering = ('-uploadDate',)
    readonly_fields = ('uploadDate',)

    def user_link(self, obj):
        url = f'/admin/yourapp/user/{obj.user.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def job_link(self, obj):
        url = f'/admin/yourapp/job/{obj.job.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    job_link.short_description = 'Job'

    def resume_file_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.resume.url)
        return "-"
    resume_file_link.short_description = 'Resume File'


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume_link', 'score', 'feedback')
    list_editable = ('score', 'feedback')
    search_fields = ('resume__user__username', 'resume__job__title')
    list_filter = ('score',)

    def resume_link(self, obj):
        url = f'/admin/yourapp/resume/{obj.resume.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, str(obj.resume))
    resume_link.short_description = 'Resume'


@admin.register(ScoringCriteria)
class ScoringCriteriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_link', 'keyword', 'weight')
    search_fields = ('keyword', 'job__title')
    list_filter = ('job',)

    def job_link(self, obj):
        url = f'/admin/yourapp/job/{obj.job.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    job_link.short_description = 'Job'


@admin.register(ResumeHistory)
class ResumeHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume_link', 'viewed_by_link', 'viewed_at')
    search_fields = ('resume__user__username', 'viewed_by__username')
    list_filter = ('viewed_at', 'viewed_by')
    ordering = ('-viewed_at',)

    def resume_link(self, obj):
        url = f'/admin/yourapp/resume/{obj.resume.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, str(obj.resume))
    resume_link.short_description = 'Resume'

    def viewed_by_link(self, obj):
        url = f'/admin/yourapp/user/{obj.viewed_by.id}/change/'  # Adjust 'yourapp'
        return format_html('<a href="{}">{}</a>', url, obj.viewed_by.username)
    viewed_by_link.short_description = 'Viewed By'

