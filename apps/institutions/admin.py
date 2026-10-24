from django.contrib import admin

from .models import Campus, EmailDomain, HostRole, Hub, University, Venue


class EmailDomainInline(admin.TabularInline):
    model = EmailDomain
    extra = 0


class CampusInline(admin.TabularInline):
    model = Campus
    extra = 0
    fields = ("name", "short_code", "city")


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("short_code", "name", "is_active")
    search_fields = ("short_code", "name")
    inlines = (EmailDomainInline, CampusInline)


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "university", "short_code", "city")
    list_filter = ("university",)


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "city")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "campus", "hub", "capacity")


@admin.register(HostRole)
class HostRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "campus", "hub", "granted_by", "granted_at")
    list_filter = ("role",)
    autocomplete_fields = ("user",)
    readonly_fields = ("granted_by", "granted_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
