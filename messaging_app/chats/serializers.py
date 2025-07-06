from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['user_id']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['user_id']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at', 'is_read']
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model"""
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at', 
                 'updated_at', 'participant_count']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

    def get_participant_count(self, obj):
        return obj.participants.count()

class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new conversation"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participant_ids']
        read_only_fields = ['conversation_id']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with ID {user_id} does not exist")
        
        return conversation

class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new message"""
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'message_body']
        read_only_fields = ['message_id']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            if not data['conversation'].participants.filter(user_id=request.user.user_id).exists():
                raise serializers.ValidationError("You are not a participant in this conversation")
        return data
