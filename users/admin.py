from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import Department, Cluster, Team

# - CustomUser page ------------------------------------------------

CustomUser = get_user_model()

class DepartmentPerUserInline(admin.TabularInline):
    model = CustomUser.departments.through

class ClusterPerUserInline(admin.TabularInline):
    model = CustomUser.clusters.through

class TeamPerUserInline(admin.TabularInline):
    model = CustomUser.teams.through

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name']

    first_part_of_org_user_screen = UserAdmin.fieldsets[:2]
    second_part_of_org_user_screen = UserAdmin.fieldsets[2:]
    additional_fields = (
        'Referentie velden naar andere systemen',
        {
            'fields': (
                'name_in_negometrix',
            ),
        },
    )
    fieldsets = (
        *first_part_of_org_user_screen,
        additional_fields,
        *second_part_of_org_user_screen,  # original form fieldsets, expanded
    )
    inlines = [DepartmentPerUserInline, ClusterPerUserInline, TeamPerUserInline]

admin.site.register(CustomUser, CustomUserAdmin)


# - Department page -------------------------

class ClusterInline(admin.TabularInline):
    show_change_link = True
    model = Cluster

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [ClusterInline, ]

admin.site.register(Department, DepartmentAdmin)


# - Cluster Page -----------------------------

class TeamInline(admin.TabularInline):
    show_change_link = True
    model = Team


class ClusterAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [TeamInline, ]

admin.site.register(Cluster, ClusterAdmin)


# - Team Page -----------------------------

class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Team, TeamAdmin)
