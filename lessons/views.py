from django.shortcuts import render, redirect
from .forms import StudentSignUpForm

# # Create your views here.


def home(request):
    return render(request, "home.html")


def sign_up(request):
    # form = SignUpForm()
    return render(request, "sign_up.html")


def sign_up_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            # create user and add to db
            form.save()
            return redirect("home")
            # login(request, user)
            # return redirect("feed")
    else:
        form = StudentSignUpForm()
    return render(request, "sign_up_student.html", {"form": form})
