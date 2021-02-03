from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction

from bdata.models import Contract
from rm.constants import CONTRACTEN
from stage.models import StageContract
from users.models import OrganizationalUnit, CustomUser


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
    INTERFACE_CALL_STATUS = (
        (NEW, "NEW"),
        (LOADING, "LOADING"),
        (ERROR, "ERROR"),
        (READY_LOADING, "READY_LOADING"),
        (ACTIVE, "ACTIVE"),
        (INACTIVE, "INACTIVE"),
    )

    class Meta:
        permissions = [
            ("upload_contract_file", "Can upload file with contracts"),
            ("call_contract_interface", "Can call the (negometrix) contract-interface"),
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

    def stage_contracts(self):
        contracts = StageContract.objects.none()
        for data_per_org_unit in self.dataperorgunit_set.all():
            contracts_per_org_unit = data_per_org_unit.stagecontract_set.all()
            contracts = contracts.union(contracts_per_org_unit)
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

    def deactivate(self):
        """
        Deactivating a InterfaceCall means deactivating all its child DataPerOrgUnit records. Which means: deleting
        all  business records (not the staging ones!) of that DataPerOrgUnit.
        """
        for data_per_org_unit in self.dataperorgunit_set.all():
            data_per_org_unit.deactivate()
        self.status = InterfaceCall.INACTIVE
        self.save()

    def activate(self):

        with transaction.atomic():
            for data_per_org_unit in self.dataperorgunit_set.all():
                data_per_org_unit.activate(deactivate_previous_interface_calls_first=True)
            self.status = InterfaceCall.ACTIVE
            self.save()

    def is_active(self):
        """
        Just to be clear: only status 'ACTIVE' is active, the others are not!
        """
        if self.status == InterfaceCall.ACTIVE:
            return True
        else:
            return False


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

    def activate(self, deactivate_previous_interface_calls_first: bool = False):
        """
        Activate the DataOrgPerUnit
        """
        if deactivate_previous_interface_calls_first:
            self.deactivate_previous_interface_call()
        else:
            if self.are_there_active_siblings():
                raise SystemError(f"Onbekende datasettype nog niet bekend in dit"
                                  f" stuk van de software: {self.get_data_set_type().name}")

        copy_stage_data_to_bdata(self)

        self.active = True
        self.save()

    def deactivate(self):
        """
        Change active->False and removes corresponding Business Data.
        No check on status Active/Inactive, it will always perform these steps.
        """
        self.active = False
        self.save()

        data_set_type_name = self.get_data_set_type().name
        if data_set_type_name and data_set_type_name == CONTRACTEN:
            self.contract_set.all().delete()
        else:
            raise RuntimeError(f"DataSetType {data_set_type_name} is nog niet bekend "
                               f"in dit stuk van de software (rm.models.DataPerOrgUnit")

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
            interface_call.deactivate()

    def find_previous_interface_calls(self):
        result = []
        this_data_set = self.get_data_set_type()
        for data_per_org_unit in DataPerOrgUnit.objects.filter(active=True,
                                                               org_unit=self.org_unit):
            if data_per_org_unit.get_data_set_type() == this_data_set:
                result.append(data_per_org_unit.interface_call)
        return result

    def are_there_active_siblings(self) -> bool:
        """
        Checks if all other DataPerOrgUnit for the same OrgUnit and DataSetType are inactive
        """
        this_data_set = self.get_data_set_type()
        for data_per_org_unit in DataPerOrgUnit.objects.filter(active=True,
                                                               org_unit=self.org_unit):
            if data_per_org_unit.get_data_set_type() == this_data_set:
                return True
        return False



def copy_stage_data_to_bdata(self):
    if self.get_data_set_type().name == CONTRACTEN:
        copy_stage_contracts_to_bdata(self)


def copy_stage_contracts_to_bdata(self):
    for stage_contract in self.stagecontract_set.all():
        contract = Contract(seq_nr=stage_contract.seq_nr)
        copy_all_fields_from_stage_object_to_bdata_object(stage_contract, contract)
        contract.save()


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