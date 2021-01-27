from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import OrganizationalUnit

# - CustomUser page ------------------------------------------------

CustomUser = get_user_model()

class OrgUnitPerUserInline(admin.TabularInline):
    model = CustomUser.org_units.through


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
    inlines = [OrgUnitPerUserInline]

admin.site.register(CustomUser, CustomUserAdmin)



# - Organizational Unit Page --------------------------------
# - with details, underlying org units and custom users in it

class OrgUnitInline(admin.TabularInline):
    show_change_link = True
    model = OrganizationalUnit

class UsersPerOrgUnitInline(admin.TabularInline):
    model = CustomUser.org_units.through

class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [OrgUnitInline,
               UsersPerOrgUnitInline]

admin.site.register(OrganizationalUnit, OrganizationalUnitAdmin)