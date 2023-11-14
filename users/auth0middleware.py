from django.contrib.auth.models import AnonymousUser

class Auth0Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_info = request.session.get("user")
        if user_info:
            # Here you can create a simple user object. You might need to customize this part.
            request.user = type('User', (object,), {"username": user_info.get("name"), "is_authenticated": True})()
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
