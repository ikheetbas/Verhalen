import logging
from typing import Tuple, Dict

import rm
from rm.constants import SKIPPED, OK, ERROR, NEGOMETRIX, MISSING_ONE_OR_MORE_MANDATORY_FIELDS, CONTRACTEN
from rm.interface_file import ExcelInterfaceFile, row_is_empty, get_fields_with_their_position, \
    register_in_raw_data, mandatory_fields_present, get_org_unit
from rm.models import InterfaceCall, Contract, System, DataSetType, InterfaceDefinition

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


def register_contract(row_nr: int,
                      row_values: Tuple[str],
                      interfaceCall: InterfaceCall,
                      fields_with_position: Dict[str, int],
                      mandatory_field_positions: Tuple[int]) -> Tuple[str, str]:
    if row_nr == 1:
        return OK, 'Header'

    if row_is_empty(row_values):
        return SKIPPED, 'Skipped empty row'

    if not mandatory_fields_present(mandatory_field_positions,
                                    row_values):
        return ERROR, MISSING_ONE_OR_MORE_MANDATORY_FIELDS


    contract = Contract(seq_nr=row_nr)

    # set all fields in a generic way
    for field in fields_with_position:
        position = fields_with_position[field]
        value = row_values[position]
        setattr(contract, field, value)

    # set up link with DataPerOrgUnit
    system = interfaceCall.interface_definition.system
    if not contract.category or contract.category == "":
        return ERROR, "Categorie is leeg, dus kan dit contract niet aan " \
                      "een organisatieonderdel gekoppeld worden"
    org_unit = get_org_unit(system, contract.category)
    if not org_unit:
        return ERROR, f"Voor categorie '{contract.category}' kan geen " \
                      f"organisatieonderdeel gevonden worden voor {system.name} "

    data_per_org_unit, created = interfaceCall.dataperorgunit_set.get_or_create(org_unit=org_unit)
    if created:
        logger.debug(f"Created Data Org Per Unit: {data_per_org_unit.__str__()}")
    else:
        logger.debug(f"Found Data Org Per Unit: {data_per_org_unit.__str__()}")

    contract.data_per_org_unit = data_per_org_unit

    # save the bastard!
    contract.save()

    logger.debug(f"Created Contract: {contract.__str__()}")

    return OK, "Valid Contract"


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
                                                                        dataset_type=data_set_type,
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


    def handle_row(self,
                   row_nr: int,
                   row_values: Tuple[str],
                   interfaceCall: InterfaceCall,
                   field_positions: Dict[str, int],
                   mandatory_field_positions: Tuple[int]):
        logger.debug(f"register RawData {row_nr} - {row_values}")

        raw_data = register_in_raw_data(row_nr,
                                        row_values,
                                        interfaceCall)
        try:
            status, message = register_contract(row_nr,
                                                row_values,
                                                interfaceCall,
                                                field_positions,
                                                mandatory_field_positions)
        except Exception as ex:
            raw_data.status = ERROR
            raw_data.message = str(ex)
        else:
            raw_data.status = status
            raw_data.message = message
        logger.debug(f"Result register Contact {row_nr} : {raw_data.status} : {raw_data.message}")
        raw_data.save()

    def get_mandatory_fields(self):
        return self.mandatory_fields
