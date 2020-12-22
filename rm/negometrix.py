import logging
from typing import Tuple, Dict

from rm.constants import SKIPPED, OK, ERROR, NEGOMETRIX, MISSING_ONE_OR_MORE_MANDATORY_FIELDS
from rm.interface_file import ExcelInterfaceFile, row_is_empty, get_fields_with_their_position, \
    register_in_received_data, mandatory_fields_present
from rm.models import InterfaceCall, Contract

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
        return OK, 'Valid Header'

    if row_is_empty(row_values):
        return SKIPPED, 'Skipped empty row'

    if not mandatory_fields_present(mandatory_field_positions,
                                    row_values):
        return ERROR, MISSING_ONE_OR_MORE_MANDATORY_FIELDS

    contract = Contract(interface_call=interfaceCall,
                        seq_nr=row_nr)

    for field in fields_with_position:
        position = fields_with_position[field]
        value = row_values[position]
        setattr(contract, field, value)

    contract.save()

    return OK, "Valid Contract"


class NegometrixInterfaceFile(ExcelInterfaceFile):

    mandatory_headers = ('Contract nr.', 'Contract status')
    mandatory_fields = ('contract_nr', 'contract_status')

    def __init__(self, file, interfaceCall: InterfaceCall):
        super().__init__(file, interfaceCall)

    def get_fields_with_their_position(self, found_headers: Tuple[str]) \
            -> Dict[str, int]:
        return get_fields_with_their_position(found_headers, defined_headers)

    def get_interface_system(self):
        return NEGOMETRIX

    def handle_row(self,
                   row_nr: int,
                   row_values: Tuple[str],
                   interfaceCall: InterfaceCall,
                   field_positions: Dict[str, int],
                   mandatory_field_positions: Tuple[int]):
        logger.debug(f"register ReceivedData {row_nr} - {row_values}")

        receivedData = register_in_received_data(row_nr,
                                                 row_values,
                                                 interfaceCall)
        try:
            status, message = register_contract(row_nr,
                                                row_values,
                                                interfaceCall,
                                                field_positions,
                                                mandatory_field_positions)
        except Exception as ex:
            receivedData.status = ERROR
            receivedData.message = str(ex)
        else:
            receivedData.status = status
            receivedData.message = message
        receivedData.save()

    def get_mandatory_fields(self):
        return self.mandatory_fields
