from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="PP ProcurementProject API",
        default_version='v1',
        description="Front end devs hoping to use our service.",
        terms_of_service="unavailable right now!",
        contact=openapi.Contact(email="adeitanemanuel086@gmail.com"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),

    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
        name='schema-swagger-ui'),

    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'), 
]
