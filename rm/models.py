import logging
from typing import Dict

from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction, IntegrityError

import rm
import users
from bdata.models import Contract
from rm.constants import CONTRACTEN, RowStatus, FileStatus
from rm.exceptions import OtherActiveDataPerOrgUnitException, DuplicateKeyException
from stage.models import StageContract
from users.models import OrganizationalUnit, CustomUser

logger = logging.getLogger(__name__)


class DataSetType(models.Model):
    """
    A data set (or dataset) is a collection of data. In the case of tabular data,
    a data set corresponds to one or more database tables,

    This is the data that is delivered by systems.
    """
    name = models.CharField("Naam", max_length=20, unique=True)
    description = models.CharField("Omschrijving", max_length=50, blank=True)

    def __str__(self):
        return self.name


class System(models.Model):
    """
    The systems that deliver the data
    """
    name = models.CharField("Naam", max_length=20, unique=True)
    description = models.CharField("Omschrijving", max_length=50, blank=True)
    data_set_types = models.ManyToManyField(DataSetType,
                                            through='InterfaceDefinition',
                                            through_fields=('system', 'data_set_type'))
    org_units = models.ManyToManyField(OrganizationalUnit,
                                       through='Mapping',
                                       through_fields=('system', 'org_unit'))

    def __str__(self):
        return self.name

    def get_org_unit_by_mapping(self, mapping_name):
        """
        Returns the OrganizationalUnit that can be found for this System with the mapping name
        """
        mappings = self.mapping_set.filter(name=mapping_name)
        if len(mappings) == 0:
            return None

        org_unit = mappings[0].org_unit

        return org_unit

