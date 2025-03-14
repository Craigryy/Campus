from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.static import serve

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from home.views import home_css_view

from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path('welcome_page_img.css', home_css_view, name='home_css_view'),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# For anything not caught by a more specific rule above, hand over to
# Wagtail's page serving mechanism. This should be the last pattern in
# the list:
urlpatterns += [
    path("", include(wagtail_urls)),
    path("__debug__/", include("debug_toolbar.urls")),
]

if not settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>/', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
