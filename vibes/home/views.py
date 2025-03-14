from django.shortcuts import render
from django.http import HttpResponse

def home_css_view(request):
    return render(request, 'welcome_page_img.css.html', content_type='text/css')
