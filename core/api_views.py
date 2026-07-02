from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    Societe, Produit, Client, Facture, Agence, Categorie, Projet,
    Fournisseur, Achat, Depense, Journal, EcritureComptable,
    MouvementStock, Role, AppPermission, RolePermission,
    UtilisateurProfile, ActivityLog
)
from .serializers import (
    SocieteSerializer, ProduitSerializer, ClientSerializer, FactureSerializer,
    AgenceSerializer, CategorieSerializer, ProjetSerializer, FournisseurSerializer,
    AchatSerializer, DepenseSerializer, JournalSerializer, EcritureComptableSerializer,
    MouvementStockSerializer, RoleSerializer, AppPermissionSerializer,
    RolePermissionSerializer, UtilisateurProfileSerializer, ActivityLogSerializer
)

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = []

class SocieteViewSet(BaseModelViewSet):
    queryset = Societe.objects.all()
    serializer_class = SocieteSerializer

class ProduitViewSet(BaseModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class ClientViewSet(BaseModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class FactureViewSet(BaseModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer

class AgenceViewSet(BaseModelViewSet):
    queryset = Agence.objects.all()
    serializer_class = AgenceSerializer

class CategorieViewSet(BaseModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class ProjetViewSet(BaseModelViewSet):
    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer

class FournisseurViewSet(BaseModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer

class AchatViewSet(BaseModelViewSet):
    queryset = Achat.objects.all()
    serializer_class = AchatSerializer

class DepenseViewSet(BaseModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer

class JournalViewSet(BaseModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer

class EcritureComptableViewSet(BaseModelViewSet):
    queryset = EcritureComptable.objects.all()
    serializer_class = EcritureComptableSerializer

class MouvementStockViewSet(BaseModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer

class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class AppPermissionViewSet(BaseModelViewSet):
    queryset = AppPermission.objects.all()
    serializer_class = AppPermissionSerializer

class RolePermissionViewSet(BaseModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

class UtilisateurProfileViewSet(BaseModelViewSet):
    queryset = UtilisateurProfile.objects.all()
    serializer_class = UtilisateurProfileSerializer

class ActivityLogViewSet(BaseModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