class InterfaceDefinition(models.Model):
    """
    This defines the Interface through which a System delivers data of type
    DataSetType.
    """
    API = "API"
    UPLOAD = "UPL"
    INTERFACE_TYPE = (
        (API, "API"),
        (UPLOAD, "Upload")
    )
    name = models.CharField("Naam", max_length=20, unique=True)
    description = models.CharField("Omschrijving", max_length=50, blank=True)
    interface_type = models.CharField(max_length=3, choices=INTERFACE_TYPE)
    url = models.URLField(blank=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    data_set_type = models.ForeignKey(DataSetType, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['system', 'data_set_type', 'interface_type']]

    @property
    def data_set_type_name(self):
        return self.data_set_type.name

    @property
    def system_name(self):
        return self.system.name

    def __str__(self):
        return self.name


class Mapping(models.Model):
    """
    Mapping contains the 'names' of the OrganizationalUnits in the Systems.
    For example, it defines how the 'Team IAAS' is called in Negometrix, or the
    'kostenplaats' as defined in Oracle. The downloads contains these values and
    have to be converted into a Department, Cluster or Team. That is done with
    this class.
    """
    name = models.CharField("Naam/Code/Sleutel", max_length=50, unique=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    org_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)


# PROCESS MODELS ###############################################################

class InterfaceCall(models.Model):
    """
    Call of interface (or file upload)
    """
    NEW = "NEW"
    LOADING = "LOADING"
    ERROR = "ERROR"
    READY_LOADING = "READY_LOADING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OK = "OK"
    INTERFACE_CALL_STATUS = (
        (NEW, "NEW"),
        (LOADING, "LOADING"),
        (ERROR, "ERROR"),
        (OK, "OK"),
        (READY_LOADING, "READY_LOADING"),
        (ACTIVE, "ACTIVE"),
        (INACTIVE, "INACTIVE"),
    )

    class Meta:
        permissions = [
            ("contracten_api", "Contracten API"),
            ("contracten_upload", "Contracten upload"),
            ("contracten_view", "Contracten view")
        ]

    date_time_creation = models.DateTimeField(auto_now=False, auto_now_add=True)
    filename = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=15, choices=INTERFACE_CALL_STATUS)
    message = models.TextField(max_length=250, blank=True)

    number_of_rows_received = models.IntegerField("Aantal ontvangen regels", default=0)
    number_of_data_rows_received = models.IntegerField("Aantal ontvangen dataregels", default=0)
    number_of_empty_rows = models.IntegerField("Aantal lege regels", default=0)
    number_of_header_rows = models.IntegerField("Aantal header regels", default=0)
    number_of_data_rows_ok = models.IntegerField("Aantal dataregels goed", default=0)
    number_of_data_rows_warning = models.IntegerField("Aantal dataregels waarschuwing", default=0)
    number_of_data_rows_error = models.IntegerField("Aantal dataregels fout", default=0)
    number_of_data_rows_ignored = models.IntegerField("Aantal dataregels genegeerd", default=0)

    interface_definition = models.ForeignKey(InterfaceDefinition,
                                             on_delete=models.CASCADE,
                                             related_name='interface_calls',
                                             null=True)
    # username and user_email are set, in case the user is removed, we still have the original user
    username = models.CharField(max_length=250, null=True)
    user_email = models.CharField(max_length=254, null=True)
    user = models.ForeignKey(CustomUser,
                             on_delete=models.SET_NULL,
                             null=True)

    @property
    def datatype(self):
        """
        shortcut for interface_definition.data_set_type.name
        """
        if not self.interface_definition:
            return None
        return self.interface_definition.data_set_type.name

    @property
    def system_name(self):
        """
        shortcut for interface_definition.system.name
        """
        if not self.interface_definition:
            return None
        return self.interface_definition.system.name

    @property
    def org_units(self):
        org_units = []
        for dpou in self.dataperorgunit_set.all():
            org_units.append(dpou.org_unit)
        return org_units


    def stage_contracts(self):
        contracts = StageContract.objects.none()
        for data_per_org_unit in self.dataperorgunit_set.all():
            contracts_per_org_unit = data_per_org_unit.stagecontract_set.all()
            contracts = contracts.union(contracts_per_org_unit)
        return contracts

    def stage_contracts_per_org(self) -> Dict[str, StageContract]:
        """
        Delivers a Dict per DataOrgPerUnit with StageContracts for display on tabs
        """
        contracts = {}
        for data_per_org_unit in self.dataperorgunit_set.all():
            contracts_per_org_unit = data_per_org_unit.stagecontract_set.all().order_by("seq_nr")
            status = " (Actief)" if data_per_org_unit.active else " (Inactief)"
            tab_label_and_id_tuple = (data_per_org_unit.org_unit.name + status,
                                      data_per_org_unit.org_unit.id)
            contracts[tab_label_and_id_tuple] = contracts_per_org_unit
        return contracts


    def contracts(self):
        contracts = Contract.objects.none()
        for data_per_org_unit in self.dataperorgunit_set.all():
            contracts_per_org_unit = data_per_org_unit.contract_set.all()
            contracts = contracts.union(contracts_per_org_unit)
        return contracts

    def __str__(self):
        return f"{self.interface_definition.name}" if self.interface_definition else "Onbekende interface" \
                                                                                     + f" - {self.date_time_creation}"

    def get_dataperorgunit(self, org_unit) -> "DataPerOrgUnit":
        if not org_unit:
            raise ValueError("Calling get_dataperorgunit with org_unit is None")

        if type(org_unit) == str:
            org_unit = OrganizationalUnit.objects.get(name=org_unit)

        if type(org_unit) == OrganizationalUnit:
            dpou_set = self.dataperorgunit_set.filter(org_unit=org_unit)
            if len(dpou_set) == 1:
                return dpou_set[0]
            else:
                raise users.models.OrganizationalUnit.DoesNotExist

    def deactivate_interface_call(self,
                                  start_transaction: bool = False):
        """
        Deactivating a InterfaceCall means deactivating all its child DataPerOrgUnit records. Which means: deleting
        all  business records (not the staging ones!) of that DataPerOrgUnit.
        """
        self.refresh_from_db()
        if not self.is_active():
            return

        if start_transaction:
            try:
                with transaction.atomic():
                    self._deactivate_interface_call()
            except Exception as ex:
                logger.exception(f"Exception tijdens het deactiveren van Interface Call: "
                                 f"id={self.id} {self.filename} {self.date_time_creation}", ex)
                # re raise so we can show it to the user
                raise
        else:
            self._deactivate_interface_call()

    def _deactivate_interface_call(self):
        self.status = InterfaceCall.INACTIVE
        self.save()
        for data_per_org_unit in self.dataperorgunit_set.filter(active=True):
            data_per_org_unit.deactivate_dataset()

    def activate_interface_call(self,
                                start_transaction: bool = False,
                                cascading=False):
        """
        Activate this Interface Call, by activating all Data Per Org Units under it.
        Parameters:
            * start_transaction: default False
            * cascading: when True, children DPOU will be activated as well
        Exceptions:
            * all exceptions that occur during underlying actions
        """
        self.refresh_from_db()


        if start_transaction:
            try:
                with transaction.atomic():
                    self._activate_interface_call(cascading)
            except Exception as ex:
                logger.exception(f"Exception tijdens het activeren van Interface Call: "
                                 f"id={self.id} {self.filename} {self.date_time_creation}", ex)
                # re raise so we can show it to the user
                self.status = FileStatus.ERROR.name
                self.message = f"Activeren is mislukt: {ex.__str__()}"
                self.save()
        else:
            self._activate_interface_call(cascading)

    def _activate_interface_call(self, cascading):
        """
        Loop through all data_per_org_unit and activate them.
        After that, activate this interface_call
        """
        self.status = InterfaceCall.ACTIVE
        self.save()
        if cascading:
            for data_per_org_unit in self.dataperorgunit_set.filter(active=False):
                data_per_org_unit.activate_dataset(activating_from_interface_call=True)

    def is_active(self):
        """
        Just to be clear: only status 'ACTIVE' is active, the others are not!
        """
        if self.status == InterfaceCall.ACTIVE:
            return True
        else:
            return False

    @property
    def active(self):
        return self.is_active()

    def is_not_active(self):
        """
        Just to be clear: only status 'ACTIVE' is active, the others are not!
        """
        return not self.is_active()

    @property
    def not_active(self):
        return self.is_not_active()

    def is_completely_active(self):
        """
        True if the interface_call is active AND all data_per_org_unit's are active
        """
        if not self.is_active():
            return False

        if self.dataperorgunit_set.filter(active=False).count() > 0:
            return False

        return True

    def is_completely_inactive(self):
        """
        True if the interface_call is not active AND all data_per_org_unit's are not active
        """
        if self.is_active():
            return False

        if self.dataperorgunit_set.filter(active=True).count() > 0:
            return False

        return True


