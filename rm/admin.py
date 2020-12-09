from django.contrib import admin
from rm.models import Contract, InterfaceCall, ReceivedData

class ReceivedDataAdmin(admin.ModelAdmin):
    list_display = ["interface_call", "seq_nr", "field_01", "field_02"]

admin.site.register(ReceivedData, ReceivedDataAdmin)

# -------------------------------------------------------------------
# ADMIN Interface page with Contracts
# -------------------------------------------------------------------
class ContractInline(admin.TabularInline):
    model = Contract

class ReceivedDataInline(admin.TabularInline):
    model = ReceivedData

class InterfaceCallAdmin(admin.ModelAdmin):
    """
    Change the way the list of interface calls looks
    """
    inlines = [ContractInline, ReceivedDataInline]
    list_display = ["date_time_creation", "status", "filename"]

admin.site.register(InterfaceCall, InterfaceCallAdmin)


# -------------------------------------------------------------------
# ADMIN Contract page
# -------------------------------------------------------------------
class ContractAdmin(admin.ModelAdmin):
    """
    Change the way the list of contracts looks
    """
    list_display = ["contract_nr", "description", "contract_owner"]

admin.site.register(Contract, ContractAdmin)