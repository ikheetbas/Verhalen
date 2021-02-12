import logging
from typing import Dict, List

from django.db.models.functions import Now
from django.urls import reverse, NoReverseMatch

from rm.constants import CONTRACTEN, FileStatus
from rm.interface_file_util import check_file_and_interface_type
from rm.models import DataPerOrgUnit, DataSetType, InterfaceDefinition, InterfaceCall
from users import user_utils
from users.models import CustomUser

logger = logging.getLogger(__name__)


def get_active_filter_value(value):
    if value.lower() == 'true':
        return 'active', 'True'
    if value.lower() == 'false':
        return 'active', 'False'
    if value.lower() == 'all':
        return None, None

    logger.info(f"Received unknown filter options in url for 'action', value: '{value}'")
    return None, None


def get_dataset_type_filter_value(value):
    if value.lower() == 'all':
        return None, None
    if value.lower() == CONTRACTEN.lower():
        dataset_type = DataSetType.objects.get(name=CONTRACTEN)
        return 'interface_call__interface_definition__data_set_type_id=', dataset_type.id

    logger.info(f"Received unknown filter options in url for 'system', value: '{value}'")
    return None, None


def get_filter_for_user_responsible_interfaces(value, user):
    if value.lower() == 'false':
        return None, None
    if value.lower() == 'true':
        interface_permission_names = user_utils.get_user_responsible_interface_names(user)
        return 'interface_call__interface_definition__name__in', interface_permission_names

    logger.info(f"Received unknown filter options in url for 'my_datasets', value: '{value}'")
    return None, None


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
        filter_key = None
        if key == 'active':
            filter_key, filter_value = get_active_filter_value(value)
        elif key == 'dataset_type_contracten':
            filter_key, filter_value = get_dataset_type_filter_value(value)
        elif key == 'my_datasets':
            filter_key, filter_value = get_filter_for_user_responsible_interfaces(value, user)
        else:
            logger.info(f"Received unknown filter options in url, key: {key}, value: {value}")
        if filter_key:
            additional_filter[filter_key] = filter_value
    return additional_filter


# filter(interface_call__interface_definition__name__in=user_interface_permissions)

def set_defaults_for_not_available_params(kwargs) -> Dict[str, str]:
    """
    When parameters not present in the parms, add them with their default:
        - active: True
        - my_datasets: False
        - dataset_type_contracten: All
    """
    params = {}
    active_present = False
    my_datasets_present = False
    dataset_type_present = False

    for key, value in kwargs.items():
        params[key] = value
        if key == 'active':
            active_present = True
        if key == 'my_datasets':
            my_datasets_present = True
        if key == 'dataset_type_contracten':
            dataset_type_present = True

    if not active_present:
        params['active'] = 'True'
    if not my_datasets_present:
        params['my_datasets'] = 'False'
    if not dataset_type_present:
        params['dataset_type_contracten'] = 'All'
    return params


def get_datasets_for_user(user: CustomUser, kwargs: dict):
    """
    Gets you the datasets that this user is allowed to see according to the role (group)
    and organization unit.
    Value example of kwargs: {'active': 'True', 'system': 'Negometrix'}>
    """
    list_of_all_org_units_of_user = user_utils.get_all_org_units_of_user(user)
    params = set_defaults_for_not_available_params(kwargs)
    additional_filter = create_addition_dataset_filter(user, params)

    queryset = DataPerOrgUnit.objects. \
        select_related('interface_call', 'org_unit'). \
        filter(org_unit__in=list_of_all_org_units_of_user). \
        filter(**additional_filter)

    return queryset


class InterfaceListRecord:

    def __eq__(self, o: object) -> bool:
        return self.nr == o.nr \
        and self.interface_type == o.interface_type \
        and self.url_upload_page == o.url_upload_page \
        and self.dataset_type == o.dataset_type \
        and self.system == o.system \
        and self.user_email == o.user_email \
        and self.org_unit == o.org_unit \
        and self.rows_ok == o.rows_ok \
        and self.rows_warning ==  o.rows_warning

        # and self.date_time == o.date_time \  -> not checked, makes testing easier

    def __init__(self, nr=None, interface_type="", url_upload_page="", dataset_type="", system="",
                 date_time="", user_email="", org_unit="", rows_ok="", rows_warning=""):
        self.nr = nr
        self.interface_type = interface_type
        self.url_upload_page = url_upload_page
        self.dataset_type = dataset_type
        self.system = system
        self.date_time = date_time
        self.user_email = user_email
        self.org_unit = org_unit
        self.rows_ok = rows_ok
        self.rows_warning = rows_warning


