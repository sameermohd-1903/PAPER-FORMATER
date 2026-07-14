from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from apps.accounts.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=reverse_lazy('accounts:login'), permanent=False)),
    path('dashboard/', dashboard, name='dashboard'),

    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('questions/', include('apps.questions.urls', namespace='questions')),
    path('papers/', include('apps.papers.urls', namespace='papers')),
    path('api/', include('apps.questions.api_urls')),
    path('api/', include('apps.papers.api_urls')),
    path('academic/',include('academic.urls',namespace='academic')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)