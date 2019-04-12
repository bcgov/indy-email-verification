from django import forms

from .models import Verification


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class EmailForm(BaseForm):
    class Meta:
        model = Verification
        fields = ["email"]
