from django.db import models


# class System(models.Model):
#     name = models.CharField(max_length=30, blank=True)


class InterfaceCall(models.Model):
    """
    Call of interface (or file upload)
    """
    date_time_creation = models.DateTimeField(auto_now=False)
    filename = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=15)
    type = models.CharField(max_length=15)
    message = models.TextField(max_length=250, blank=True)
    system = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"File {self.filename} - {self.status} - {self.system}"


class ReceivedData(models.Model):
    interface_call = models.ForeignKey(InterfaceCall,
                                       on_delete=models.CASCADE,
                                       related_name='received_data')
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
    original_end_date = models.DateField("Oorsponkelijke einddatum", null=True, blank=True)
    notice_period = models.CharField("Opzegtermijn", max_length=50, blank=True, null=True)
    notice_period_available = models.CharField("Opzegtermijn aanwezig", max_length=50, blank=True, null=True)

    interface_call = models.ForeignKey(InterfaceCall,
                                       on_delete=models.CASCADE,
                                       related_name='contracten')

    def __str__(self):
        return "Leeg" if not self.contract_nr else str(self.contract_nr) + ": " + self.contract_name
