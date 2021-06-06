from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from members.models import Membership, User
from members.utils import is_admin, is_security_officer


class MembershipInline(admin.StackedInline):
    model = Membership


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    inlines = [MembershipInline]

    def has_view_permission(self, request, obj=None):
        return is_admin(request.user) or is_security_officer(request.user)

    def has_change_permission(self, request, obj=None):
        return is_security_officer(request.user)

    def has_add_permission(self, request):
        return is_security_officer(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_security_officer(request.user)
