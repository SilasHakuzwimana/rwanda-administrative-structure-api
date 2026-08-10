"""
URL configuration for rwanda_admin_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from location.views_subscription import CreateSubscriptionView, ManageAPIKeysView, ManageOriginsView


# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Solertia Novarum Ltd - Rwanda Administrative API",
        default_version='v1',
        description="""
        Rwanda Administrative Structure API
        
        ## Features
        - Complete administrative hierarchy from Country to Village level
        - Filtering, searching, and pagination support
        - 17,440 total records available
        
        ## Endpoints
        - Countries: /api/v1/countries/
        - Provinces: /api/v1/provinces/
        - Districts: /api/v1/districts/
        - Sectors: /api/v1/sectors/
        - Cells: /api/v1/cells/
        - Villages: /api/v1/villages/
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(
            name="Solertia Novarum Ltd Team",
            email="info.solertianovarumltd@gmail.com"
        ),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("admin/v1/", admin.site.urls),
    path("api/v1/", include("location.urls")),
    
    # Subscription management (requires authentication)
    path('api/v1/subscribe/', CreateSubscriptionView.as_view(), name='subscribe'),
    path('api/v1/keys/', ManageAPIKeysView.as_view(), name='api-keys'),
    path('api/v1/keys/<int:key_id>/', ManageAPIKeysView.as_view(), name='api-key-delete'),
    path('api/v1/origins/', ManageOriginsView.as_view(), name='origins'),
    path('api/v1/origins/<int:origin_id>/', ManageOriginsView.as_view(), name='origin-delete'),
    
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    path('__debug__/', include('debug_toolbar.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
]