class RawData(models.Model):
    interface_call = models.ForeignKey(InterfaceCall,
                                       on_delete=models.CASCADE)
    seq_nr = models.IntegerField()
    status = models.CharField(max_length=20, blank=True)
    message = models.CharField(max_length=250, blank=True, null=True)
    field_01 = models.CharField(max_length=250, blank=True)
    field_02 = models.CharField(max_length=250, blank=True)
    field_03 = models.CharField(max_length=250, blank=True)
    field_04 = models.CharField(max_length=250, blank=True)
    field_05 = models.CharField(max_length=250, blank=True)
    field_06 = models.CharField(max_length=250, blank=True)
    field_07 = models.CharField(max_length=250, blank=True)
    field_08 = models.CharField(max_length=250, blank=True)
    field_09 = models.CharField(max_length=250, blank=True)
    field_10 = models.CharField(max_length=250, blank=True)
    field_11 = models.CharField(max_length=250, blank=True)
    field_12 = models.CharField(max_length=250, blank=True)
    field_13 = models.CharField(max_length=250, blank=True)
    field_14 = models.CharField(max_length=250, blank=True)
    field_15 = models.CharField(max_length=250, blank=True)
    field_16 = models.CharField(max_length=250, blank=True)
    field_17 = models.CharField(max_length=250, blank=True)
    field_18 = models.CharField(max_length=250, blank=True)
    field_19 = models.CharField(max_length=250, blank=True)
    field_20 = models.CharField(max_length=250, blank=True)
    field_21 = models.CharField(max_length=250, blank=True)
    field_22 = models.CharField(max_length=250, blank=True)
    field_23 = models.CharField(max_length=250, blank=True)
    field_24 = models.CharField(max_length=250, blank=True)
    field_25 = models.CharField(max_length=250, blank=True)
    field_26 = models.CharField(max_length=250, blank=True)
    field_27 = models.CharField(max_length=250, blank=True)
    field_28 = models.CharField(max_length=250, blank=True)
    field_29 = models.CharField(max_length=250, blank=True)
    field_30 = models.CharField(max_length=250, blank=True)
    field_31 = models.CharField(max_length=250, blank=True)
    field_32 = models.CharField(max_length=250, blank=True)
    field_33 = models.CharField(max_length=250, blank=True)
    field_34 = models.CharField(max_length=250, blank=True)
    field_35 = models.CharField(max_length=250, blank=True)
    field_36 = models.CharField(max_length=250, blank=True)
    field_37 = models.CharField(max_length=250, blank=True)
    field_38 = models.CharField(max_length=250, blank=True)
    field_39 = models.CharField(max_length=250, blank=True)
    field_40 = models.CharField(max_length=250, blank=True)
    field_41 = models.CharField(max_length=250, blank=True)
    field_42 = models.CharField(max_length=250, blank=True)
    field_43 = models.CharField(max_length=250, blank=True)
    field_44 = models.CharField(max_length=250, blank=True)
    field_45 = models.CharField(max_length=250, blank=True)
    field_46 = models.CharField(max_length=250, blank=True)
    field_47 = models.CharField(max_length=250, blank=True)
    field_48 = models.CharField(max_length=250, blank=True)
    field_49 = models.CharField(max_length=250, blank=True)
    field_50 = models.CharField(max_length=250, blank=True)


