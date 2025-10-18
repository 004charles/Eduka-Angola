from django.shortcuts import render

def biblioteca(request):
    return render(request, 'biblioteca.html')