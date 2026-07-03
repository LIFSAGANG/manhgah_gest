from django.contrib import admin
from .models import (Agence, Categorie, Projet, Fournisseur, Achat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, MouvementStock, Stock, Societe, Produit, Client, Facture, ActivityLog)


@admin.register(Societe)
class SocieteAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'code_societe', 'email', 'telephone', 'ville', 'pays', 'actif')
    list_filter = ('actif', 'pays')
    search_fields = ('raison_sociale', 'code_societe', 'email', 'ville')


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'nom_produit', 'categorie', 'prix_vente_ht', 'stock_alerte', 'actif')
    list_filter = ('actif', 'categorie')
    search_fields = ('code_produit', 'nom_produit', 'code_barre')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'email', 'telephone', 'ville', 'pays', 'actif')
    list_filter = ('actif', 'pays')
    search_fields = ('nom', 'code', 'email', 'ville')


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'date_emission', 'montant_total', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference', 'client__nom', 'client__code')
    raw_id_fields = ('client',)


@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ('societe', 'code', 'nom', 'type_agence', 'ville', 'telephone', 'email', 'actif')
    list_filter = ('type_agence', 'actif', 'ville')
    search_fields = ('nom', 'code', 'responsable', 'ville')


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('code_categorie', 'nom_categorie', 'societe', 'actif')
    list_filter = ('actif',)
    search_fields = ('code_categorie', 'nom_categorie')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'agence', 'quantite_disponible', 'quantite_reservee', 'valeur_stock', 'date_dernier_mouvement')
    list_filter = ('agence',)
    search_fields = ('produit__nom_produit', 'produit__code_produit', 'agence__nom')


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('societe', 'agence', 'code', 'nom', 'budget', 'actif')
    list_filter = ('actif', 'societe')
    search_fields = ('code', 'nom', 'description')


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('societe', 'code', 'nom', 'email', 'telephone', 'ville', 'pays', 'actif')
    list_filter = ('actif', 'pays')
    search_fields = ('code', 'nom', 'email')


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'date_commande', 'montant_total', 'statut')
    list_filter = ('statut', 'date_commande')
    search_fields = ('reference', 'fournisseur__nom')


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('reference', 'societe', 'agence', 'projet', 'montant', 'date_depense', 'type_depense')
    list_filter = ('type_depense', 'date_depense', 'societe')
    search_fields = ('reference', 'description')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'direction', 'niveau_acces', 'actif')
    list_filter = ('direction', 'actif')
    search_fields = ('nom', 'direction')


@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ('code_permission', 'nom_permission', 'module')
    search_fields = ('code_permission', 'nom_permission', 'module')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    raw_id_fields = ('role', 'permission')


@admin.register(UtilisateurProfile)
class UtilisateurProfileAdmin(admin.ModelAdmin):
    list_display = ('nom_utilisateur', 'prenom', 'nom', 'email', 'societe', 'agence', 'role', 'actif')
    search_fields = ('user__username', 'nom', 'prenom', 'email')
    raw_id_fields = ('societe', 'agence', 'role')


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('societe', 'code', 'nom', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom', 'code')


@admin.register(EcritureComptable)
class EcritureComptableAdmin(admin.ModelAdmin):
    list_display = ('journal', 'reference', 'date_ecriture', 'intitule', 'debit', 'credit')
    list_filter = ('date_ecriture',)
    search_fields = ('reference', 'intitule', 'compte')


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'agence', 'agence_destination', 'quantite', 'type_mouvement', 'utilisateur', 'date_mouvement')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('produit__nom_produit', 'produit__code_produit', 'reference', 'utilisateur__username')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'content_type', 'object_name', 'ip_address', 'timestamp')
    list_filter = ('action', 'content_type', 'timestamp', 'user')
    search_fields = ('user__username', 'object_name', 'ip_address', 'details')
    readonly_fields = ('user', 'action', 'content_type', 'object_id', 'object_name', 'old_values', 'new_values', 'ip_address', 'user_agent', 'timestamp', 'details')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
