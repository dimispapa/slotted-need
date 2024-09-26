from functools import wraps
from django.http import JsonResponse


def ajax_login_required_no_redirect(view_func):
    """
    Decorator that checks if the user is authenticated.
    Returns a JSON response if not authenticated.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'messages': [{
                    'level': 40,
                    'level_tag': 'error',
                    'message': 'Authentication required.'
                }]
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ajax_admin_required_no_redirect(view_func):
    """
    Decorator that checks if the user has admin privileges.
    Returns a JSON response if not authorized.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'messages': [{
                    'level': 40,
                    'level_tag': 'error',
                    'message':
                        'You do not have permission to perform this action.'
                }]
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
