# script/views.py
from django.shortcuts import render
from django.views.defaults import page_not_found, server_error

def custom_page_not_found(request, exception=None):
    return page_not_found(request, exception, template_name='404.html')

    
def custom_server_error(request, *args, **kwargs):
    return server_error(request)
