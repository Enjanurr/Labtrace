from django import forms

from authentication.forms import INPUT_CLASSES

from .models import Asset, Condition, EquipmentLog

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _check_image(img):
    if not img:
        return img
    if img.size > MAX_IMAGE_BYTES:
        raise forms.ValidationError("Image must be 5 MB or smaller.")
    content_type = getattr(img, "content_type", None)
    if content_type and content_type not in ALLOWED_IMAGE_TYPES:
        raise forms.ValidationError("Only JPG, PNG or WebP images are allowed.")
    return img


class BorrowForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("asset", "pre_condition", "pre_condition_img")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset"].queryset = Asset.objects.filter(
            availability_status=Asset.Availability.AVAILABLE
        ).order_by("asset_code")
        self.fields["asset"].empty_label = "Select equipment..."

        # You can't borrow something that is already missing.
        self.fields["pre_condition"].choices = [("", "Select condition...")] + [
            c for c in Condition.choices if c[0] != Condition.MISSING
        ]
        self.fields["pre_condition"].label = "Condition before borrowing"
        self.fields["pre_condition_img"].label = "Photo of the item"
        self.fields["pre_condition_img"].help_text = (
            "Required if the item is not in good condition. JPG/PNG/WebP, max 5 MB."
        )
        self.fields["pre_condition_img"].widget.attrs["accept"] = "image/*"

        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_pre_condition_img(self):
        return _check_image(self.cleaned_data.get("pre_condition_img"))

    def clean(self):
        cleaned = super().clean()
        cond = cleaned.get("pre_condition")
        if cond and cond != Condition.GOOD and not cleaned.get("pre_condition_img"):
            self.add_error(
                "pre_condition_img", "Attach a photo to document the item's condition."
            )
        return cleaned


class ReturnForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("post_condition", "post_condition_img")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["post_condition"].required = True
        self.fields["post_condition"].choices = [
            ("", "Select condition...")
        ] + list(Condition.choices)
        self.fields["post_condition"].label = "Condition on return"
        self.fields["post_condition_img"].label = "Proof photo"
        self.fields["post_condition_img"].help_text = (
            "Required unless the item is Good or Missing. JPG/PNG/WebP, max 5 MB."
        )
        self.fields["post_condition_img"].widget.attrs["accept"] = "image/*"

        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_post_condition_img(self):
        return _check_image(self.cleaned_data.get("post_condition_img"))

    def clean(self):
        cleaned = super().clean()
        cond = cleaned.get("post_condition")
        if (
            cond in (Condition.DAMAGED, Condition.MALFUNCTIONING)
            and not cleaned.get("post_condition_img")
        ):
            self.add_error(
                "post_condition_img", "Attach a photo showing the damage or fault."
            )
        return cleaned


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ("asset_code", "name", "availability_status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status = self.fields["availability_status"]
        if self.instance.pk and self.instance.availability_status == Asset.Availability.BORROWED:
            # Borrowed status is controlled by the borrow/return flow only.
            status.disabled = True
            status.help_text = "Currently borrowed. Status changes when it is returned."
        else:
            status.choices = [
                c for c in Asset.Availability.choices if c[0] != Asset.Availability.BORROWED
            ]
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_asset_code(self):
        return self.cleaned_data["asset_code"].strip().upper()