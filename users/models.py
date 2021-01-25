from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """
    The classes Department, Cluster and Team are candidates for inheritance as subclasses of Organizational_unit.
    But the possible constructions in Django didn't deliver that much benefits.
    Therefore was decided to make them just plain classes, with the benefit of readability and easy relations and screen
    generation for the admin screens.
    """
    name = models.CharField("Naam", max_length=50)
    cost_centre = models.CharField("Kostenplaats", max_length=50, default="<<onbekend>>")
    def __str__(self):
        return f"Department: {self.name}"


class Cluster(models.Model):
    name = models.CharField("Naam", max_length=50)
    cost_centre = models.CharField("Kostenplaats", max_length=50, default="<<onbekend>>")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cluster: {self.name}"


class Team(models.Model):
    name = models.CharField("Naam", max_length=50)
    cost_centre = models.CharField("Kostenplaats", max_length=50, default="<<onbekend>>")
    cluster = models.ForeignKey(Cluster,on_delete=models.CASCADE)

    def __str__(self):
        return f"Team: {self.name}"


class CustomUser(AbstractUser):
    """
    Custom User extending the Django AbstractUser gives us the possibility to add attributes and relations
    """
    name_in_negometrix = models.CharField("Naam in Negometrix", max_length=150, blank=True, null=True)

    # Django Generally, ManyToManyField instances should go in the object that’s going to be edited on a form.
    departments = models.ManyToManyField(Department)
    clusters = models.ManyToManyField(Cluster)
    teams = models.ManyToManyField(Team)
