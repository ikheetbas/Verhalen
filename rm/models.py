from django.db import models


class InterfaceCall(models.Model):
    """
    Call of interface (or file upload)
    """
    date_time_creation = models.DateTimeField(auto_now=False)
    filename = models.CharField(max_length=150)
    status = models.CharField(max_length=10)


class Contract(models.Model):
    """
    Contract with almost no constraints.
    We only use Char and Date, to minimise the risk that the
    received data can't be inserted.
    """
    nr = models.CharField("Contract nr", max_length=25)
    status = models.CharField(max_length=25)
    description = models.CharField("Beschrijving", max_length=250)
    category = models.CharField("Categorie", max_length=50)
    owner = models.CharField("Eigenaar", max_length=25)
    owner_email = models.CharField("Eigenaar email", max_length=50)
    owner_phone_nr = models.CharField("Eigenaar telnr", max_length=20)
    type = models.CharField(max_length=20)
    last_end_date = models.DateField("Uiterste einddatum")
    interface_call = models.ForeignKey(InterfaceCall,
                                       on_delete=models.CASCADE,
                                       related_name='contracten')

    def __str__(self):
        return self.nr + " - " + self.description
