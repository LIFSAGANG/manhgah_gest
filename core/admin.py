from django.contrib import admin
from .models import (Agence, Categorie, Projet, Fournisseur, Achat, LigneAchat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, MouvementStock, Stock, Societe, Produit, Client, Facture, LigneVente, ActivityLog, Caisse, MouvementCaisse, LogActivite, Banque, MouvementBanque, PlanComptable, LigneEcriture)


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
    list_display = ('numero_vente', 'societe', 'agence', 'client', 'projet', 'type_vente', 'date_vente', 'montant_ttc', 'statut_vente')
    list_filter = ('statut_vente', 'type_vente')
    search_fields = ('numero_vente', 'client__nom', 'client__code')
    raw_id_fields = ('client', 'projet')


@admin.register(LigneVente)
class LigneVenteAdmin(admin.ModelAdmin):
    list_display = ('vente', 'designation', 'produit', 'quantite', 'prix_unitaire_ht', 'montant_ttc')
    search_fields = ('vente__numero_vente', 'produit__nom_produit', 'produit__code_produit')


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
    list_display = ('societe', 'agence', 'reference_projet', 'libelle_projet', 'type_projet', 'statut_projet', 'client', 'responsable', 'budget_previsionnel', 'actif')
    list_filter = ('actif', 'societe', 'type_projet', 'statut_projet')
    search_fields = ('reference_projet', 'libelle_projet', 'description')


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('societe', 'code', 'nom', 'email', 'telephone', 'ville', 'pays', 'actif')
    list_filter = ('actif', 'pays')
    search_fields = ('code', 'nom', 'email')


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('numero_achat', 'societe', 'agence', 'fournisseur', 'projet', 'type_achat', 'date_achat', 'montant_ttc', 'statut_achat')
    list_filter = ('statut_achat', 'date_achat')
    search_fields = ('numero_achat', 'fournisseur__nom')


@admin.register(LigneAchat)
class LigneAchatAdmin(admin.ModelAdmin):
    list_display = ('achat', 'designation', 'produit', 'quantite', 'prix_unitaire_ht', 'montant_ttc', 'quantite_recue')
    search_fields = ('achat__numero_achat', 'produit__nom_produit', 'produit__code_produit')


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
    list_display = ('societe', 'code', 'nom', 'type_journal', 'actif')
    list_filter = ('actif', 'type_journal')
    search_fields = ('nom', 'code', 'type_journal')


@admin.register(EcritureComptable)
class EcritureComptableAdmin(admin.ModelAdmin):
    list_display = ('societe', 'agence', 'journal', 'numero_ecriture', 'date_ecriture', 'valide', 'utilisateur')
    list_filter = ('date_ecriture', 'journal', 'valide')
    search_fields = ('numero_ecriture', 'reference', 'libelle_ecriture', 'piece_comptable')


@admin.register(PlanComptable)
class PlanComptableAdmin(admin.ModelAdmin):
    list_display = ('societe', 'numero_compte', 'nom_compte', 'type_compte', 'classe', 'compte_parent', 'actif')
    list_filter = ('societe', 'type_compte', 'classe', 'actif')
    search_fields = ('numero_compte', 'nom_compte')


@admin.register(LigneEcriture)
class LigneEcritureAdmin(admin.ModelAdmin):
    list_display = ('ecriture', 'compte', 'debit', 'credit', 'date_creation')
    list_filter = ('date_creation',)
    search_fields = ('ecriture__numero_ecriture', 'ecriture__reference', 'compte__numero_compte', 'compte__nom_compte')


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


@admin.register(Caisse)
class CaisseAdmin(admin.ModelAdmin):
    list_display = ('code_caisse', 'nom_caisse', 'agence', 'solde_initial', 'solde_actuel', 'responsable', 'actif', 'date_creation')
    list_filter = ('actif', 'agence')
    search_fields = ('code_caisse', 'nom_caisse', 'agence__nom')


@admin.register(MouvementCaisse)
class MouvementCaisseAdmin(admin.ModelAdmin):
    list_display = ('caisse', 'type_mouvement', 'montant', 'reference', 'utilisateur', 'date_mouvement')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('caisse__code_caisse', 'reference', 'motif')


@admin.register(LogActivite)
class LogActiviteAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'action', 'table_cible', 'enregistrement_id', 'adresse_ip', 'date_action')
    list_filter = ('table_cible', 'date_action')
    search_fields = ('action', 'table_cible', 'description', 'adresse_ip')


@admin.register(Banque)
class BanqueAdmin(admin.ModelAdmin):
    list_display = ('code_banque', 'nom_banque', 'agence', 'solde_initial', 'solde_actuel', 'responsable', 'actif', 'date_creation')
    list_filter = ('actif', 'agence')
    search_fields = ('code_banque', 'nom_banque', 'agence__nom')


@admin.register(MouvementBanque)
class MouvementBanqueAdmin(admin.ModelAdmin):
    list_display = ('banque', 'type_mouvement', 'montant', 'reference', 'utilisateur', 'date_mouvement')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('banque__code_banque', 'reference', 'motif')
