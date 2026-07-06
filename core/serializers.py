from rest_framework import serializers
from .models import (
    Societe, Produit, Client, Facture, Agence, Categorie, Projet,
    Fournisseur, Achat, LigneAchat, Depense, Journal, EcritureComptable, Stock,
    MouvementStock, Role, AppPermission, RolePermission,
    UtilisateurProfile, LigneVente, ActivityLog, Caisse, MouvementCaisse, LogActivite, Banque, MouvementBanque, PlanComptable, LigneEcriture
)

class SocieteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Societe
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'


class LigneVenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneVente
        fields = '__all__'

class AgenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agence
        fields = '__all__'

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'

class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = '__all__'

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class AchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achat
        fields = '__all__'


class LigneAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneAchat
        fields = '__all__'

class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = '__all__'

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = '__all__'

class EcritureComptableSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcritureComptable
        fields = '__all__'


class PlanComptableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanComptable
        fields = '__all__'


class LigneEcritureSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneEcriture
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = '__all__'
        read_only_fields = ['utilisateur', 'date_mouvement']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'

class UtilisateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilisateurProfile
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'


class CaisseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caisse
        fields = '__all__'


class MouvementCaisseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementCaisse
        fields = '__all__'


class LogActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogActivite
        fields = '__all__'


class BanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banque
        fields = '__all__'


class MouvementBanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementBanque
        fields = '__all__'
