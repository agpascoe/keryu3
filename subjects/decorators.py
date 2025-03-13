from django.core.exceptions import PermissionDenied
from functools import wraps

def staff_member_required_403(view_func):
    """
    Decorator for views that checks that the user is a staff member,
    returning 403 Forbidden instead of redirecting to the login page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view 