from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it and its messages.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated before proceeding to object-level checks.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation.
        """
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        elif isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        return False

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset to only include conversations and messages the user is a participant of.
        """
        if isinstance(queryset.first(), Conversation):
            return queryset.filter(participants__user_id=request.user.user_id).distinct()
        elif isinstance(queryset.first(), Message):
            return queryset.filter(conversation__participants__user_id=request.user.user_id).distinct()
        return queryset

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user_id == request.user.user_id

class IsOwnerOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow the owner of a conversation to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the conversation
        return obj.owner_id == request.user.user_id

class IsOwnerOfMessage(permissions.BasePermission):
    """
    Custom permission to only allow the owner of a message to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the message
        return obj.user_id == request.user.user_id