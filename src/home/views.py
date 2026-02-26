from django.shortcuts import render

from .models import PressCut, HomePage

def home_view(request):
    page = HomePage.objects.first()  # ou utilise get_object_or_404
    press_cuts = PressCut.objects.all().order_by('-date')[:3]  # 3 dernières coupures
    return render(request, 'home/home_page.html', {'page': page, 'press_cuts': press_cuts})
