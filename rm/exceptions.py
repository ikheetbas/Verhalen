class OtherActiveDataPerOrgUnitException(Exception):

    def __init__(self, id: int, datasettype_name: str, org_unit_name: str):
        self.datasettype_name = datasettype_name
        self.org_unit_name = org_unit_name

    def __str__(self):
        return f"Deze dataset (pk={id}) kan niet geactiveerd worden. " \
               f"Een andere dataset met {self.datasettype_name} is nog actief voor {self.org_unit_name}"


class DuplicateKeyException(Exception):

    def __init__(self, table: str, seq_nr: int, field_name: str, value, to_string: str):
        self.to_string = to_string
        self.seq_nr = seq_nr
        self.table = table
        self.field_name = field_name
        self.value = value

    def __str__(self):
        return f"Duplicate Key in tabel: {self.table}, veld: {self.field_name} inhoud: {self.value} " \
               f"oorsprong rij {self.seq_nr}, omschr: {self.to_string} "

