# messaging/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class MessagingTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='pass')
        self.recipient = User.objects.create_user(username='recipient', password='pass')

    def test_message_creation_triggers_notification(self):
        msg = Message.objects.create(sender=self.sender, recipient=self.recipient, content="Hello")
        notif = Notification.objects.get(user=self.recipient, message=msg)
        self.assertIsNotNone(notif)
        self.assertFalse(notif.read)

    def test_edit_message_creates_history(self):
        msg = Message.objects.create(sender=self.sender, recipient=self.recipient, content="Original")
        msg.content = "Edited version"
        msg.save()

        history = MessageHistory.objects.filter(message=msg)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().old_content, "Original")