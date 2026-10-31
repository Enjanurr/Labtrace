from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created for {user.username}. You can now sign in.",
            )
            return redirect("authentication:login")
    else:
        form = RegistrationForm()

    return render(request, "authentication/register.html", {"form": form})


class LabTraceLoginView(LoginView):
    template_name = "authentication/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # logged-in users skip the login page

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name or user.username}!")
        return super().form_valid(form)  # honors a safe ?next= param, else LOGIN_REDIRECT_URL


class LabTraceLogoutView(LogoutView):
    # Redirects to LOGOUT_REDIRECT_URL (login page). Template uses POST + CSRF.
    pass