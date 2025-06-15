from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Prefetch, Q
from django.views.decorators.cache import cache_page
from .models import Message

User = get_user_model()


@login_required
def delete_user(request):
    """
    Allow logged-in user to delete their account via POST request only.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')
    else:
        return HttpResponseForbidden("You must submit a POST request to delete your account.")


@cache_page(60)
@login_required
def conversation_detail(request, message_id):
    """
    Display the details of a message and its threaded replies.
    This view is cached for 60 seconds to improve performance.
    Note: Marking the message as read will not take effect immediately due to caching.
    """
    user = request.user
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
        .prefetch_related(
            Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
        )
        .filter(Q(sender=user) | Q(receiver=user)),
        pk=message_id
    )

    def get_threaded_replies(message):
        replies = Message.objects.filter(parent_message=message).select_related('sender', 'receiver')
        return [{
            'message': reply,
            'replies': get_threaded_replies(reply)
        } for reply in replies]

    threaded_replies = get_threaded_replies(message)

    context = {
        'message': message,
        'threaded_replies': threaded_replies,
    }
    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def unread_messages(request):
    """
    Display all unread messages for the logged-in user.
    Uses .only() to optimize the query.
    """
    user = request.user
    unread_messages = Message.unread.unread_for_user(user).only('id', 'content', 'timestamp', 'sender_id')
    context = {
        'unread_messages': unread_messages
    }
    return render(request, 'messaging/unread_messages.html', context)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['delete'], url_path='custom-delete')
    def delete_user(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)

    @method_decorator(cache_page(60))
    def get_conversation(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread_messages = Message.unread.unread_for_user(request.user).only('sender_id', 'content', 'timestamp').select_related('sender')
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inbox(request):
            messages = Message.objects.filter(sender=request.user).select_related('sender', 'receiver').prefetch_related('replies')
            serializer = MessageSerializer(messages, many=True)
            return JsonResponse(serializer.data, safe=False)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
    return Notification.objects.filter(recipient=self.request.user)


class MessageHistoryViewSet(viewsets.ModelViewSet):
    queryset = MessageHistory.objects.all()
    serializer_class = MessageHistorySerializer
