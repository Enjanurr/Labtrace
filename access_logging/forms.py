from django import forms
from django.conf import settings

from authentication.forms import INPUT_CLASSES

from .models import LabVisit


class CheckInForm(forms.ModelForm):
    class Meta:
        model = LabVisit
        fields = ("lab_location", "purpose")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lab list comes from settings so audit filters stay consistent.
        locations = [(loc, loc) for loc in settings.LAB_LOCATIONS]
        self.fields["lab_location"] = forms.ChoiceField(
            label="Lab location",
            choices=[("", "Select a lab...")] + locations,
        )
        self.fields["purpose"].choices = [("", "Select a purpose...")] + list(
            LabVisit.Purpose.choices
        )

        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES