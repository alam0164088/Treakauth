from django.http import JsonResponse

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"detail": "Authentication required"}, status=401)
            if request.user.role not in allowed_roles:
                return JsonResponse({"detail": "Not authorized"}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
