from typing import List, Tuple, Dict

from rm.models import InterfaceCall, Contract

required_headers = ('Contract nr.', 'Contract status')

defined_headers = dict(
    database_nr          = "Database nr.",
    contract_nr          = "Contract nr.",
    contract_status      = "Contract status",
    description          = "Beschrijving",
    description_contract = "Beschrijving contract",
    category = "Categorie",
    contract_owner = "Contracteigenaar",
    contract_owner_email = "Contracteigenaar-E-mailadres",
    contract_owner_phone_nr = "Contracteigenaar-Telefoon",
    end_date_contract = "Einddatum contract",
    contact_person = "Contactpersoon",
    contact_person_email = "Contactpersoon-E-mailadres",
    contact_person_phone_nr = "Contactpersoon-Telefoon",
    manufacturer = "Fabrikant",
    manufacturer_kvk_nr = "Fabrikant-KvK-nummer",
    manufacturer_address = "Fabrikant-Adres",
    manufacturer_website = "Fabrikant-Website",
    contracted_value = "Gecontracteerde waarde",
    contact_person_name = "Naam contactpersoon",
    service_level_manager = "Service Level Manager",
    service_level_manager_email = "Service Level Manager-E-mailadres",
    service_level_manager_phone_nr = "Service Level Manager-Telefoon",
    service_level_manager_2 = "Service Level Manager 2",
    service_level_manager_2_email = "Service Level Manager 2-E-mailadres",
    service_level_manager_2_phone_nr = "Service Level Manager 2-Telefoon",
    contract_name = "Naam contract",
    last_end_date = "Uiterste einddatum",
    original_end_date = "Oorspronkelijke einddatum (bij toepassing verlenging)",
    notice_period = "Opzegtermijn",
    notice_period_available = "Opzegtermijn aanwezig",
    type = "Soort contract",
    start_date = "Startdatum contract",
)


def register_contract(rownr: int,
                      row_value: Tuple[str],
                      interfaceCall: InterfaceCall,
                      field_positions: Dict[str, int]):

    if rownr > 1:
        contract = Contract(interface_call=interfaceCall,
                            seq_nr=rownr)

        for field in defined_headers:
            attr = getattr(contract, field)
            if isinstance(attr, str):
                setattr(contract, field, "")

        for field in field_positions:
            position = field_positions[field]
            value = row_value[position]
            setattr(contract, field, value)

        contract.save()
