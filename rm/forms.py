from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    interface_call_id = None
    interface_call = None
    stage_contract_list = None
    received_data = None

class DatasetForm(forms.Form):
    dpou_id = None
    stage_contract_list = None
    received_data = None