from django.shortcuts import render

# Create your views here.


def Operator(request):
    return render(request,'new/operator.html')


def Vacancy(request):
    return render(request,'new/vacancy.html')


def Pharm(request):
    return render(request,'new/farmaset.html')


def About(request):
    return render(request,'new/onas.html')