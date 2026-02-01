from django.shortcuts import render



def home_centro(request):
    return render(request, 'home_centro.html')