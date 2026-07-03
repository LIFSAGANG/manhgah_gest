from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'societes', api_views.SocieteViewSet)
router.register(r'produits', api_views.ProduitViewSet)
router.register(r'clients', api_views.ClientViewSet)
router.register(r'factures', api_views.FactureViewSet)
router.register(r'agences', api_views.AgenceViewSet)
router.register(r'categories', api_views.CategorieViewSet)
router.register(r'projets', api_views.ProjetViewSet)
router.register(r'fournisseurs', api_views.FournisseurViewSet)
router.register(r'achats', api_views.AchatViewSet)
router.register(r'depenses', api_views.DepenseViewSet)
router.register(r'journaux', api_views.JournalViewSet)
router.register(r'ecritures', api_views.EcritureComptableViewSet)
router.register(r'stocks', api_views.StockViewSet)
router.register(r'mouvements', api_views.MouvementStockViewSet)
router.register(r'roles', api_views.RoleViewSet)
router.register(r'permissions', api_views.AppPermissionViewSet)
router.register(r'role-permissions', api_views.RolePermissionViewSet)
router.register(r'utilisateurs-profiles', api_views.UtilisateurProfileViewSet)
router.register(r'activity-logs', api_views.ActivityLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
