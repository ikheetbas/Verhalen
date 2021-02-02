from django.contrib import admin
from rm.models import StageContract, InterfaceCall, RawData, System, DataSetType, InterfaceDefinition, DataPerOrgUnit, \
    Mapping


# STATIC TOTAL_DATA_ROWS_RECEIVED

# -------------------------------------------------------------------
# System page with InterfaceDefinition and Mappings
# -------------------------------------------------------------------
class InterfaceDefinitionInline(admin.TabularInline):
    show_change_link = True
    model = InterfaceDefinition


class MappingInline(admin.TabularInline):
    show_change_link = True
    model = Mapping

class SystemAdmin(admin.ModelAdmin):
    inlines = [InterfaceDefinitionInline, MappingInline]
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


# PROCESS TOTAL_DATA_ROWS_RECEIVED

# -------------------------------------------------------------------
# Interface page with Contracts
# -------------------------------------------------------------------

class ReceivedDataAdmin(admin.ModelAdmin):
    list_display = ["interface_call", "seq_nr", "field_01", "field_02"]

admin.site.register(RawData, ReceivedDataAdmin)


# -------------------------------------------------------------------
# InterfaceCall page with Raw Data
# -------------------------------------------------------------------

class RawDataInline(admin.TabularInline):
    model = RawData


class DataPerOrgUnitInline(admin.TabularInline):
    model = DataPerOrgUnit

class InterfaceCallAdmin(admin.ModelAdmin):
    """
    Change the way the list of interface calls looks
    """
    inlines = [RawDataInline, DataPerOrgUnitInline]
    list_display = ["date_time_creation", "status", "filename"]

admin.site.register(InterfaceCall, InterfaceCallAdmin)

# -------------------------------------------------------------------
# DataPerOrgUnit page with Contracts
# -------------------------------------------------------------------
class ContractInline(admin.TabularInline):
    show_change_link = True
    model = StageContract
    fields = ('seq_nr','contract_nr', 'contract_status', 'contract_name')

class DataPerOrgUnitAdmin(admin.ModelAdmin):
    inlines = [ContractInline]
    pass

admin.site.register(DataPerOrgUnit, DataPerOrgUnitAdmin)


# -------------------------------------------------------------------
# StageContract page
# -------------------------------------------------------------------
class ContractAdmin(admin.ModelAdmin):
    """
    Change the way the list of contracts looks
    """
    list_display = ["contract_nr", "description", "contract_owner"]

admin.site.register(StageContract, ContractAdmin)


