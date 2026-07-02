from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.urls import reverse
from .models import (Societe, Produit, Client, Facture, Agence, Categorie, Projet, Fournisseur, Achat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, MouvementStock, ActivityLog)
from .forms import (SocieteForm, ProduitForm, ClientForm, FactureForm, AgenceForm, CategorieForm, ProjetForm, FournisseurForm, AchatForm, DepenseForm, RoleForm, AppPermissionForm, RolePermissionForm, UtilisateurProfileForm, JournalForm, EcritureComptableForm, MouvementStockForm)
from .middleware import permission_required, clear_permissions_cache


def _redirect_with_standalone(request, route_name):
    url = reverse(route_name)
    if request.GET.get('standalone') == '1':
        return redirect(f'{url}?standalone=1')
    return redirect(url)


@login_required
def api_status(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'manhgah-gest',
    })


@login_required
def accueil(request):
    from .middleware import get_user_permissions
    perms = get_user_permissions(request.user)
    has = lambda *codes: '__all__' in perms or any(c in perms for c in codes)

    all_modules = [
        {'title': 'Produits et Stock', 'subtitle': 'Catalogue, catégories et mouvements', 'icon': 'fa-boxes-stacked', 'link': 'produits_stock_page', 'color_class': 'bg-yellow', 'codes': ['produit_voir', 'stock_voir']},
        {'title': 'Ventes', 'subtitle': 'Factures clients', 'icon': 'fa-chart-column', 'link': 'ventes', 'color_class': 'bg-blue', 'codes': ['vente_voir', 'facture_ajouter', 'client_voir']},
        {'title': 'Achats', 'subtitle': 'Commandes et approvisionnement', 'icon': 'fa-cart-shopping', 'link': 'achat_list', 'color_class': 'bg-danger', 'codes': ['achat_voir', 'fournisseur_voir']},
        {'title': 'Comptabilité', 'subtitle': 'Journaux et écritures', 'icon': 'fa-calculator', 'link': 'comptabilite_page', 'color_class': 'bg-purple', 'codes': ['ecriture_voir', 'journal_voir', 'rapport_comptable_voir']},
        {'title': 'Contacts', 'subtitle': 'Clients et fournisseurs', 'icon': 'fa-address-book', 'link': 'client_list', 'color_class': 'bg-teal', 'codes': ['client_voir', 'contact_voir', 'fournisseur_voir']},
        {'title': 'Statistique', 'subtitle': 'Analyses et tableaux de bord', 'icon': 'fa-chart-pie', 'link': 'statistiques', 'color_class': 'bg-success', 'codes': ['statistique_voir', 'rapport_voir']},
        {'title': 'Paramètre', 'subtitle': 'Sociétés et utilisateurs', 'icon': 'fa-gear', 'link': 'parametres_page', 'color_class': 'bg-dark', 'codes': ['utilisateur_voir', 'role_voir', 'societe_voir']},
    ]

    modules = [m for m in all_modules if has(*m['codes'])]

    return render(request, 'core/accueil.html', {'modules': modules})


@login_required
def produits_stock_page(request):
    return render(request, 'core/produits_stock_page.html')


@login_required
def ventes_page(request):
    return render(request, 'core/ventes_page.html')


@login_required
def comptabilite_page(request):
    return render(request, 'core/comptabilite_page.html')


@login_required
def parametres_page(request):
    return render(request, 'core/parametres_page.html')


@login_required
def etat_ventes_page(request):
    factures = Facture.objects.select_related('client').order_by('-date_emission')
    total_factures = factures.count()
    montant_total = factures.aggregate(total=Sum('montant_total'))['total'] or 0
    etats = factures.values('statut').annotate(nombre=Count('id'), montant=Sum('montant_total')).order_by('statut')

    return render(
        request,
        'core/etat_ventes_page.html',
        {
            'factures': factures[:20],
            'total_factures': total_factures,
            'montant_total': montant_total,
            'etats': etats,
        },
    )


