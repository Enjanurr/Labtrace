from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import validate_institutional_email

User = get_user_model()

INPUT_CLASSES = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-14 "
    "text-sm text-slate-900 placeholder-slate-400 shadow-sm "
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Institutional email",
        help_text="Must be an institutional address, e.g. juan.delacruz@cit.edu",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        self.fields["username"].help_text = "Letters, digits and @/./+/-/_ only."
        self.fields["password1"].help_text = (
            "At least 8 characters. Not too common, not all numbers."
        )
        self.fields["password2"].help_text = "Enter the same password again."

        placeholders = {
            "username": "jdelacruz",
            "first_name": "Juan",
            "last_name": "Dela Cruz",
            "email": "name@cit.edu",
            "password1": "Create a password",
            "password2": "Repeat the password",
        }
        autocompletes = {
            "username": "username",
            "first_name": "given-name",
            "last_name": "family-name",
            "email": "email",
            "password1": "new-password",
            "password2": "new-password",
        }
        for name, field in self.fields.items():
            field.widget.attrs["class"] = INPUT_CLASSES
            field.widget.attrs["placeholder"] = placeholders.get(name, "")
            field.widget.attrs["autocomplete"] = autocompletes.get(name, "off")

        # Single source of truth for the jQuery live hint in main.js
        self.fields["email"].widget.attrs["data-allowed-domains"] = ",".join(
            getattr(settings, "ALLOWED_EMAIL_DOMAINS", ["cit.edu"])
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        validate_institutional_email(email)  # raises ValidationError on bad domain
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists.", code="duplicate_email"
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)  # password is hashed here
        user.role = User.Role.STUDENT      # never trust self-selected roles
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Invalid username/email or password.",
        "inactive": "This account has been deactivated. Contact an administrator.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username or email"
        self.fields["username"].widget.attrs.update(
            {
                "class": INPUT_CLASSES,
                "placeholder": "jdelacruz or name@cit.edu",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": INPUT_CLASSES,
                "placeholder": "Your password",
                "autocomplete": "current-password",
            }
        )

    def clean_username(self):
        """Allow signing in with either username or email."""
        value = self.cleaned_data["username"].strip()
        if "@" in value:
            match = User.objects.filter(email__iexact=value).first()
            if match:
                return match.get_username()
        return value