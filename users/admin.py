from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import Department, Cluster, Team

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name']
    fieldsets = (
        *UserAdmin.fieldsets[:2],  # original form fieldsets, expanded
        (                      # new fieldset added on to the bottom
            'Referentie velden naar andere systemen',
            {
                'fields': (
                    'name_in_negometrix',
                ),
            },
        ),
        *UserAdmin.fieldsets[2:],  # original form fieldsets, expanded
    )

admin.site.register(CustomUser, CustomUserAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Department, DepartmentAdmin)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Cluster, ClusterAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Team, TeamAdmin)
