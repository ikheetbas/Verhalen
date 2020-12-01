from django.contrib import admin
from rm.models import Contract, InterfaceCall



class ContractInline(admin.TabularInline):
    model = Contract


class InterfaceCallAdmin(admin.ModelAdmin):
    """
    Change the way the list of interface calls looks
    """
    inlines = [ ContractInline, ]
    list_display = ["date_time_creation", "status", "filename"]


admin.site.register(InterfaceCall, InterfaceCallAdmin)


class ContractAdmin(admin.ModelAdmin):
    """
    Change the way the list of contracts looks
    """
    list_display = ["nr", "description", "owner"]


admin.site.register(Contract, ContractAdmin)
