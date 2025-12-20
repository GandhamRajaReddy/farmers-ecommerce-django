from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import OTP
import random


def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        OTP.objects.update_or_create(email=email, defaults={"code": otp_code})

        # Store temporary signup info
        request.session["signup_email"] = email
        request.session["signup_password"] = password

        print("DEBUG OTP:", otp_code)

        return redirect("otp")     # FIXED URL NAME

    return render(request, "accounts/signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Admin redirect FIXED
            if user.is_staff or user.is_superuser:
                return redirect("/admin/")

            return redirect("home")

        # DO NOT override context processor → DO NOT use {}
        context = {"error": "Invalid username or password"}
        return render(request, "accounts/login.html", context)

    return render(request, "accounts/login.html")


def otp_verify(request):
    if request.method == "POST":
        code = "".join([
            request.POST.get("d1"),
            request.POST.get("d2"),
            request.POST.get("d3"),
            request.POST.get("d4"),
            request.POST.get("d5"),
            request.POST.get("d6")
        ])

        email = request.session.get("signup_email")
        password = request.session.get("signup_password")

        if not email or not password:
            messages.error(request, "Session expired. Register again.")
            return redirect("signup")

        if OTP.objects.filter(email=email, code=code).exists():

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            login(request, user)

            OTP.objects.filter(email=email).delete()

            return redirect("home")

        messages.error(request, "Invalid OTP. Try again.")

    return render(request, "accounts/otp_verify.html")


@login_required
def user_dashboard(request):
    return render(request, "accounts/user_dashboard.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