@login_required
def tva_ventes_page(request):
    tva_rate = 0.18
    factures = Facture.objects.select_related('client').order_by('-date_emission')
    lignes = []
    total_ttc = 0
    total_ht = 0
    total_tva = 0

    for facture in factures:
        montant_ttc = facture.montant_total or 0
        montant_ht = montant_ttc / (1 + tva_rate)
        montant_tva = montant_ttc - montant_ht
        total_ttc += montant_ttc
        total_ht += montant_ht
        total_tva += montant_tva
        lignes.append(
            {
                'reference': facture.reference,
                'client': facture.client.nom,
                'date_emission': facture.date_emission,
                'montant_ht': montant_ht,
                'montant_tva': montant_tva,
                'montant_ttc': montant_ttc,
            }
        )

    return render(
        request,
        'core/tva_ventes_page.html',
        {
            'tva_rate': int(tva_rate * 100),
            'lignes': lignes[:50],
            'total_ttc': total_ttc,
            'total_ht': total_ht,
            'total_tva': total_tva,
        },
    )


@login_required
def etat_comptabilite_page(request):
    ecritures = EcritureComptable.objects.select_related('journal').order_by('-date_ecriture')
    total_ecritures = ecritures.count()
    total_debit = ecritures.aggregate(total=Sum('debit'))['total'] or 0
    total_credit = ecritures.aggregate(total=Sum('credit'))['total'] or 0
    solde = total_debit - total_credit
    etats_journaux = (
        ecritures.values('journal__nom')
        .annotate(nombre=Count('id'), total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('journal__nom')
    )

    return render(
        request,
        'core/etat_comptabilite_page.html',
        {
            'ecritures': ecritures[:30],
            'total_ecritures': total_ecritures,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'solde': solde,
            'etats_journaux': etats_journaux,
        },
    )


@login_required
def plan_comptable_page(request):
    comptes = (
        EcritureComptable.objects.values('compte')
        .annotate(nombre=Count('id'), total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('compte')
    )
    return render(request, 'core/plan_comptable_page.html', {'comptes': comptes})


@login_required
def code_journaux_page(request):
    journaux = Journal.objects.select_related('societe').order_by('code')
    return render(request, 'core/code_journaux_page.html', {'journaux': journaux})


@login_required
def brouillard_page(request):
    ecritures = EcritureComptable.objects.select_related('journal').order_by('-date_ecriture', '-id')
    return render(request, 'core/brouillard_page.html', {'ecritures': ecritures[:100]})


@login_required
def etat_journaux_page(request):
    journaux = (
        EcritureComptable.objects.values('journal__code', 'journal__nom')
        .annotate(nombre=Count('id'), total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('journal__code')
    )
    return render(request, 'core/etat_journaux_page.html', {'journaux': journaux})


@login_required
def balance_comptes_page(request):
    balances = (
        EcritureComptable.objects.values('compte')
        .annotate(total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('compte')
    )
    for ligne in balances:
        ligne['solde'] = (ligne['total_debit'] or 0) - (ligne['total_credit'] or 0)
    return render(request, 'core/balance_comptes_page.html', {'balances': balances})


@login_required
def grand_livre_page(request):
    lignes = EcritureComptable.objects.select_related('journal').order_by('compte', 'date_ecriture', 'id')
    return render(request, 'core/grand_livre_page.html', {'lignes': lignes[:200]})


@login_required
def etats_tiers_page(request):
    top_clients = (
        Facture.objects.values('client__nom')
        .annotate(total=Sum('montant_total'), nombre=Count('id'))
        .order_by('-total')
    )
    top_fournisseurs = (
        Achat.objects.values('fournisseur__nom')
        .annotate(total=Sum('montant_total'), nombre=Count('id'))
        .order_by('-total')
    )
    return render(
        request,
        'core/etats_tiers_page.html',
        {
            'top_clients': top_clients[:20],
            'top_fournisseurs': top_fournisseurs[:20],
        },
    )


@login_required
def etat_stock_page(request):
    produits = Produit.objects.all().order_by('nom')
    total_produits = produits.count()
    total_quantite = produits.aggregate(total=Sum('quantite_stock'))['total'] or 0
    produits_rupture = produits.filter(quantite_stock=0).count()

    return render(
        request,
        'core/etat_stock_page.html',
        {
            'produits': produits,
            'total_produits': total_produits,
            'total_quantite': total_quantite,
            'produits_rupture': produits_rupture,
        },
    )


@login_required
def inventaire_stock_page(request):
    produits = list(Produit.objects.all().order_by('nom'))
    for produit in produits:
        produit.valeur_stock = produit.prix_unitaire * produit.quantite_stock
    return render(request, 'core/inventaire_stock_page.html', {'produits': produits})


@login_required
def societe_list(request):
    societes = Societe.objects.annotate(agent_count=Count('agence')).all()
    return render(request, 'core/societe_list.html', {'societes': societes})


@login_required
def societe_create(request):
    form = SocieteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Société ajoutée avec succès.')
        return redirect('societe_list')
    return render(request, 'core/societe_form.html', {'form': form, 'title': 'Ajouter une société'})


@login_required
def societe_update(request, pk):
    societe = get_object_or_404(Societe, pk=pk)
    form = SocieteForm(request.POST or None, instance=societe)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Société modifiée avec succès.')
        return redirect('societe_list')
    return render(request, 'core/societe_form.html', {'form': form, 'title': 'Modifier la société'})


@login_required
def societe_delete(request, pk):
    societe = get_object_or_404(Societe, pk=pk)
    if request.method == 'POST':
        societe.delete()
        messages.success(request, 'Société supprimée avec succès.')
        return redirect('societe_list')
    return render(request, 'core/societe_confirm_delete.html', {'societe': societe})


@permission_required('client_voir')
def client_list(request):
    clients = Client.objects.select_related('societe').all()
    return render(request, 'core/client_list.html', {'clients': clients})


@permission_required('client_ajouter')
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Client ajouté avec succès.')
        return _redirect_with_standalone(request, 'client_list')
    return render(request, 'core/client_form.html', {'form': form, 'title': 'Ajouter un client'})


@permission_required('client_voir')
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Client modifié avec succès.')
        return _redirect_with_standalone(request, 'client_list')
    return render(request, 'core/client_form.html', {'form': form, 'title': 'Modifier le client'})


@permission_required('client_voir')
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Client supprimé avec succès.')
        return _redirect_with_standalone(request, 'client_list')
    return render(request, 'core/client_confirm_delete.html', {'client': client})


@permission_required('vente_voir')
def facture_list(request):
    factures = Facture.objects.select_related('client').all()
    return render(request, 'core/facture_list.html', {'factures': factures})


@permission_required('facture_ajouter')
def facture_create(request):
    form = FactureForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Facture ajoutée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_form.html', {'form': form, 'title': 'Ajouter une facture'})


@permission_required('facture_modifier')
def facture_update(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    form = FactureForm(request.POST or None, instance=facture)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Facture modifiée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_form.html', {'form': form, 'title': 'Modifier la facture'})


@permission_required('facture_supprimer')
def facture_delete(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture supprimée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_confirm_delete.html', {'facture': facture})


@permission_required('produit_voir')
def produit_list(request):
    produits = Produit.objects.all()
    return render(request, 'core/produit_list.html', {'produits': produits})


@permission_required('produit_ajouter')
def produit_create(request):
    form = ProduitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit ajouté avec succès.')
        return _redirect_with_standalone(request, 'produit_list')
    return render(request, 'core/produit_form.html', {'form': form, 'title': 'Ajouter un produit'})


@permission_required('produit_modifier')
def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, instance=produit)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit modifié avec succès.')
        return _redirect_with_standalone(request, 'produit_list')
    return render(request, 'core/produit_form.html', {'form': form, 'title': 'Modifier le produit'})


@permission_required('produit_supprimer')
def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès.')
        return _redirect_with_standalone(request, 'produit_list')
    return render(request, 'core/produit_confirm_delete.html', {'produit': produit})


@login_required
def module_page(request, module, description):
    stats = {
        'societes': Societe.objects.count(),
        'produits': Produit.objects.count()
    }
    return render(request, 'core/module_page.html', {'module': module, 'description': description, 'stats': stats})


# ============ AGENCE CRUD ============

@login_required
def agence_list(request):
    societe_id = request.GET.get('societe')
    q = request.GET.get('q', '').strip()
    ville = request.GET.get('ville', '').strip()
    agences = Agence.objects.select_related('societe').all()
    selected_societe = None

    if societe_id:
        selected_societe = get_object_or_404(Societe, pk=societe_id)
        agences = agences.filter(societe_id=societe_id)

    if q:
        agences = agences.filter(
            Q(nom__icontains=q)
            | Q(code__icontains=q)
            | Q(responsable__icontains=q)
            | Q(email__icontains=q)
            | Q(telephone__icontains=q)
        )

    if ville:
        agences = agences.filter(ville__iexact=ville)

    villes = (
        Agence.objects.exclude(ville__isnull=True)
        .exclude(ville__exact='')
        .order_by('ville')
        .values_list('ville', flat=True)
        .distinct()
    )

    return render(
        request,
        'core/agence_list.html',
        {
            'agences': agences,
            'selected_societe': selected_societe,
            'q': q,
            'selected_ville': ville,
            'villes': villes,
        },
    )


@login_required
def agence_create(request):
    societe_id = request.GET.get('societe')
    initial = {}
    if societe_id:
        initial['societe'] = societe_id
    form = AgenceForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agence ajoutée avec succès.')
        if societe_id:
            return redirect(f"{reverse('agence_list')}?societe={societe_id}")
        return redirect('agence_list')
    return render(request, 'core/agence_form.html', {'form': form, 'title': 'Ajouter une agence'})


@login_required
def agence_update(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    form = AgenceForm(request.POST or None, instance=agence)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agence modifiée avec succès.')
        return redirect('agence_list')
    return render(request, 'core/agence_form.html', {'form': form, 'title': 'Modifier l\'agence'})


@login_required
def agence_delete(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    if request.method == 'POST':
        agence.delete()
        messages.success(request, 'Agence supprimée avec succès.')
        return redirect('agence_list')
    return render(request, 'core/agence_confirm_delete.html', {'agence': agence})


# ============ CATEGORIE CRUD ============

@login_required
def categorie_list(request):
    categories = Categorie.objects.all()
    return render(request, 'core/categorie_list.html', {'categories': categories})


@login_required
def categorie_create(request):
    form = CategorieForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Catégorie ajoutée avec succès.')
        return _redirect_with_standalone(request, 'categorie_list')
    return render(request, 'core/categorie_form.html', {'form': form, 'title': 'Ajouter une catégorie'})


@login_required
def categorie_update(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    form = CategorieForm(request.POST or None, instance=categorie)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Catégorie modifiée avec succès.')
        return _redirect_with_standalone(request, 'categorie_list')
    return render(request, 'core/categorie_form.html', {'form': form, 'title': 'Modifier la catégorie'})


@login_required
def categorie_delete(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        messages.success(request, 'Catégorie supprimée avec succès.')
        return _redirect_with_standalone(request, 'categorie_list')
    return render(request, 'core/categorie_confirm_delete.html', {'categorie': categorie})


# ============ PROJET CRUD ============

@login_required
def projet_list(request):
    projets = Projet.objects.select_related('societe', 'agence').all()
    return render(request, 'core/projet_list.html', {'projets': projets})


@login_required
def projet_create(request):
    form = ProjetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet ajouté avec succès.')
        return redirect('projet_list')
    return render(request, 'core/projet_form.html', {'form': form, 'title': 'Ajouter un projet'})


@login_required
def projet_update(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    form = ProjetForm(request.POST or None, instance=projet)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet modifié avec succès.')
        return redirect('projet_list')
    return render(request, 'core/projet_form.html', {'form': form, 'title': 'Modifier le projet'})


@login_required
def projet_delete(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    if request.method == 'POST':
        projet.delete()
        messages.success(request, 'Projet supprimé avec succès.')
        return redirect('projet_list')
    return render(request, 'core/projet_confirm_delete.html', {'projet': projet})


# ============ FOURNISSEUR CRUD ============

@permission_required('fournisseur_voir')
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.select_related('societe').all()
    return render(request, 'core/fournisseur_list.html', {'fournisseurs': fournisseurs})


@permission_required('fournisseur_ajouter')
def fournisseur_create(request):
    form = FournisseurForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fournisseur ajouté avec succès.')
        return redirect('fournisseur_list')
    return render(request, 'core/fournisseur_form.html', {'form': form, 'title': 'Ajouter un fournisseur'})


@permission_required('fournisseur_voir')
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    form = FournisseurForm(request.POST or None, instance=fournisseur)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fournisseur modifié avec succès.')
        return redirect('fournisseur_list')
    return render(request, 'core/fournisseur_form.html', {'form': form, 'title': 'Modifier le fournisseur'})


@permission_required('fournisseur_voir')
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
        return redirect('fournisseur_list')
    return render(request, 'core/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})


# ============ ACHAT CRUD ============

@permission_required('achat_voir')
def achat_list(request):
    achats = Achat.objects.select_related('fournisseur', 'agence').all()
    return render(request, 'core/achat_list.html', {'achats': achats})


@permission_required('achat_ajouter')
def achat_create(request):
    form = AchatForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Achat ajouté avec succès.')
        return redirect('achat_list')
    return render(request, 'core/achat_form.html', {'form': form, 'title': 'Ajouter un achat'})


@permission_required('achat_modifier')
def achat_update(request, pk):
    achat = get_object_or_404(Achat, pk=pk)
    form = AchatForm(request.POST or None, instance=achat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Achat modifié avec succès.')
        return redirect('achat_list')
    return render(request, 'core/achat_form.html', {'form': form, 'title': 'Modifier l\'achat'})


@permission_required('achat_supprimer')
def achat_delete(request, pk):
    achat = get_object_or_404(Achat, pk=pk)
    if request.method == 'POST':
        achat.delete()
        messages.success(request, 'Achat supprimé avec succès.')
        return redirect('achat_list')
    return render(request, 'core/achat_confirm_delete.html', {'achat': achat})


# ============ DEPENSE CRUD ============

@login_required
def depense_list(request):
    depenses = Depense.objects.select_related('societe', 'agence', 'projet').all()
    return render(request, 'core/depense_list.html', {'depenses': depenses})


@login_required
def depense_create(request):
    form = DepenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dépense ajoutée avec succès.')
        return redirect('depense_list')
    return render(request, 'core/depense_form.html', {'form': form, 'title': 'Ajouter une dépense'})


@login_required
def depense_update(request, pk):
    depense = get_object_or_404(Depense, pk=pk)
    form = DepenseForm(request.POST or None, instance=depense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dépense modifiée avec succès.')
        return redirect('depense_list')
    return render(request, 'core/depense_form.html', {'form': form, 'title': 'Modifier la dépense'})


@login_required
def depense_delete(request, pk):
    depense = get_object_or_404(Depense, pk=pk)
    if request.method == 'POST':
        depense.delete()
        messages.success(request, 'Dépense supprimée avec succès.')
        return redirect('depense_list')
    return render(request, 'core/depense_confirm_delete.html', {'depense': depense})


# ============ ROLE CRUD ============

@permission_required('role_voir')
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'core/role_list.html', {'roles': roles})


@permission_required('role_modifier')
def role_create(request):
    form = RoleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Rôle ajouté avec succès.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Ajouter un rôle'})


@permission_required('role_modifier')
def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Rôle modifié avec succès.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Modifier le rôle'})


@permission_required('role_modifier')
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Rôle supprimé avec succès.')
        return redirect('role_list')
    return render(request, 'core/role_confirm_delete.html', {'role': role})


# ============ UTILISATEUR CRUD ============

@permission_required('utilisateur_voir')
def utilisateur_list(request):
    utilisateur_direction = request.GET.get('direction')
    utilisateurs = UtilisateurProfile.objects.select_related('user', 'societe', 'agence', 'role')
    if utilisateur_direction:
        utilisateurs = utilisateurs.filter(role__direction=utilisateur_direction)
    utilisateurs = utilisateurs.all()
    directions = Role.objects.order_by('direction').values_list('direction', flat=True).distinct()
    return render(request, 'core/utilisateur_list.html', {
        'utilisateurs': utilisateurs,
        'directions': directions,
        'selected_direction': utilisateur_direction,
    })


@permission_required('utilisateur_ajouter')
def utilisateur_create(request):
    form = UtilisateurProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Utilisateur ajouté avec succès.')
        return redirect('utilisateur_list')
    return render(request, 'core/utilisateur_form.html', {'form': form, 'title': 'Ajouter un utilisateur'})


@permission_required('utilisateur_modifier')
def utilisateur_update(request, pk):
    utilisateur = get_object_or_404(UtilisateurProfile, pk=pk)
    form = UtilisateurProfileForm(request.POST or None, instance=utilisateur)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Vider le cache permissions si le rôle a changé
        clear_permissions_cache(utilisateur.user_id)
        messages.success(request, 'Utilisateur modifié avec succès.')
        return redirect('utilisateur_list')
    return render(request, 'core/utilisateur_form.html', {'form': form, 'title': 'Modifier l\'utilisateur'})


@permission_required('utilisateur_supprimer')
def utilisateur_delete(request, pk):
    utilisateur = get_object_or_404(UtilisateurProfile, pk=pk)
    if request.method == 'POST':
        clear_permissions_cache(utilisateur.user_id)
        utilisateur.delete()
        messages.success(request, 'Utilisateur supprimé avec succès.')
        return redirect('utilisateur_list')
    return render(request, 'core/utilisateur_confirm_delete.html', {'utilisateur': utilisateur})


# ============ JOURNAL CRUD ============

@permission_required('journal_voir')
def journal_list(request):
    journaux = Journal.objects.select_related('societe').all()
    return render(request, 'core/journal_list.html', {'journaux': journaux})


@permission_required('journal_voir')
def journal_create(request):
    form = JournalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Journal ajouté avec succès.')
        return _redirect_with_standalone(request, 'journal_list')
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Ajouter un journal'})


@permission_required('journal_voir')
def journal_update(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    form = JournalForm(request.POST or None, instance=journal)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Journal modifié avec succès.')
        return _redirect_with_standalone(request, 'journal_list')
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Modifier le journal'})


@permission_required('journal_voir')
def journal_delete(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    if request.method == 'POST':
        journal.delete()
        messages.success(request, 'Journal supprimé avec succès.')
        return _redirect_with_standalone(request, 'journal_list')
    return render(request, 'core/journal_confirm_delete.html', {'journal': journal})


# ============ ECRITURE COMPTABLE CRUD ============

@permission_required('ecriture_voir')
def ecriture_list(request):
    ecritures = EcritureComptable.objects.select_related('journal').all()
    return render(request, 'core/ecriture_list.html', {'ecritures': ecritures})


@permission_required('ecriture_ajouter')
def ecriture_create(request):
    form = EcritureComptableForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Écriture ajoutée avec succès.')
        return _redirect_with_standalone(request, 'ecriture_list')
    return render(request, 'core/ecriture_form.html', {'form': form, 'title': 'Ajouter une écriture'})


@permission_required('ecriture_modifier')
def ecriture_update(request, pk):
    ecriture = get_object_or_404(EcritureComptable, pk=pk)
    form = EcritureComptableForm(request.POST or None, instance=ecriture)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Écriture modifiée avec succès.')
        return _redirect_with_standalone(request, 'ecriture_list')
    return render(request, 'core/ecriture_form.html', {'form': form, 'title': 'Modifier l\'écriture'})


@permission_required('ecriture_supprimer')
def ecriture_delete(request, pk):
    ecriture = get_object_or_404(EcritureComptable, pk=pk)
    if request.method == 'POST':
        ecriture.delete()
        messages.success(request, 'Écriture supprimée avec succès.')
        return _redirect_with_standalone(request, 'ecriture_list')
    return render(request, 'core/ecriture_confirm_delete.html', {'ecriture': ecriture})


# ============ MOUVEMENT STOCK CRUD ============

@permission_required('stock_voir')
def mouvement_list(request):
    mouvements = MouvementStock.objects.select_related('produit', 'agence').all()
    return render(request, 'core/mouvement_list.html', {'mouvements': mouvements})


@permission_required('mouvement_ajouter')
def mouvement_create(request):
    form = MouvementStockForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        mouvement = form.save()
        produit = mouvement.produit
        if mouvement.type_mouvement == 'entree':
            produit.quantite_stock += mouvement.quantite
        elif mouvement.type_mouvement == 'sortie':
            produit.quantite_stock = max(0, produit.quantite_stock - mouvement.quantite)
        produit.save()
        messages.success(request, 'Mouvement ajouté avec succès.')
        return _redirect_with_standalone(request, 'mouvement_list')
    return render(request, 'core/mouvement_form.html', {'form': form, 'title': 'Ajouter un mouvement'})


@permission_required('stock_voir')
def mouvement_update(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    form = MouvementStockForm(request.POST or None, instance=mouvement)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mouvement modifié avec succès.')
        return _redirect_with_standalone(request, 'mouvement_list')
    return render(request, 'core/mouvement_form.html', {'form': form, 'title': 'Modifier le mouvement'})


@permission_required('stock_voir')
def mouvement_delete(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    if request.method == 'POST':
        mouvement.delete()
        messages.success(request, 'Mouvement supprimé avec succès.')
        return _redirect_with_standalone(request, 'mouvement_list')
    return render(request, 'core/mouvement_confirm_delete.html', {'mouvement': mouvement})


# ============ AUDIT LOG ============

@login_required
def activity_log(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('accueil')
    
    logs = ActivityLog.objects.all().order_by('-timestamp')[:1000]
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    content_type_filter = request.GET.get('content_type')
    
    if user_filter:
        logs = logs.filter(user__username=user_filter)
    if action_filter:
        logs = logs.filter(action=action_filter)
    if content_type_filter:
        logs = logs.filter(content_type=content_type_filter)
    
    return render(request, 'core/activity_log.html', {
        'logs': logs,
        'users': ActivityLog.objects.values_list('user__username', flat=True).distinct(),
        'actions': ActivityLog.ACTION_CHOICES,
        'content_types': ActivityLog.objects.values_list('content_type', flat=True).distinct(),
    })


# ============ ROLE PERMISSIONS MANAGEMENT ============

@login_required
def role_permissions(request, pk):
    """Gérer les permissions d'un rôle"""
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('accueil')
    
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        permission_ids = request.POST.getlist('permissions')
        # Supprimer les permissions existantes
        RolePermission.objects.filter(role=role).delete()
        # Ajouter les nouvelles permissions
        for perm_id in permission_ids:
            permission = get_object_or_404(AppPermission, pk=perm_id)
            RolePermission.objects.create(role=role, permission=permission)
        messages.success(request, 'Permissions mises à jour avec succès.')
        return redirect('role_list')
    
    # Récupérer les permissions actuelles
    current_permissions = RolePermission.objects.filter(role=role).values_list('permission_id', flat=True)
    all_permissions = AppPermission.objects.all().order_by('module', 'nom_permission')
    
    # Grouper les permissions par module
    permissions_by_module = {}
    for perm in all_permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append({
            'id': perm.id,
            'nom': perm.nom_permission,
            'code': perm.code_permission,
            'description': perm.description,
            'checked': perm.id in current_permissions
        })
    
    return render(request, 'core/role_permissions.html', {
        'role': role,
        'permissions_by_module': permissions_by_module,
    })


@login_required
def utilisateur_permissions(request, pk):
    """Afficher les permissions d'un utilisateur"""
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('accueil')
    
    utilisateur = get_object_or_404(UtilisateurProfile, pk=pk)
    role = utilisateur.role
    
    # Récupérer les permissions du rôle
    role_permissions = RolePermission.objects.filter(role=role).select_related('permission')
    permissions_by_module = {}
    
    for rp in role_permissions:
        perm = rp.permission
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append({
            'nom': perm.nom_permission,
            'code': perm.code_permission,
            'description': perm.description,
        })
    
    return render(request, 'core/utilisateur_permissions.html', {
        'utilisateur': utilisateur,
        'role': role,
        'permissions_by_module': permissions_by_module,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accueil')
        else:
            messages.error(request, 'Identifiants invalides')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
