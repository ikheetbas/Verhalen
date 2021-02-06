from typing import Tuple, List

from users.models import OrganizationalUnit, CustomUser


def get_all_org_units_of_user(user: CustomUser) -> List[OrganizationalUnit]:
    """
    Gets you all the org_units that this user is allowed to see, this means
    all org_units with a direct relation to the user, but also all org_units
    that are part of these org_units as defined in their hierarchy.
    """
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