class DataPerOrgUnit(models.Model):
    """
    The data from the interface is transformed into business objects. They always
    have a relation with a Organizational Unit. Per interfacecall that can be multiple
    Organizational Units. This class gives a handle to that grouping per OrgUnit.
    We need that for example to see the latest refresh moment of data for certain
    OrgUnits
    """

    class Meta:
        unique_together = [['interface_call', 'org_unit']]

    interface_call = models.ForeignKey(InterfaceCall, on_delete=models.CASCADE)
    org_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)
    number_of_data_rows_ok = models.IntegerField("Dataregels goed", default=0)
    number_of_data_rows_warning = models.IntegerField("Dataregels waarschuwing", default=0)
    active = models.BooleanField("Actief", default=False)

    def __str__(self):
        return f"{self.id} - " \
               f"{self.org_unit.name} - " \
               f"{self.interface_call.interface_definition.name} - " \
               f"{self.interface_call.date_time_creation}"

    @property
    def not_active(self):
        return not self.active

    def activate_dataset(self,
                         start_transaction: bool = False,
                         activating_from_interface_call: bool = False) -> str:
        """
        Activate the dataset, when activated from screen and error occurs, all is rolled back and
        the errormessage is returned.
        """
        errormessage = None
        if self.active:
            return errormessage

        if start_transaction:
            try:
                with transaction.atomic():
                    self._activate_dataset(activating_from_interface_call)
            except Exception as ex:
                logger.exception(f"Exception tijdens het activeren van DataPerOrgUnit: "
                                 f"id={self.id} {self.org_unit.name} {self.get_data_set_type().name}", ex)
                errormessage = f"Activeren is mislukt: {ex.__str__()}"
                return errormessage
        else:
            self._activate_dataset(activating_from_interface_call)
        return errormessage

    def _activate_dataset(self,
                          activating_from_interface_call: bool):

        """
        Activate the DataOrgPerUnit
        """
        if activating_from_interface_call:
            self.deactivate_previous_interface_call()
        else:
            self.deactivate_active_siblings()

        copy_stage_data_to_bdata(self)

        self.active = True
        self.save()

        if self.interface_call.is_not_active():
            self.interface_call.activate_interface_call(cascading=False)

        if self.all_data_org_units_of_this_interface_call_are_active():
            self.interface_call.activate_interface_call()

    def deactivate_dataset(self,
                           start_transaction: bool = False):
        """
        Change active->False and removes corresponding Business Data.
        When already deactivated, no error, but directly exit.
        To prevent circular reactions as well.
        """
        errormessage = None
        if not self.active:
            return errormessage

        if start_transaction:
            try:
                with transaction.atomic():
                    self._deactivate_dataset()
            except Exception as ex:
                logger.exception(f"Exception tijdens het deactiveren van DataPerOrgUnit: "
                                 f"id={self.id} {self.org_unit.name} {self.get_data_set_type().name}", ex)
                errormessage = f"Deactiveren is mislukt: {ex.__str__()}"
                return errormessage
        else:
            self._deactivate_dataset()

        return errormessage

    def _deactivate_dataset(self, ):
        self.active = False
        self.save()

        data_set_type_name = self.get_data_set_type().name
        if data_set_type_name and data_set_type_name == CONTRACTEN:
            self.contract_set.all().delete()
        else:
            raise RuntimeError(f"DataSetType {data_set_type_name} is nog niet bekend "
                               f"in dit stuk van de software (rm.models.DataPerOrgUnit")

        if self.all_data_org_units_of_this_interface_call_are_inactive():
            self.interface_call.deactivate_interface_call()

    def get_data_set_type(self):
        if not self.interface_call:
            raise RuntimeError(f"Dit DataPerOrgUnit (pk={self.pk}) heeft geen InterfaceCall")
        if not self.interface_call.interface_definition:
            raise RuntimeError(f"Dit DataPerOrgUnit (pk={self.pk}) heeft geen InterfaceDefinition")
        if not self.interface_call.interface_definition.data_set_type:
            raise RuntimeError(f"Dit DataPerOrgUnit (pk={self.pk}) heeft geen DataSetType")
        if not self.interface_call.interface_definition.data_set_type.name:
            raise RuntimeError(f"De DataSetType van deze DataPerORgUnit (pk={self.pk}) heeft geen naam")

        return self.interface_call.interface_definition.data_set_type

    def deactivate_previous_interface_call(self):
        """
        Looks for active 'siblings', meaning: active, same data_set_type and
        deactivate the owning InterfaceCall (which will deactivate all its DataPerOrgUnit,
        amongst which the just found DataPerOrgUnit
        """
        for interface_call in self.find_previous_interface_calls():
            interface_call.deactivate_interface_call()

    def find_previous_interface_calls(self):
        result = []
        this_data_set = self.get_data_set_type()
        for data_per_org_unit in DataPerOrgUnit.objects.filter(active=True,
                                                               org_unit=self.org_unit):
            if not self.myself(data_per_org_unit):
                if data_per_org_unit.get_data_set_type() == this_data_set:
                    result.append(data_per_org_unit.interface_call)
        return result

    def all_data_org_units_of_this_interface_call_are_inactive(self):
        return self.interface_call.dataperorgunit_set.filter(active=True).count() == 0

    def all_data_org_units_of_this_interface_call_are_active(self):
        return self.interface_call.dataperorgunit_set.filter(active=False).count() == 0

    def deactivate_active_siblings(self):
        """
        Deactivate other active datasets for the same org_unit and datasettype
        """
        data_set_type_name = self.get_data_set_type().name
        for data_per_org_unit in DataPerOrgUnit.objects.filter(active=True, org_unit=self.org_unit):
            if not self.myself(data_per_org_unit):
                if data_per_org_unit.get_data_set_type().name == data_set_type_name:
                    data_per_org_unit.deactivate_dataset()

    def myself(self, data_per_org_unit):
        return data_per_org_unit.id == self.id

    def increase_row_count(self, count, status):
        if status == RowStatus.DATA_OK:
            self.number_of_data_rows_ok += 1
        elif status == RowStatus.DATA_WARNING:
            self.number_of_data_rows_warning += 1
        else:
            raise ValueError(f"Increasing rowcount for DataPerOrgUnit is only valid for status {RowStatus.DATA_OK} "
                             f"and {RowStatus.DATA_WARNING}, not for {status}")


