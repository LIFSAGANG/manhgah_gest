from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
import threading

# Thread-local storage for request
_request_context = threading.local()

# Cache local des permissions par utilisateur (vidé à la déconnexion)
_permissions_cache = {}


def get_user_permissions(user):
    """Retourne le set des codes de permissions de l'utilisateur.
    Superuser a tout. Sinon basé sur le rôle."""
    if user.is_superuser:
        return {'__all__'}  # Token spécial = accès total

    if not user.is_authenticated:
        return set()

    cache_key = user.pk
    if cache_key in _permissions_cache:
        return _permissions_cache[cache_key]

    try:
        from core.models import RolePermission
        profile = user.utilisateurprofile
        if not profile.actif:
            return set()
        codes = set(
            RolePermission.objects.filter(role=profile.role)
            .values_list('permission__code_permission', flat=True)
        )
        _permissions_cache[cache_key] = codes
        return codes
    except Exception:
        return set()


def clear_permissions_cache(user_pk):
    """Vide le cache permissions d'un utilisateur (appeler après modification du rôle)"""
    _permissions_cache.pop(user_pk, None)


def has_permission(user, code):
    """Vérifie si l'utilisateur a la permission 'code'"""
    perms = get_user_permissions(user)
    return '__all__' in perms or code in perms


def permission_required(code):
    """Décorateur de vue : refuse l'accès si l'utilisateur n'a pas la permission 'code'"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not has_permission(request.user, code):
                messages.error(request, "Accès refusé : vous n'avez pas la permission nécessaire.")
                return redirect('accueil')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def user_permissions_processor(request):
    """Context processor : injecte les permissions dans tous les templates"""
    if request.user.is_authenticated:
        perms = get_user_permissions(request.user)
        return {
            'user_perms': perms,
            'user_is_admin': request.user.is_superuser or '__all__' in perms,
        }
    return {'user_perms': set(), 'user_is_admin': False}


class ActivityLogMiddleware(MiddlewareMixin):
    """Middleware to capture request information for activity logging"""

    def process_request(self, request):
        """Store request in thread-local storage for signal handlers"""
        _request_context.request = request
        return None

    def process_response(self, request, response):
        """Clean up thread-local storage"""
        if hasattr(_request_context, 'request'):
            delattr(_request_context, 'request')
        return response


def get_current_request():
    """Get the current request from thread-local storage"""
    return getattr(_request_context, 'request', None)
