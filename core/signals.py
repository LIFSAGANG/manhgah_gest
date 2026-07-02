from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    Societe, Produit, Client, Facture, Agence, Categorie, Projet, 
    Fournisseur, Achat, Depense, Role, UtilisateurProfile, 
    Journal, EcritureComptable, MouvementStock, ActivityLog
)
import json


def get_client_ip(request):
    """Extract client IP from request"""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    if not request:
        return None
    return request.META.get('HTTP_USER_AGENT', '')


def serialize_instance(instance):
    """Convert model instance to JSON-serializable dict"""
    data = {}
    for field in instance._meta.get_fields():
        try:
            value = getattr(instance, field.name)
            if value is None:
                data[field.name] = None
            elif hasattr(value, 'isoformat'):
                data[field.name] = value.isoformat()
            elif isinstance(value, (str, int, float, bool)):
                data[field.name] = value
            else:
                data[field.name] = str(value)
        except Exception:
            pass
    return data


# Track the old values before save
_old_values = {}


@receiver(pre_save)
def track_old_values(sender, instance, **kwargs):
    """Store old values before update"""
    if sender in [Societe, Produit, Client, Facture, Agence, Categorie, Projet, 
                  Fournisseur, Achat, Depense, Role, UtilisateurProfile, 
                  Journal, EcritureComptable, MouvementStock]:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _old_values[instance.pk] = serialize_instance(old_instance)
        except sender.DoesNotExist:
            _old_values[instance.pk] = None


@receiver(post_save)
def log_activity_create_update(sender, instance, created, **kwargs):
    """Log creation and update activities"""
    if sender in [Societe, Produit, Client, Facture, Agence, Categorie, Projet, 
                  Fournisseur, Achat, Depense, Role, UtilisateurProfile, 
                  Journal, EcritureComptable, MouvementStock]:
        
        try:
            from core.middleware import get_current_request
            request = get_current_request()
        except ImportError:
            request = None
        
        user = None
        ip_address = None
        user_agent = None
        
        if request:
            user = getattr(request, 'user', None)
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
        
        action = 'CREATE' if created else 'UPDATE'
        old_values = _old_values.get(instance.pk)
        new_values = serialize_instance(instance)
        
        # Get object name
        object_name = str(instance)
        
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=sender.__name__,
            object_id=instance.pk,
            object_name=object_name,
            old_values=old_values if not created else None,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Action {action} sur {sender.__name__}"
        )
        
        # Clean up old values
        if instance.pk in _old_values:
            del _old_values[instance.pk]


@receiver(post_delete)
def log_activity_delete(sender, instance, **kwargs):
    """Log deletion activities"""
    if sender in [Societe, Produit, Client, Facture, Agence, Categorie, Projet, 
                  Fournisseur, Achat, Depense, Role, UtilisateurProfile, 
                  Journal, EcritureComptable, MouvementStock]:
        
        try:
            from core.middleware import get_current_request
            request = get_current_request()
        except ImportError:
            request = None
        
        user = None
        ip_address = None
        user_agent = None
        
        if request:
            user = getattr(request, 'user', None)
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
        
        ActivityLog.objects.create(
            user=user,
            action='DELETE',
            content_type=sender.__name__,
            object_id=instance.pk,
            object_name=str(instance),
            old_values=serialize_instance(instance),
            new_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Suppression de {sender.__name__}: {instance}"
        )


@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    """Log user login/creation activities"""
    if not created:  # Only log for updates (not creation during migration)
        pass
