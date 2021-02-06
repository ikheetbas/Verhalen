import logging

from rm.constants import NEGOMETRIX
from rm.models import DataPerOrgUnit, System
from users.models import CustomUser
from users.user_utils import get_all_org_units_of_user

logger = logging.getLogger(__name__)

def create_addition_dataset_filter(kwargs) -> dict:
    additional_filter = {}
    for key, value in kwargs.items():
        logger.debug(f"Key: {key}, value: {value}")
        if key == 'active':
            if value.upper() == 'TRUE':
                additional_filter['active'] = 'True'
            elif value.upper() == 'FALSE':
                additional_filter['active'] = 'False'
            else:
                logger.info(f"Received unknown filter options in url, key: {key}, value: {value}")
        elif key == 'system':
            if value.upper() == NEGOMETRIX.upper():
                system = System.objects.get(name=NEGOMETRIX)
                additional_filter['interface_call__interface_definition__system_id'] = system.id
            else:
                logger.info(f"Received unknown filter options in url, key: {key}, value: {value}")
        else:
            logger.info(f"Received unknown filter options in url, key: {key}, value: {value}")
    return additional_filter


def create_authorization_filter(user):
    user_org_units = get_all_org_units_of_user(user)



def get_datasets_for_user(user: CustomUser, kwargs: dict):
    """
    Gets you the datasets that this user is allowed to see according to the role (group) and organization unit
    Type op params: <class 'django.http.request.QueryDict'>,
    Value example <QueryDict: {'active': ['True'], 'system': ['Negometrix']}>
    """
    authorization_filter = create_authorization_filter(user)
    additional_filter = create_addition_dataset_filter(kwargs)

    dataset_filter = {}
    queryset = DataPerOrgUnit.objects.\
        select_related('interface_call', 'org_unit').\
        filter(**additional_filter)
    return queryset
