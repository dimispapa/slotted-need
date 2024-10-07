from django.shortcuts import render


# View that renders the home template
def home(request):
    return render(request, 'home.html')
