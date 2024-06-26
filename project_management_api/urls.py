from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view

# schema_view = get_schema_view(
#     openapi.Info(
#         title= 'Taskify API',
#         default_version='v1',
#         description='API for effective project management',
#         contact=openapi.Contact(name='Joboy-Dev', email="oluwakoredeadegbehingbe@gmail.com"),
#         # license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny]
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('user/', include('user.urls')),
    path('workspace/', include('workspace.urls')),
    path('project/', include('project.urls')),
    path('team/', include('team.urls')),
    path('task/', include('task.urls')),
    path('comment/', include('comment.urls')),
    path('notification/', include('notification.urls')),
    
    # path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    