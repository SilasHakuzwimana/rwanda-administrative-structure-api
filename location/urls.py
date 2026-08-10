from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *
from .views_token import *

router = DefaultRouter(trailing_slash=True)

router.register(r"countries", CountryViewSet)
router.register(r"provinces", ProvinceViewSet)
router.register(r"districts", DistrictViewSet)
router.register(r"sectors", SectorViewSet)
router.register(r"cells", CellViewSet)
router.register(r"villages", VillageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Token Management Endpoints
    path('auth/register/', register_customer, name='register_customer'),
    path('auth/token/generate/', generate_token, name='generate_token'),
    path('auth/token/validate/', validate_token, name='validate_token'),
    path('auth/token/revoke/', revoke_token, name='revoke_token'),
    path('auth/customer/<int:customer_id>/keys/', list_customer_keys, name='list_customer_keys'),
]
