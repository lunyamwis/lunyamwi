import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import View

from .forms import EmailSignupForm
from .models import Signup

logger = logging.getLogger(__name__)


class EmailSignupView(View):
    """Handle newsletter subscription."""

    def post(self, request, *args, **kwargs):
        form = EmailSignupForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please enter a valid email address.")
            logger.warning("Invalid email signup attempt: %s", request.POST.get("email"))
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        email = form.cleaned_data["email"]

        if Signup.objects.filter(email=email).exists():
            messages.warning(request, "You are already subscribed to the newsletter.")
            logger.info("Duplicate subscription attempt for: %s", email)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        Signup.objects.create(email=email)
        messages.success(request, "Welcome aboard! You have successfully subscribed.")
        logger.info("New newsletter subscription: %s", email)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def email_list_signup(request):
    """Function-based wrapper kept for URL compatibility."""
    if request.method == "POST":
        return EmailSignupView.as_view()(request)
    return redirect("home")
