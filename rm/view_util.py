import logging

from django.contrib.auth.models import Permission

from rm.constants import NEGOMETRIX
from rm.models import DataPerOrgUnit, System
from users.models import CustomUser
from users.user_utils import get_all_org_units_of_user, get_user_responsible_interface_names

logger = logging.getLogger(__name__)


def get_active_filter_value(value):
    if value.lower() == 'true':
        return 'active', 'True'
    elif value.lower() == 'false':
        return 'active', 'False'
    else:
        logger.info(f"Received unknown filter options in url for 'action', value: '{value}'")
        return None, None


def get_system_filter_value(value):
    if value.lower() == NEGOMETRIX.lower():
        system = System.objects.get(name=NEGOMETRIX)
        return 'interface_call__interface_definition__system_id', system.id
    else:
        logger.info(f"Received unknown filter options in url for 'system', value: '{value}'")
        return None, None


def get_filter_for_user_responsible_interfaces(user):
    interface_permission_names = get_user_responsible_interface_names(user)
    return 'interface_call__interface_definition__name__in', interface_permission_names


def create_addition_dataset_filter(user, kwargs) -> dict:
    """
    Creates additional filter using the kwargs. It responds on the following key's
       * active: True/False
       * system: Negometrix / ....
       * my_responsibility:
    """
    additional_filter = {}
    for key, value in kwargs.items():
        key = key.lower()
        value = value.lower()
        logger.debug(f"Key: {key}, value: {value}")
        if key == 'active':
            filter_key, filter_value = get_active_filter_value(value)
        elif key == 'system':
            filter_key, filter_value = get_system_filter_value(value)
        elif key == 'responsibility' and value == 'user':
            filter_key, filter_value = get_filter_for_user_responsible_interfaces(user)
        else:
            logger.info(f"Received unknown filter options in url, key: {key}, value: {value}")
        if filter_key:
            additional_filter[filter_key] = filter_value
    return additional_filter

# filter(interface_call__interface_definition__name__in=user_interface_permissions)

def get_datasets_for_user(user: CustomUser, kwargs: dict):
    """
    Gets you the datasets that this user is allowed to see according to the role (group)
    and organization unit.
    Value example of kwargs: {'active': 'True', 'system': 'Negometrix'}>
    """
    org_based_authorization_filter = get_all_org_units_of_user(user)
    additional_filter = create_addition_dataset_filter(user, kwargs)

    dataset_filter = {}
    queryset = DataPerOrgUnit.objects.\
        select_related('interface_call', 'org_unit').\
        filter(org_unit__in=org_based_authorization_filter).\
        filter(**additional_filter).filter()

    # if kwargs.get('callable') == 'True':
    #     logger.debug("Callable = True")
    #     filtered_queryset = []
    #     for dpou in queryset:
    #         if user.has_perm_with_name("rm",
    #                                    dpou.interface_call.interface_definition.name):
    #             filtered_queryset.append(dpou)
    #     return filtered_queryset
    # else:

    return queryset
