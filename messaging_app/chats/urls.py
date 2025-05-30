from django.urls import path,include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework import routers
from .views import ConversationViewSet, UserViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversations")
router.register(r"messages", MessageViewSet, basename="messages")
router.register(r"users", UserViewSet, basename="users")
conversation = NestedDefaultRouter(router, r"conversations", lookup="conversations")

urlpatterns = [
    path('', include(router.urls)),
]
