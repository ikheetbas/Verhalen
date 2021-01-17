from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField("Naam", max_length=50)
    def __str__(self):
        return f"Department: {self.name}"


class Cluster(models.Model):
    name = models.CharField("Naam", max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cluster: {self.name}"


class Team(models.Model):
    name = models.CharField("Naam", max_length=50)
    cluster = models.ForeignKey(Cluster,on_delete=models.CASCADE)

    def __str__(self):
        return f"Team: {self.name}"


class CustomUser(AbstractUser):
    name_in_negometrix = models.CharField("Naam in Negometrix", max_length=150, blank=True, null=True)

    # Django Generally, ManyToManyField instances should go in the object that’s going to be edited on a form.
    departments = models.ManyToManyField(Department)
    clusters = models.ManyToManyField(Cluster)
    teams = models.ManyToManyField(Team)
