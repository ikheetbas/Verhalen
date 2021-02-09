import logging
from typing import Tuple, List

from django.contrib.auth.models import Permission
from django.db.models import Q

from users.models import OrganizationalUnit, CustomUser

logger = logging.getLogger(__name__)


def get_all_org_units_of_user(user: CustomUser) -> List[OrganizationalUnit]:
    """
    Gets you all the org_units that this user is allowed to see, this means
    all org_units with a direct relation to the user, but also all org_units
    that are part of these org_units as defined in their hierarchy.
    """
    if user.is_superuser:
        return OrganizationalUnit.objects.all()
    
    direct_org_units_from_user = user.org_units.all()
    all_org_units_from_user = []
    for org_unit in direct_org_units_from_user:
        all_org_units_from_user = all_org_units_from_user + all_org_units_of_org_unit(org_unit)
    return all_org_units_from_user


def all_org_units_of_org_unit(org_unit: OrganizationalUnit) -> List[OrganizationalUnit]:
    """
    Gets you all the org_units that are part of this org_units as defined in the hierarchy,
    including itself.
    """
    child_orgs = []
    for child_org in org_unit.child_org_units.all():
        child_orgs = child_orgs + all_org_units_of_org_unit(child_org)
    return [org_unit] + child_orgs


def get_user_responsible_interface_names(user):
    """
    Gets the names of the user's permissions that are like 'X upload' or 'X API'. These can be compared
    to the names of the Interface Definition to help filtering the Interface Calls to the ones that the
    user is responsible for (or 'allowed' to start/upload).
    """
    interface_permission_names = []
    if user.is_superuser:
        permissions = Permission.objects.filter(Q(codename__contains="upload") | Q(codename__contains="api"))
        permission_codenames = []
        for permission in permissions:
            permission_codenames.append(permission.codename)
    else:
        permission_codenames = user.get_all_permissions()
    for permission_codename in permission_codenames:
        if "upload" in permission_codename or "api" in permission_codename:
            if "." in permission_codename:
                interface_name = permission_codename.split(".")[1]
            else:
                interface_name = permission_codename
            try:
                interface_permission = Permission.objects.get(codename=interface_name)
            except Exception:
                logger.error(f"Ernstige foutsituatie bij het ophalen van de interface "
                             f"(upload/API) permissie {permission} voor gebruiker {user.name}")
            interface_permission_names.append(interface_permission.name)
    return interface_permission_names

