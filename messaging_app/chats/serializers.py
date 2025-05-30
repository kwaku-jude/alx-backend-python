from rest_framework import serializers
from .models import User, Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        models = Conversation
        fields = ("conversation_id", "participants")


class UserSerializer(serializers.ModelSerializer):
    conversations = ConversationSerializer(many=True)
    full_name = serializers.SerializerMethodField()
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        models = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "conversations",
            "password",
            "password_confirm",
        )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    
    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password_confirm"]
        
        if password != password2:
            raise serializers.ValidationError()
        
        return attrs
    


class MessageSerializer(serializers.ModelSerializer):
    models = Message
    fields = (
        "message_id",
        "message_body",
        "sent_at",
        "created_at",
    )
