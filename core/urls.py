from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('produits-stock/', views.produits_stock_page, name='produits_stock_page'),
    path('stock/etat/', views.etat_stock_page, name='etat_stock_page'),
    path('stock/inventaire/', views.inventaire_stock_page, name='inventaire_stock_page'),
    path('api/', include('core.api_urls')),

    path('societes/', views.societe_list, name='societe_list'),
    path('societes/ajouter/', views.societe_create, name='societe_create'),
    path('societes/<int:pk>/modifier/', views.societe_update, name='societe_update'),
    path('societes/<int:pk>/supprimer/', views.societe_delete, name='societe_delete'),

    path('produits/', views.produit_list, name='produit_list'),
    path('produits/ajouter/', views.produit_create, name='produit_create'),
    path('produits/<int:pk>/modifier/', views.produit_update, name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.produit_delete, name='produit_delete'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/ajouter/', views.client_create, name='client_create'),
    path('clients/<int:pk>/modifier/', views.client_update, name='client_update'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),

    path('factures/', views.facture_list, name='facture_list'),
    path('factures/ajouter/', views.facture_create, name='facture_create'),
    path('factures/<int:pk>/modifier/', views.facture_update, name='facture_update'),
    path('factures/<int:pk>/supprimer/', views.facture_delete, name='facture_delete'),
    path('ventes/etat/', views.etat_ventes_page, name='etat_ventes_page'),
    path('ventes/tva/', views.tva_ventes_page, name='tva_ventes_page'),
    path('comptabilite/', views.comptabilite_page, name='comptabilite_page'),
    path('comptabilite/etat/', views.etat_comptabilite_page, name='etat_comptabilite_page'),
    path('comptabilite/plan-comptable/', views.plan_comptable_page, name='plan_comptable_page'),
    path('comptabilite/code-journaux/', views.code_journaux_page, name='code_journaux_page'),
    path('comptabilite/brouillard/', views.brouillard_page, name='brouillard_page'),
    path('comptabilite/etat-journaux/', views.etat_journaux_page, name='etat_journaux_page'),
    path('comptabilite/balance-comptes/', views.balance_comptes_page, name='balance_comptes_page'),
    path('comptabilite/grand-livre/', views.grand_livre_page, name='grand_livre_page'),
    path('comptabilite/etats-tiers/', views.etats_tiers_page, name='etats_tiers_page'),

    # ============ AGENCES ============
    path('agences/', views.agence_list, name='agence_list'),
    path('agences/ajouter/', views.agence_create, name='agence_create'),
    path('agences/<int:pk>/modifier/', views.agence_update, name='agence_update'),
    path('agences/<int:pk>/supprimer/', views.agence_delete, name='agence_delete'),

    # ============ CATEGORIES ============
    
    path('categories/', views.categorie_list, name='categorie_list'),
    path('categories/ajouter/', views.categorie_create, name='categorie_create'),
    path('categories/<int:pk>/modifier/', views.categorie_update, name='categorie_update'),
    path('categories/<int:pk>/supprimer/', views.categorie_delete, name='categorie_delete'),

    # ============ PROJETS ============
    path('projets/', views.projet_list, name='projet_list'),
    path('projets/ajouter/', views.projet_create, name='projet_create'),
    path('projets/<int:pk>/modifier/', views.projet_update, name='projet_update'),
    path('projets/<int:pk>/supprimer/', views.projet_delete, name='projet_delete'),

    # ============ FOURNISSEURS ============
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/ajouter/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),

    # ============ ACHATS ============
    path('achats/', views.achat_list, name='achat_list'),
    path('achats/ajouter/', views.achat_create, name='achat_create'),
    path('achats/<int:pk>/modifier/', views.achat_update, name='achat_update'),
    path('achats/<int:pk>/supprimer/', views.achat_delete, name='achat_delete'),

    # ============ DEPENSES ============
    path('depenses/', views.depense_list, name='depense_list'),
    path('depenses/ajouter/', views.depense_create, name='depense_create'),
    path('depenses/<int:pk>/modifier/', views.depense_update, name='depense_update'),
    path('depenses/<int:pk>/supprimer/', views.depense_delete, name='depense_delete'),

    # ============ ROLES ============
    path('roles/', views.role_list, name='role_list'),
    path('roles/ajouter/', views.role_create, name='role_create'),
    path('roles/<int:pk>/modifier/', views.role_update, name='role_update'),
    path('roles/<int:pk>/supprimer/', views.role_delete, name='role_delete'),
    path('roles/<int:pk>/permissions/', views.role_permissions, name='role_permissions'),

    # ============ UTILISATEURS ============
    path('utilisateurs/', views.utilisateur_list, name='utilisateur_list'),
    path('utilisateurs/ajouter/', views.utilisateur_create, name='utilisateur_create'),
    path('utilisateurs/<int:pk>/modifier/', views.utilisateur_update, name='utilisateur_update'),
    path('utilisateurs/<int:pk>/supprimer/', views.utilisateur_delete, name='utilisateur_delete'),
    path('utilisateurs/<int:pk>/permissions/', views.utilisateur_permissions, name='utilisateur_permissions'),

    # ============ JOURNAUX ============
    path('journaux/', views.journal_list, name='journal_list'),
    path('journaux/ajouter/', views.journal_create, name='journal_create'),
    path('journaux/<int:pk>/modifier/', views.journal_update, name='journal_update'),
    path('journaux/<int:pk>/supprimer/', views.journal_delete, name='journal_delete'),

    # ============ ECRITURES COMPTABLES ============
    path('ecritures/', views.ecriture_list, name='ecriture_list'),
    path('ecritures/ajouter/', views.ecriture_create, name='ecriture_create'),
    path('ecritures/<int:pk>/modifier/', views.ecriture_update, name='ecriture_update'),
    path('ecritures/<int:pk>/supprimer/', views.ecriture_delete, name='ecriture_delete'),

    # ============ MOUVEMENTS DE STOCK ============
    path('mouvements/', views.mouvement_list, name='mouvement_list'),
    path('mouvements/ajouter/', views.mouvement_create, name='mouvement_create'),
    path('mouvements/<int:pk>/modifier/', views.mouvement_update, name='mouvement_update'),
    path('mouvements/<int:pk>/supprimer/', views.mouvement_delete, name='mouvement_delete'),

    # ============ NAVIGATION ============
    path('ventes/', views.ventes_page, name='ventes'),
    path('parametres/', views.parametres_page, name='parametres_page'),
    path('contacts/', views.contacts_page, name='contacts_page'),
    path('statistiques/', views.module_page, {'module': 'Statistiques', 'description': 'Analyses, rapports et tableaux de bord.'}, name='statistiques'),
    path('audit/', views.activity_log, name='activity_log'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/status/', views.api_status, name='api_status'),
]
