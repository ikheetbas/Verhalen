from django.contrib import admin
from rm.models import Contract, InterfaceCall, RawData, System, DataSetType, InterfaceDefinition


# -------------------------------------------------------------------
# System page with InterfaceDefinition
# -------------------------------------------------------------------
class InterfaceDefinitionInline(admin.TabularInline):
    show_change_link = True
    model = InterfaceDefinition

class SystemAdmin(admin.ModelAdmin):
    inlines = [InterfaceDefinitionInline]
    list_display = ["name", "description"]

admin.site.register(System, SystemAdmin)


# -------------------------------------------------------------------
# DateSetType page with InterfaceDefinition
# -------------------------------------------------------------------

class DataSetTypeAdmin(admin.ModelAdmin):
    inlines = [InterfaceDefinitionInline]
    list_display = ["name", "description"]

admin.site.register(DataSetType, DataSetTypeAdmin)


# -------------------------------------------------------------------
# InterfaceDefinition
# -------------------------------------------------------------------

class InterfaceCallInline(admin.TabularInline):
    show_change_link = True
    model = InterfaceCall

class InterfaceDefinitionAdmin(admin.ModelAdmin):
    inlines = [InterfaceCallInline]
    list_display = ["name", "description", "interface_type"]

admin.site.register(InterfaceDefinition, InterfaceDefinitionAdmin)




# -------------------------------------------------------------------
# Interface page with Contracts
# -------------------------------------------------------------------

class ReceivedDataAdmin(admin.ModelAdmin):
    list_display = ["interface_call", "seq_nr", "field_01", "field_02"]

admin.site.register(RawData, ReceivedDataAdmin)


# -------------------------------------------------------------------
# InterfaceCall page with Contracts
# -------------------------------------------------------------------

class RawDataInline(admin.TabularInline):
    model = RawData

class InterfaceCallAdmin(admin.ModelAdmin):
    """
    Change the way the list of interface calls looks
    """
    inlines = [RawDataInline]
    list_display = ["date_time_creation", "status", "filename"]

admin.site.register(InterfaceCall, InterfaceCallAdmin)


# -------------------------------------------------------------------
# Contract page
# -------------------------------------------------------------------
class ContractAdmin(admin.ModelAdmin):
    """
    Change the way the list of contracts looks
    """
    list_display = ["contract_nr", "description", "contract_owner"]

admin.site.register(Contract, ContractAdmin)


