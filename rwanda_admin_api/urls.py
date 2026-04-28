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


# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="iTechnology - Rwanda Administrative API",
        default_version='v1',
        description="""
        Rwanda Administrative Structure API
        
        ## Features
        - Complete administrative hierarchy from Country to Village level
        - Filtering, searching, and pagination support
        - 17,440 total records available
        
        ## Endpoints
        - Countries: /api/countries/
        - Provinces: /api/provinces/
        - Districts: /api/districts/
        - Sectors: /api/sectors/
        - Cells: /api/cells/
        - Villages: /api/villages/
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(
            name="iTechnology Development Team",
            email="infinitytechnologiesltd8@gmail.com"
        ),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("location.urls")),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