def copy_stage_data_to_bdata(self):
    if self.get_data_set_type().name == CONTRACTEN:
        copy_stage_contracts_to_bdata(self)


def copy_stage_contracts_to_bdata(self):
    for stage_contract in self.stagecontract_set.all():
        contract = Contract(seq_nr=stage_contract.seq_nr)
        copy_all_fields_from_stage_object_to_bdata_object(stage_contract, contract)
        try:
            contract.save()
        except IntegrityError as ex:
            logger.error(f"Fout (dubbel contract_nr?)  bij het wegschrijven van Contract: {contract.__str__()}", ex)
            if "bdata_contract_contract_nr_key" in ex.__str__():
                raise DuplicateKeyException(table=Contract._meta.model_name,
                                            to_string=contract.__str__(),
                                            seq_nr=contract.seq_nr,
                                            field_name="contract_nr",
                                            value=contract.contract_nr,
                                            )
            else:
                raise
        except Exception as ex:
            logger.error(f"Andere exception dan Integrity fout bij het wegschrijven van Contract: {contract.__str__()}",
                         ex)
            raise


def copy_all_fields_from_stage_object_to_bdata_object(stage_contract, contract):
    for field in StageContract._meta.get_fields():
        if contract_has_field(field.name):
            value = getattr(stage_contract, field.name)
            setattr(contract, field.name, value)


def contract_has_field(name):
    try:
        Contract._meta.get_field(name)
    except FieldDoesNotExist as ex:
        return False
    return True
