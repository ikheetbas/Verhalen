from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    interface_call = None
    stage_contract_list = None
    received_data = None