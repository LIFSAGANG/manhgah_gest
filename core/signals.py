from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    Societe, Produit, Client, Facture, LigneVente, Agence, Categorie, Projet, 
    Fournisseur, Achat, LigneAchat, Depense, Role, UtilisateurProfile, 
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
    if sender in [Societe, Produit, Client, Facture, LigneVente, Agence, Categorie, Projet, 
                  Fournisseur, Achat, LigneAchat, Depense, Role, UtilisateurProfile, 
                  Journal, EcritureComptable, MouvementStock]:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _old_values[instance.pk] = serialize_instance(old_instance)
        except sender.DoesNotExist:
            _old_values[instance.pk] = None


@receiver(post_save)
def log_activity_create_update(sender, instance, created, **kwargs):
    """Log creation and update activities"""
    if sender in [Societe, Produit, Client, Facture, LigneVente, Agence, Categorie, Projet, 
                  Fournisseur, Achat, LigneAchat, Depense, Role, UtilisateurProfile, 
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
            if user is not None and not getattr(user, 'is_authenticated', False):
                user = None
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
    if sender in [Societe, Produit, Client, Facture, LigneVente, Agence, Categorie, Projet, 
                  Fournisseur, Achat, LigneAchat, Depense, Role, UtilisateurProfile, 
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
            if user is not None and not getattr(user, 'is_authenticated', False):
                user = None
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


@receiver(post_save, sender=Societe)
def generate_plan_comptable(sender, instance, created, **kwargs):
    """Auto-generate plan comptable when a new Societe is created"""
    if not created:
        return  # Only for new societies
    
    from .models import PlanComptable
    from django.db import transaction
    
    # Plan comptable standard pour chaque nouvelle société
    plan_comptable_data = [
        ('101100', 'Capital engagé non appelé', 'Capitaux propres', 1),
        ('101200', 'Capital souscrit, appelé, non versé', 'Capitaux propres', 1),
        ('101300', 'Capital souscrit, appelé, versé, non amorti', 'Capitaux propres', 1),
        ('401100', 'Fournisseurs', 'Fournisseur', 4),
        ('401200', 'Fournisseurs, Groupe', 'Fournisseur', 4),
        ('411100', 'Clients', 'Client', 4),
        ('411200', 'Clients - Groupe', 'Client', 4),
        ('512100', 'Banque', 'Banque et espèces', 5),
        ('531100', 'Caisse', 'Banque et espèces', 5),
        ('600100', 'Achats matières premières', 'Charges', 6),
        ('700100', 'Ventes', 'Revenus', 7),
    ]
    
    try:
        with transaction.atomic():
            for numero, nom, type_compte, classe in plan_comptable_data:
                PlanComptable.objects.get_or_create(
                    societe=instance,
                    numero_compte=numero,
                    defaults={
                        'nom_compte': nom,
                        'type_compte': type_compte,
                        'classe': classe,
                        'actif': True,
                    }
                )
    except Exception as e:
        # Silently fail - plan comptable should be imported manually
        print(f"Error generating plan comptable for {instance}: {e}")

