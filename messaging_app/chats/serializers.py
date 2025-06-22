from .models import User, Conversation, Message
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number']
        read_only_fields = ['user_id']

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""

    sender = UserSerializer(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at', 'created_at']
        read_only_fields = ['message_id', 'sent_at', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model."""

    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    conversation_name = serializers.CharField(required=False)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages', 'conversation_name']
        read_only_fields = ['conversation_id', 'created_at']

    def get_messages(self, obj):
        """Return serialized messages for the conversation."""
        return MessageSerializer(obj.messages.all(), many=True).data
    
    def validate_conversation_name(self, value):
        if not value:
            raise serializers.ValidationError("Conversation name is required.")
        return value
