from django.db import models

# STATIC MODELS ################################################################
from users.models import OrganizationalUnit


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
    class Meta:
        permissions = [
            ("upload_contract_file", "Can upload file with contracts"),
            ("call_contract_interface", "Can call the (negometrix) contract-interface"),
        ]
    date_time_creation = models.DateTimeField(auto_now=False)
    filename = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=15)
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

    def contracts(self):
        contracts = Contract.objects.none()
        for data_per_org_unit in self.dataperorgunit_set.all():
            contracts_per_org_unit = data_per_org_unit.contracten.all()
            contracts = contracts.union(contracts_per_org_unit)
        return contracts

    def __str__(self):
        return f"{self.interface_definition.name}" if self.interface_definition else "Onbekende interface"\
                                                                                     + f" - {self.date_time_creation}"


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
    interface_call = models.ForeignKey(InterfaceCall, on_delete=models.CASCADE)
    org_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)
    number_of_data_rows_ok = models.IntegerField("Dataregels goed", default=0)
    number_of_data_rows_warning = models.IntegerField("Dataregels waarschuwing", default=0)

    def __str__(self):
        return f"{self.org_unit.name} - {self.interface_call.interface_definition.name} - {self.interface_call.date_time_creation}"

# BUSINESS MODELS #########################################################################

class Contract(models.Model):
    """
    Contract with almost no constraints.
    We only use Char and Date, to minimise the risk that the
    received data can't be inserted.
    """
    seq_nr = models.IntegerField()

    database_nr = models.CharField(max_length=50, blank=True, null=True)
    contract_nr = models.CharField(max_length=50, blank=True, null=True)
    contract_status = models.CharField(max_length=50, blank=True, null=True)
    contract_name = models.CharField("Contract naam", max_length=250, blank=True, null=True)
    description = models.CharField("Beschrijving", max_length=250, blank=True, null=True)
    description_contract = models.CharField("Beschrijving contract", max_length=250, blank=True, null=True)
    category = models.CharField("Categorie", max_length=50, blank=True, null=True)

    contract_owner = models.CharField("Contracteigenaar", max_length=50, blank=True, null=True)
    contract_owner_email = models.CharField("Contracteigenaar email", max_length=50, blank=True, null=True)
    contract_owner_phone_nr = models.CharField("Contracteigenaar telnr", max_length=20, blank=True, null=True)

    end_date_contract = models.DateField("Einddatum contract", null=True, blank=True)

    contact_person = models.CharField("Contactpersoon", max_length=50, blank=True, null=True)
    contact_person_email = models.CharField("Contactpersoon email", max_length=50, blank=True, null=True)
    contact_person_phone_nr = models.CharField("Contactpersoon telnr", max_length=20, blank=True, null=True)
    contact_person_name = models.CharField("Contactpersoon naam", max_length=50, blank=True, null=True)

    manufacturer = models.CharField("Fabrikant", max_length=50, blank=True, null=True)
    manufacturer_kvk_nr = models.CharField("Fabrikant KvK nr", max_length=50, blank=True, null=True)
    manufacturer_address = models.CharField("Fabrikant Adres", max_length=250, blank=True, null=True)
    manufacturer_website = models.CharField("Fabrikant Website", max_length=50, blank=True, null=True)

    contracted_value = models.DecimalField("Gecontracteerde waarde", max_digits=10, decimal_places=2, null=True,
                                           blank=True)

    service_level_manager = models.CharField(max_length=50, blank=True, null=True)
    service_level_manager_email = models.CharField(max_length=50, blank=True, null=True)
    service_level_manager_phone_nr = models.CharField(max_length=20, blank=True, null=True)
    service_level_manager_2 = models.CharField(max_length=50, blank=True, null=True)
    service_level_manager_2_email = models.CharField(max_length=50, blank=True, null=True)
    service_level_manager_2_phone_nr = models.CharField(max_length=20, blank=True, null=True)

    type = models.CharField("Soort Contract", max_length=50, blank=True, null=True)
    start_date = models.DateField("Startdatum", null=True, blank=True)
    last_end_date = models.DateField("Uiterste einddatum", null=True, blank=True)
    original_end_date = models.DateField("Oorspronkelijke einddatum", null=True, blank=True)
    notice_period = models.CharField("Opzegtermijn", max_length=50, blank=True, null=True)
    notice_period_available = models.CharField("Opzegtermijn aanwezig", max_length=50, blank=True, null=True)

    data_per_org_unit = models.ForeignKey(DataPerOrgUnit,
                                          on_delete=models.CASCADE,
                                          related_name='contracten')

    raw_data = models.OneToOneField(RawData, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Leeg" if not self.contract_nr else str(self.contract_nr) + ": " + self.contract_name
