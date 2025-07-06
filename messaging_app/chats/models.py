from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import uuid


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    first_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2, "First name must be at least 2 characters long")]
    )
    last_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2, "Last name must be at least 2 characters long")]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'chats_user'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Conversation(models.Model):
    """Model to track conversations between users"""
    
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chats_conversation'
        ordering = ['-updated_at']

    def __str__(self):
        participants = list(self.participants.all()[:2])
        names = [user.get_full_name() for user in participants]
        if self.participants.count() > 2:
            names.append(f"and {self.participants.count() - 2} others")
        return f"Conversation: {', '.join(names)}"


class Message(models.Model):
    """Model to store messages in conversations"""
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_body = models.TextField(help_text='The body of the message')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'chats_message'
        ordering = ['-sent_at']

    def clean(self):
        if not self.message_body.strip():
            raise ValidationError('Message content cannot be empty')

    def __str__(self):
        return f"Message from {self.sender.first_name} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

    def get_sender_name(self):
        """Return the full name of the message sender."""
        return f"{self.sender.first_name} {self.sender.last_name}"
