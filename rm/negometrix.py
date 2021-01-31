import logging
from typing import Tuple, Dict

from django.contrib.auth import get_user_model

import rm
from rm.constants import NEGOMETRIX, MISSING_ONE_OR_MORE_MANDATORY_FIELDS, CONTRACTEN, RowStatus
from rm.interface_file import ExcelInterfaceFile, row_is_empty, get_fields_with_their_position, \
    mandatory_fields_present, get_org_unit, fill_fields_in_record_from_row_values
from rm.models import InterfaceCall, Contract, System, DataSetType, InterfaceDefinition
from users.models import OrganizationalUnit, CustomUser

logger = logging.getLogger(__name__)

defined_headers = dict(
    database_nr="Database nr.",
    contract_nr="Contract nr.",
    contract_status="Contract status",
    description="Beschrijving",
    description_contract="Beschrijving contract",
    category="Categorie",
    contract_owner="Contracteigenaar",
    contract_owner_email="Contracteigenaar-E-mailadres",
    contract_owner_phone_nr="Contracteigenaar-Telefoon",
    end_date_contract="Einddatum contract",
    contact_person="Contactpersoon",
    contact_person_email="Contactpersoon-E-mailadres",
    contact_person_phone_nr="Contactpersoon-Telefoon",
    manufacturer="Fabrikant",
    manufacturer_kvk_nr="Fabrikant-KvK-nummer",
    manufacturer_address="Fabrikant-Adres",
    manufacturer_website="Fabrikant-Website",
    contracted_value="Gecontracteerde waarde",
    contact_person_name="Naam contactpersoon",
    service_level_manager="Service Level Manager",
    service_level_manager_email="Service Level Manager-E-mailadres",
    service_level_manager_phone_nr="Service Level Manager-Telefoon",
    service_level_manager_2="Service Level Manager 2",
    service_level_manager_2_email="Service Level Manager 2-E-mailadres",
    service_level_manager_2_phone_nr="Service Level Manager 2-Telefoon",
    contract_name="Naam contract",
    last_end_date="Uiterste einddatum",
    original_end_date="Oorspronkelijke einddatum (bij toepassing verlenging)",
    notice_period="Opzegtermijn",
    notice_period_available="Opzegtermijn aanwezig",
    type="Soort contract",
    start_date="Startdatum contract",
)


def handle_negometrix_file_row(row_nr: int,
                               row_values: Tuple[str, ...],
                               interface_call: InterfaceCall,
                               fields_with_position: Dict[str, int],
                               mandatory_field_positions: Tuple[int, ...]) -> Tuple[RowStatus, str]:
    if row_nr == 1:
        return RowStatus.HEADER_ROW, 'Header'

    if row_is_empty(row_values):
        return RowStatus.EMPTY_ROW, 'Skipped empty row'

    if not mandatory_fields_present(mandatory_field_positions,
                                    row_values):
        return RowStatus.DATA_ERROR, MISSING_ONE_OR_MORE_MANDATORY_FIELDS

    contract = Contract(seq_nr=row_nr)

    fill_fields_in_record_from_row_values(contract, fields_with_position, row_values)

    if not contract.category or contract.category == "":
        return RowStatus.DATA_ERROR, "Categorie is leeg, dus kan dit contract niet aan " \
                                     "een organisatieonderdeel gekoppeld worden"

    system = interface_call.interface_definition.system
    org_unit = get_org_unit(system, contract.category)
    if not org_unit:
        return RowStatus.DATA_ERROR, f"Voor categorie '{contract.category}' kan geen " \
                                     f"organisatieonderdeel gevonden worden voor {system.name}"
    if not interface_call.user:
        msg = "Zou niet mogen voorkomen bij het inlezen, InterfaceCall heeft geen 'user'"
        logger.error(f"{msg} bij interface_call.id:{interface_call.pk}")
        return RowStatus.DATA_ERROR, msg

    if not interface_call.user.is_authorized_for_org_unit(org_unit):
        return RowStatus.DATA_IGNORED, \
               f"Gebruiker is niet geautoriseerd voor het organisatieonderdeel van dit contract ({org_unit.name})"

    # find and set data_per_org_unit
    data_per_org_unit, created = interface_call.dataperorgunit_set.get_or_create(org_unit=org_unit)
    contract.data_per_org_unit = data_per_org_unit

    contract.save()

    logger.debug(f"Created Contract: {contract.__str__()}")

    return RowStatus.DATA_OK, "Valid Contract"


class NegometrixInterfaceFile(ExcelInterfaceFile):
    mandatory_headers = ('Contract nr.', 'Contract status')
    mandatory_fields = ('contract_nr', 'contract_status')
    interface_definition: InterfaceDefinition = None

    def __init__(self, file):

        super().__init__(file)

    def _set_interface_definition(self):
        logger.debug(f"Trying to get InterfaceDefinition "
                     f"for system {NEGOMETRIX} for datasettype {CONTRACTEN}")
        try:
            system = System.objects.get(name=NEGOMETRIX)
            logger.debug(f"Found System: {system}")
            data_set_type = DataSetType.objects.get(name=CONTRACTEN)
            logger.debug(f"Found DataSetType: {data_set_type}")
            self.interface_definition = InterfaceDefinition.objects.get(system=system,
                                                                        data_set_type=data_set_type,
                                                                        interface_type=InterfaceDefinition.UPLOAD)
            logger.debug(f"Found InterfaceDefinition: {self.interface_definition}")
        except rm.models.System.DoesNotExist as ex:
            msg = f"System {NEGOMETRIX} is niet geregistreerd, waarschuw Admin"
            logger.error(msg)
            raise rm.models.System.DoesNotExist(msg)
        except rm.models.DataSetType.DoesNotExist as ex:
            msg = f"DataSetType {CONTRACTEN} is niet geregistreerd, waarschuw Admin"
            logger.error(msg)
            raise rm.models.DataSetType.DoesNotExist(msg)
        except rm.models.InterfaceDefinition.DoesNotExist as ex:
            msg = f"Interface definitie {NEGOMETRIX} voor {CONTRACTEN} type {InterfaceDefinition.UPLOAD} " \
                  f"is niet geregistreerd, waarschuw Admin"
            logger.error(msg)
            raise rm.models.InterfaceDefinition.DoesNotExist(msg)
        except Exception as ex:
            msg = (f"Unexpected Error in static data: there is no InterfaceDefinition "
                   f"for system {NEGOMETRIX} for datasettype {CONTRACTEN} "
                   f"\n ExceptionType {type(ex)}, message: {ex.__str__()}")
            logger.error(msg)
            raise Exception(msg)

    def get_fields_with_their_position(self, found_headers: Tuple[str]) \
            -> Dict[str, int]:
        return get_fields_with_their_position(found_headers, defined_headers)

    def get_interface_definition(self):
        if not self.interface_definition:
            self._set_interface_definition()
        return self.interface_definition

    def get_mandatory_fields(self):
        return self.mandatory_fields

    def register_business_data(self,
                               row_nr: int,
                               row_values: Tuple[str, ...],
                               interface_call: InterfaceCall,
                               fields_with_position: Dict[str, int],
                               mandatory_field_positions: Tuple[int, ...]) -> Tuple[RowStatus, str]:

        # call a function, which makes it easier to unit test, could not do that direct
        # since we wanted an abstract method to force subclasses to implement it.

        return handle_negometrix_file_row(row_nr,
                                          row_values,
                                          interface_call,
                                          fields_with_position,
                                          mandatory_field_positions)
