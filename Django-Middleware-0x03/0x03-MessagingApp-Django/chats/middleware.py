import logging
from datetime import datetime
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure the logger
        self.logger = logging.getLogger('request_logger')
        handler = logging.FileHandler('requests.log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "AnonymousUser"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Allow access only between 18 (6PM) and 21 (9PM) inclusive
        if not (18 <= current_hour <= 21):
            return HttpResponseForbidden("Access to the messaging app is only allowed between 6PM and 9PM.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_tracker = {}  # { ip: [timestamps] }

    def __call__(self, request):
        if request.path.startswith('/api/messages/') and request.method == 'POST':
            ip = self.get_client_ip(request)
            now = datetime.now()

            if ip not in self.ip_tracker:
                self.ip_tracker[ip] = []

            # Remove timestamps older than 1 minute
            self.ip_tracker[ip] = [t for t in self.ip_tracker[ip] if now - t < timedelta(minutes=1)]

            if len(self.ip_tracker[ip]) >= 5:
                return HttpResponseForbidden("Rate limit exceeded: You can only send 5 messages per minute.")

            self.ip_tracker[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ['/api/messages/', '/api/conversations/']  # You can adjust this

        if any(request.path.startswith(path) for path in protected_paths):
            user = request.user
            if not user.is_authenticated:
                return HttpResponseForbidden("Authentication required.")

            user_role = getattr(user, 'role', None)

            if not (user.is_superuser or user_role in ['admin', 'moderator']):
                return HttpResponseForbidden("Access denied: Admin or Moderator required.")

        return self.get_response(request)
