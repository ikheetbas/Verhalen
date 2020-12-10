from typing import List, Tuple, Dict

from rm.constants import SKIPPED, OK, ERROR
from rm.models import InterfaceCall, Contract

mandatory_headers = ('Contract nr.', 'Contract status')
mandatory_fields = ('contract_nr', 'contract_status')

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


def row_is_empty(row_values: Tuple[str]) -> bool:
    return row_values.count(None) == len(row_values)


def mandatory_fields_present(mandatory_field_positions: Tuple[int],
                             row_values: Tuple[str]) -> bool:
    """
    Checks in the mandatory fields in the row have a value. If a mandatory field contains
    a None or "" a False is returned.
    """
    for position in mandatory_field_positions:
        value_to_be_checked = row_values[position]
        if not value_to_be_checked:
            return False
        if row_values[position] == "":
            return False
    return True


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
        return (ERROR, f'Missing one or more mandatory fields: '
                       f'{mandatory_fields}')

    contract = Contract(interface_call=interfaceCall,
                        seq_nr=row_nr)

    for field in fields_with_position:
        position = fields_with_position[field]
        value = row_values[position]
        setattr(contract, field, value)

    contract.save()

    return OK, "Valid Contract"