def get_active_datasets_per_interface_for_users_org_units(user: CustomUser) -> List[InterfaceListRecord]:
    """
    Returns overview of interfaces in a way to give the user insight
    in the relations between system/dataset_type -> Interface Calls and DPOU.
    To give the overview, the repeating fields are not filled on following rows.
    To guarantee the right order, a row_nr is added.
    """

    list_of_all_org_units_of_user = user_utils.get_all_org_units_of_user(user)

    records = []
    nr = 1
    for interface in InterfaceDefinition.objects.all():

        interface_type = interface.get_interface_type_display()
        logger.debug(f"Interface_type: {interface_type}")
        dataset_type = interface.data_set_type.name

        url_name_upload_page = user.get_url_name_for_rm_function_if_has_permission(interface.name)
        if url_name_upload_page:
            try:
                url_upload_page = reverse(url_name_upload_page)
            except NoReverseMatch:
                logger.critical(f"Er is een Interface gedefinieerd waar geen "
                                f"upload of api pagina bij hoort: {url_name_upload_page}")
                url_upload_page = ""
        else:
            url_upload_page = ""

        record = InterfaceListRecord(nr=nr,
                                     interface_type=interface_type,
                                     dataset_type=interface.data_set_type.name,
                                     url_upload_page=url_upload_page,
                                     system=interface.system.name)

        if interface.interface_calls.all().filter(status=InterfaceCall.ACTIVE).count() > 0:
            for call in interface.interface_calls.all().filter(status=InterfaceCall.ACTIVE):
                record.date_time = call.date_time_creation
                record.user_email = call.user_email
                dpous_for_this_user = call.dataperorgunit_set.all().\
                    filter(org_unit__in=list_of_all_org_units_of_user,
                           active=True)
                if dpous_for_this_user.count() > 0:
                    for dpou in dpous_for_this_user:
                        if dpou.org_unit in list_of_all_org_units_of_user:
                            record.org_unit = dpou.org_unit.name
                            record.rows_ok = dpou.number_of_data_rows_ok
                            record.rows_warning = dpou.number_of_data_rows_warning
                            records.append(record)
                            nr += 1
                            record = InterfaceListRecord(nr=nr)
                else:
                    records.append(record)
                    nr += 1
                    record = InterfaceListRecord(nr=nr)
        else:
            records.append(record)
            nr += 1
            record = InterfaceListRecord(nr=nr)
    return records


def process_file(file, user, expected_system=None):
    """
    Process the file, register it with the user, find out the type

    """
    # First things first, create the InterfaceCall, with the user
    interface_call = InterfaceCall(filename=file.name,
                                   status=FileStatus.NEW,
                                   date_time_creation=Now(),
                                   user=user,
                                   username=user.username,
                                   user_email=user.email)
    try:
        # check the file and try to find out what type it is
        interface_file = check_file_and_interface_type(file)

        # register InterfaceDefinition (System & DataSetType)
        found_interface_definition: InterfaceDefinition = interface_file.get_interface_definition()
        if not found_interface_definition.system_name == expected_system:
            raise Exception(f"Er werd een {expected_system} bestand verwacht, "
                            f"maar dit is een {found_interface_definition.system_name} bestand")
        interface_call.interface_definition = interface_file.get_interface_definition()
        interface_call.save()

        # process the file!
        interface_file.process(interface_call)

    except Exception as ex:

        interface_call.status = FileStatus.ERROR.name
        interface_call.message = ex.__str__()
        interface_call.save()
        return interface_call.id, "ERROR", ex.__str__()

    return interface_call.id, "OK", "File has been processed"