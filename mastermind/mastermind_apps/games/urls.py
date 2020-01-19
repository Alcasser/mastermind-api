from rest_framework.routers import DefaultRouter

from mastermind_apps.games.views import GameViewSet


router = DefaultRouter()
router.register(r'games', GameViewSet, base_name='games')

urlpatterns = router.urls
