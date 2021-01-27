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


class CustomUser(AbstractUser):
    """
    Custom User extending the Django AbstractUser gives us the possibility to add attributes and relations
    """
    name_in_negometrix = models.CharField("Naam in Negometrix", max_length=150, blank=True, null=True)

    # Django Generally, ManyToManyField instances should go in the object that’s going to be edited on a form.
    org_units = models.ManyToManyField(OrganizationalUnit)


