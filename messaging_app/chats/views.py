from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from .permissions import (
    IsParticipantOfConversation,
    IsOwnerOfConversation,
    IsOwnerOfMessage
)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Allow anyone to create a user (register)
        but require authentication for other actions
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """Filter users by email or name"""
        queryset = User.objects.all()
        email = self.request.query_params.get('email', None)
        name = self.request.query_params.get('name', None)
        if email is not None:
            queryset = queryset.filter(email__icontains=email)
        if name is not None:
            queryset = queryset.filter(first_name__icontains=name)
        return queryset

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating conversations
    """
    permission_classes = [
        permissions.IsAuthenticated,
        IsParticipantOfConversation,
        IsOwnerOfConversation
    ]
    serializer_class = ConversationSerializer
    lookup_field = 'conversation_id'

    def get_queryset(self):
        """Return conversations for the current user"""
        return self.request.user.conversations.all()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new conversation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save(owner=request.user)
        
        # Add the current user as a participant
        conversation.participants.add(request.user)
        
        # Return the conversation with all its data
        return_serializer = ConversationSerializer(conversation)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation.participants.add(user_id)
            return Response(
                {'message': 'Participant added successfully'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating messages
    """
    permission_classes = [
        permissions.IsAuthenticated,
        IsParticipantOfConversation,
        IsOwnerOfMessage
    ]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Return messages for the current user's conversations"""
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        """Create a new message"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add the sender (current user) to the message
        message = serializer.save(user=request.user)
        
        # Return the message with all its data
        return_serializer = MessageSerializer(message)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response(
            {'message': 'Message marked as read'}, 
            status=status.HTTP_200_OK
        )
