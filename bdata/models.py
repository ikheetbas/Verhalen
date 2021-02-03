from django.db import models


class Contract(models.Model):
    """
    Contract with a bit more constraints, but loosely coupled
    """
    seq_nr = models.IntegerField()

    database_nr = models.CharField(max_length=50, blank=True, null=True)
    contract_nr = models.CharField(max_length=50, blank=True, null=True, unique=True)
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

    data_per_org_unit = models.ForeignKey("rm.DataPerOrgUnit",
                                          on_delete=models.CASCADE)

    def __str__(self):
        return "Leeg" if not self.contract_nr else str(self.contract_nr) + ": " + self.contract_name

