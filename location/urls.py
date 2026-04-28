from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r"countries", CountryViewSet)
router.register(r"provinces", ProvinceViewSet)
router.register(r"districts", DistrictViewSet)
router.register(r"sectors", SectorViewSet)
router.register(r"cells", CellViewSet)
router.register(r"villages", VillageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
