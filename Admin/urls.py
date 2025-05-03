from django.views.static import serve as mediaserve 
from django.urls import path,include , re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('jet/', include('jet.urls', 'jet')), 
    path('auth/',include('main.urls')),
    path('',include('Product.urls')),
    path('front/',include('tmp.urls'))
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
        re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.STATIC_ROOT}),
        re_path(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': settings.MEDIA_ROOT}),
    ]


