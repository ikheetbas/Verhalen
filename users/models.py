from django.contrib.auth.models import AbstractUser
from django.db import models


class OrganizationalUnit(models.Model):
    AFDELING = 'AFD'
    CLUSTER = 'CLU'
    TEAM = 'TEA'
    ORG_UNIT_TYPE = (
        (AFDELING, 'Afdeling'),
        (CLUSTER, 'Cluster'),
        (TEAM, 'Team'),
    )
    name = models.CharField("Naam", max_length=50, blank=False, null=True, unique=True)
    type = models.CharField(max_length=3, choices=ORG_UNIT_TYPE)
    parent_org_unit = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='child_org_units')

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"


def convert_permission_name_to_id(app, permission_name):
    """
    Coverts "app", "Something To Do" to "rm.something_to_do"
    """
    return app + "." + permission_name.lower().replace(" ", "_")


class CustomUser(AbstractUser):
    """
    Custom User extending the Django AbstractUser gives us the possibility to add attributes and relations
    """
    name_in_negometrix = models.CharField("Naam in Negometrix", max_length=150, blank=True, null=True)

    # Django Generally, ManyToManyField instances should go in the object that’s going to be edited on a form.
    org_units = models.ManyToManyField(OrganizationalUnit)

    def is_authorized_for_org_unit(self, org_unit: OrganizationalUnit) -> bool:
        if self.is_superuser:
            return True
        if org_unit in self.org_units.all():
            return True
        i = 0
        while org_unit.parent_org_unit and i<15:
            i += 1
            org_unit = org_unit.parent_org_unit
            if org_unit in self.org_units.all():
                return True
        if i == 15:
            raise Exception("Exit i.v.m. endless-loopbeveiliging")
        return False

    def has_perm_with_name(self, app, permission_name: str):
        """
        Checks if a user has permission for "app"."Something To Do" by converting
        it to a permission codename: "app.something_to_do" and checking that codename.
        """
        permission = convert_permission_name_to_id(app, permission_name)
        return self.has_perm(permission)

    def get_url_name_for_rm_function_if_has_permission(self, permission_name):
        """
        If the user has rm.permission_name, than that permission_name
        is returned to be used as url_name

        """
        if self.has_perm_with_name("rm", permission_name)\
                or self.is_superuser:
            return permission_name.lower().replace(" ", "_")
        else:
            return None