import json
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode
from .models import (Societe, Produit, Client, Facture, Agence, Categorie, Projet, Fournisseur, Achat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, Stock, MouvementStock, ActivityLog, Caisse, MouvementCaisse, Banque, MouvementBanque, PlanComptable, LigneEcriture, ComptabilisationParametre)
from .forms import (SocieteForm, ProduitForm, ClientForm, FactureForm, LigneVenteFormSet, AgenceForm, CategorieForm, ProjetForm, FournisseurForm, AchatForm, LigneAchatFormSet, DepenseForm, RoleForm, AppPermissionForm, RolePermissionForm, UtilisateurProfileForm, JournalForm, EcritureComptableForm, MouvementStockForm, CaisseForm, MouvementCaisseForm, BanqueForm, MouvementBanqueForm, PlanComptableForm, LigneEcritureForm, LigneEcritureFormSet, ComptabilisationParametreForm)
from .middleware import permission_required, clear_permissions_cache


def _redirect_with_standalone(request, route_name):
    url = reverse(route_name)
    params = []
    journal_id = (request.POST.get('journal') or request.GET.get('journal') or '').strip()
    
    if request.GET.get('standalone') == '1':
        params.append('standalone=1')
    if request.GET.get('embed') == '1':
        params.append('embed=1')
    if request.GET.get('from_parametres') == '1':
        params.append('from_parametres=1')
    if request.GET.get('from_contacts') == '1':
        params.append('from_contacts=1')
    if request.GET.get('from_produits_stock') == '1':
        params.append('from_produits_stock=1')
    if request.GET.get('from_ventes') == '1':
        params.append('from_ventes=1')
    if request.GET.get('from_achats') == '1':
        params.append('from_achats=1')
    if request.GET.get('from_comptabilite') == '1':
        params.append('from_comptabilite=1')
    if request.GET.get('societe'):
        params.append(f"societe={request.GET.get('societe')}")
    if journal_id and route_name == 'ecriture_list':
        params.append(f'journal={journal_id}')
    
    if params:
        return redirect(f'{url}?{"&".join(params)}')
    return redirect(url)


def _get_accessible_societes(user):
    if not user.is_authenticated:
        return Societe.objects.none()
    if user.is_superuser:
        return Societe.objects.filter(actif=True).order_by('raison_sociale')
    try:
        profile = user.utilisateurprofile
    except UtilisateurProfile.DoesNotExist:
        return Societe.objects.none()
    return Societe.objects.filter(pk=profile.societe_id, actif=True).order_by('raison_sociale')


def _get_selected_societe_id(request, accessible_societes):
    raw_societe = request.GET.get('societe')
    if raw_societe and accessible_societes.filter(pk=raw_societe).exists():
        return int(raw_societe)
    return accessible_societes.values_list('id', flat=True).first()


def _amount_to_int(value):
    if value in (None, ''):
        return 0
    try:
        return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, TypeError, ValueError):
        return 0


def _amount_to_display(value):
    amount = _amount_to_int(value)
    return '' if amount == 0 else str(amount)


def _configure_form_for_societe(form, user, selected_societe_id):
    accessible_societes = _get_accessible_societes(user)

    if 'societe' in form.fields:
        form.fields['societe'].queryset = accessible_societes
        if selected_societe_id:
            if not form.is_bound:
                form.initial.setdefault('societe', selected_societe_id)
            form.fields['societe'].widget = forms.HiddenInput()

    if 'categorie' in form.fields:
        if selected_societe_id:
            form.fields['categorie'].queryset = Categorie.objects.filter(societe_id=selected_societe_id).order_by('nom_categorie')
        else:
            form.fields['categorie'].queryset = Categorie.objects.none()

    if 'categorie_parent' in form.fields:
        if selected_societe_id:
            form.fields['categorie_parent'].queryset = Categorie.objects.filter(societe_id=selected_societe_id).order_by('nom_categorie')
        else:
            form.fields['categorie_parent'].queryset = Categorie.objects.none()

    if 'produit' in form.fields:
        if selected_societe_id:
            form.fields['produit'].queryset = Produit.objects.filter(societe_id=selected_societe_id).order_by('nom_produit')
        else:
            form.fields['produit'].queryset = Produit.objects.none()

    if 'agence' in form.fields:
        if selected_societe_id:
            form.fields['agence'].queryset = Agence.objects.filter(societe_id=selected_societe_id).order_by('nom')
        else:
            form.fields['agence'].queryset = Agence.objects.none()

    if 'agence_destination' in form.fields:
        if selected_societe_id:
            form.fields['agence_destination'].queryset = Agence.objects.filter(societe_id=selected_societe_id).order_by('nom')
        else:
            form.fields['agence_destination'].queryset = Agence.objects.none()

    if 'client' in form.fields:
        if selected_societe_id:
            form.fields['client'].queryset = Client.objects.filter(societe_id=selected_societe_id).order_by('raison_sociale', 'nom')
        else:
            form.fields['client'].queryset = Client.objects.none()

    if 'fournisseur' in form.fields:
        if selected_societe_id:
            form.fields['fournisseur'].queryset = Fournisseur.objects.filter(societe_id=selected_societe_id).order_by('raison_sociale')
        else:
            form.fields['fournisseur'].queryset = Fournisseur.objects.none()

    if 'projet' in form.fields:
        if selected_societe_id:
            form.fields['projet'].queryset = Projet.objects.filter(societe_id=selected_societe_id).order_by('libelle_projet')
        else:
            form.fields['projet'].queryset = Projet.objects.none()

    if 'responsable' in form.fields:
        if selected_societe_id:
            form.fields['responsable'].queryset = UtilisateurProfile.objects.filter(societe_id=selected_societe_id, actif=True).order_by('nom', 'prenom')
        else:
            form.fields['responsable'].queryset = UtilisateurProfile.objects.none()

    if 'caisse' in form.fields:
        if selected_societe_id:
            form.fields['caisse'].queryset = Caisse.objects.filter(agence__societe_id=selected_societe_id, actif=True).select_related('agence').order_by('nom_caisse')
        else:
            form.fields['caisse'].queryset = Caisse.objects.none()

    if 'utilisateur' in form.fields:
        if selected_societe_id:
            user_profile_id = getattr(getattr(user, 'utilisateurprofile', None), 'pk', None)
            current_instance_user_id = getattr(getattr(form, 'instance', None), 'utilisateur_id', None)
            form.fields['utilisateur'].queryset = UtilisateurProfile.objects.filter(
                Q(societe_id=selected_societe_id, actif=True)
                | Q(pk=user_profile_id)
                | Q(pk=current_instance_user_id)
            ).distinct().order_by('nom', 'prenom')
        else:
            form.fields['utilisateur'].queryset = UtilisateurProfile.objects.none()

    if 'banque' in form.fields:
        if selected_societe_id:
            form.fields['banque'].queryset = Banque.objects.filter(agence__societe_id=selected_societe_id, actif=True).select_related('agence').order_by('nom_banque')
        else:
            form.fields['banque'].queryset = Banque.objects.none()

    if 'journal' in form.fields:
        if selected_societe_id:
            form.fields['journal'].queryset = Journal.objects.filter(societe_id=selected_societe_id, actif=True).order_by('code')
        else:
            form.fields['journal'].queryset = Journal.objects.none()

    if 'compte_parent' in form.fields:
        if selected_societe_id:
            form.fields['compte_parent'].queryset = PlanComptable.objects.filter(societe_id=selected_societe_id, actif=True).order_by('numero_compte')
        else:
            form.fields['compte_parent'].queryset = PlanComptable.objects.none()

    if 'compte_defaut' in form.fields:
        if selected_societe_id:
            form.fields['compte_defaut'].queryset = PlanComptable.objects.filter(societe_id=selected_societe_id, actif=True).order_by('numero_compte')
        else:
            form.fields['compte_defaut'].queryset = PlanComptable.objects.none()

    if 'compte' in form.fields and form.fields['compte'].__class__.__name__ == 'ModelChoiceField':
        if selected_societe_id:
            form.fields['compte'].queryset = PlanComptable.objects.filter(societe_id=selected_societe_id, actif=True).order_by('numero_compte')
        else:
            form.fields['compte'].queryset = PlanComptable.objects.none()

    if 'ecriture' in form.fields:
        if selected_societe_id:
            form.fields['ecriture'].queryset = EcritureComptable.objects.filter(societe_id=selected_societe_id).order_by('-date_ecriture', '-id')
        else:
            form.fields['ecriture'].queryset = EcritureComptable.objects.none()


def _configure_line_formset_for_societe(line_formset, selected_societe_id):
    queryset = Produit.objects.filter(societe_id=selected_societe_id).order_by('nom_produit') if selected_societe_id else Produit.objects.none()
    forms_to_configure = list(line_formset.forms) + [line_formset.empty_form]
    for form in forms_to_configure:
        if 'produit' in form.fields:
            form.fields['produit'].queryset = queryset


def _configure_ligne_ecriture_formset_for_societe(line_formset, selected_societe_id):
    queryset = PlanComptable.objects.filter(societe_id=selected_societe_id, actif=True).order_by('numero_compte') if selected_societe_id else PlanComptable.objects.none()
    forms_to_configure = list(line_formset.forms) + [line_formset.empty_form]
    for form in forms_to_configure:
        if 'compte' in form.fields:
            form.fields['compte'].queryset = queryset


def _get_filtered_factures(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    factures = Facture.objects.select_related('client', 'agence', 'societe').all()
    if selected_societe_id:
        factures = factures.filter(societe_id=selected_societe_id)
    else:
        factures = factures.none()
    return factures, societes, selected_societe_id


def _get_filtered_achats(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    achats = Achat.objects.select_related('fournisseur', 'agence', 'societe').all()
    if selected_societe_id:
        achats = achats.filter(societe_id=selected_societe_id)
    else:
        achats = achats.none()
    return achats, societes, selected_societe_id


def _get_line_products(selected_societe_id):
    if not selected_societe_id:
        return []
    produits = list(
        Produit.objects.filter(societe_id=selected_societe_id)
        .order_by('nom_produit')
        .values('id', 'nom_produit', 'prix_vente_ht', 'prix_achat_ht', 'taux_tva')
    )
    stocks = Stock.objects.filter(produit__societe_id=selected_societe_id).values('produit_id', 'agence_id', 'quantite_disponible')
    stocks_by_product = {}
    for stock in stocks:
        product_stocks = stocks_by_product.setdefault(stock['produit_id'], {})
        product_stocks[str(stock['agence_id'])] = stock['quantite_disponible']
    for produit in produits:
        produit['stocks_by_agence'] = stocks_by_product.get(produit['id'], {})
    return produits


def _next_numero_ecriture(societe_id=None, journal_id=None, racine='ECR'):
    racine = (racine or 'ECR').strip().upper()
    queryset = EcritureComptable.objects.all()
    if societe_id:
        queryset = queryset.filter(societe_id=societe_id)
    if journal_id:
        queryset = queryset.filter(journal_id=journal_id)

    queryset = queryset.filter(numero_ecriture__startswith=f'{racine}-')

    existing_numeros = queryset.exclude(numero_ecriture__isnull=True).exclude(numero_ecriture='').values_list('numero_ecriture', flat=True)
    max_num = 0
    width = 4
    for numero in existing_numeros:
        match = re.search(r'(\d+)$', str(numero))
        if not match:
            continue
        number_str = match.group(1)
        number_val = int(number_str)
        max_num = max(max_num, number_val)
        width = max(width, len(number_str))

    next_num = max_num + 1
    return f"{racine}-{next_num:0{width}d}"


def _resolve_numero_racine(societe_id=None, journal=None):
    if journal and getattr(journal, 'racine_numero_ecriture', None):
        return str(journal.racine_numero_ecriture).strip().upper()
    if societe_id:
        parametre = ComptabilisationParametre.objects.filter(societe_id=societe_id).first()
        if parametre and parametre.racine_numero_ecriture:
            return str(parametre.racine_numero_ecriture).strip().upper()
    return 'ECR'


def _validate_facture_stock(form, line_formset, instance):
    if form.cleaned_data.get('type_vente') != 'Produit':
        return True

    agence = form.cleaned_data.get('agence')
    if not agence:
        return True

    requested_quantities = {}
    for line_form in line_formset.forms:
        if not hasattr(line_form, 'cleaned_data'):
            continue
        cleaned = line_form.cleaned_data
        if not cleaned or cleaned.get('DELETE'):
            continue
        produit = cleaned.get('produit')
        quantite = cleaned.get('quantite') or 0
        if not produit:
            continue
        requested_quantities[produit.id] = requested_quantities.get(produit.id, 0) + quantite

    if not requested_quantities:
        return True

    current_stocks = {
        stock.produit_id: stock.quantite_disponible
        for stock in Stock.objects.filter(agence=agence, produit_id__in=requested_quantities.keys())
    }

    existing_quantities = {}
    if instance.pk and instance.agence_id == agence.id:
        existing_quantities = {
            item['produit_id']: item['total_quantite']
            for item in instance.lignes_vente.values('produit_id').annotate(total_quantite=Sum('quantite'))
        }

    has_error = False
    for produit_id, requested in requested_quantities.items():
        available = current_stocks.get(produit_id, 0) + existing_quantities.get(produit_id, 0)
        if requested > available:
            has_error = True
            for line_form in line_formset.forms:
                cleaned = getattr(line_form, 'cleaned_data', None)
                if not cleaned or cleaned.get('DELETE'):
                    continue
                produit = cleaned.get('produit')
                if produit and produit.id == produit_id:
                    line_form.add_error('quantite', f'Stock insuffisant. Disponible dans cette agence: {available}.')

    if has_error:
        line_formset._non_form_errors = line_formset.error_class([
            'Impossible d\'enregistrer la vente: une ou plusieurs lignes dépassent le stock disponible.'
        ])
        return False

    return True


def _update_stock_quantity(produit, agence, quantite_delta, prix_unitaire, date_mouvement=None):
    stock, _ = Stock.objects.get_or_create(
        produit=produit,
        agence=agence,
        defaults={
            'quantite_disponible': 0,
            'quantite_reservee': 0,
            'valeur_stock': 0,
        },
    )
    stock.quantite_disponible = max(0, stock.quantite_disponible + quantite_delta)
    stock.valeur_stock = stock.quantite_disponible * (prix_unitaire or produit.prix_achat_ht or 0)
    stock.date_dernier_mouvement = date_mouvement or timezone.now()
    stock.save()


def _reverse_generated_stock_movements(reference_prefix):
    mouvements = list(
        MouvementStock.objects.filter(reference__startswith=reference_prefix)
        .select_related('produit', 'agence')
        .order_by('-id')
    )
    for mouvement in mouvements:
        if mouvement.type_mouvement == 'entree':
            delta = -mouvement.quantite
        elif mouvement.type_mouvement == 'sortie':
            delta = mouvement.quantite
        else:
            delta = 0
        if delta:
            _update_stock_quantity(mouvement.produit, mouvement.agence, delta, mouvement.prix_unitaire, timezone.now())
        mouvement.delete()


def _sync_facture_stock(facture):
    if not facture.pk or not facture.agence_id or facture.type_vente != 'Produit':
        return
    reference_prefix = f"AUTO-VENTE-{facture.pk}-"
    _reverse_generated_stock_movements(reference_prefix)

    for index, ligne in enumerate(facture.lignes_vente.select_related('produit').all(), start=1):
        if not ligne.produit_id:
            continue
        mouvement = MouvementStock.objects.create(
            produit=ligne.produit,
            agence=facture.agence,
            quantite=ligne.quantite,
            type_mouvement='sortie',
            prix_unitaire=ligne.prix_unitaire_ht,
            reference=f"{reference_prefix}{index}",
            motif=f"Sortie automatique depuis la vente {facture.numero_vente}",
            utilisateur=facture.utilisateur,
        )
        _update_stock_quantity(ligne.produit, facture.agence, -ligne.quantite, ligne.prix_unitaire_ht, mouvement.date_mouvement)


def _sync_achat_stock(achat):
    if not achat.pk or not achat.agence_id or achat.type_achat != 'Produit':
        return
    reference_prefix = f"AUTO-ACHAT-{achat.pk}-"
    _reverse_generated_stock_movements(reference_prefix)

    for index, ligne in enumerate(achat.lignes_achat.select_related('produit').all(), start=1):
        if not ligne.produit_id:
            continue
        mouvement = MouvementStock.objects.create(
            produit=ligne.produit,
            agence=achat.agence,
            quantite=ligne.quantite,
            type_mouvement='entree',
            prix_unitaire=ligne.prix_unitaire_ht,
            reference=f"{reference_prefix}{index}",
            motif=f"Entrée automatique depuis l'achat {achat.numero_achat}",
            utilisateur=achat.utilisateur,
        )
        _update_stock_quantity(ligne.produit, achat.agence, ligne.quantite, ligne.prix_unitaire_ht, mouvement.date_mouvement)


def _validate_line_designations(doc_type, line_formset):
    """Valide les lignes selon le type métier: produit vs service/travaux."""
    requires_product = doc_type == 'Produit'
    has_error = False

    for line_form in line_formset.forms:
        cleaned = getattr(line_form, 'cleaned_data', None)
        if not cleaned or cleaned.get('DELETE'):
            continue

        produit = cleaned.get('produit')
        designation = (cleaned.get('designation') or '').strip()

        if requires_product and not produit:
            line_form.add_error('produit', 'Le produit est obligatoire pour une opération de type Produit.')
            has_error = True

        if not requires_product and not designation:
            line_form.add_error('designation', 'La désignation est obligatoire pour Service/Travaux.')
            has_error = True

        if not produit and not designation:
            line_form.add_error('designation', 'Saisissez une désignation ou choisissez un produit.')
            has_error = True

    if has_error:
        line_formset._non_form_errors = line_formset.error_class([
            'Certaines lignes sont invalides par rapport au type de document.'
        ])
        return False

    return True


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
        {'title': 'Achats', 'subtitle': 'Commandes et approvisionnement', 'icon': 'fa-cart-shopping', 'link': 'achats_page', 'color_class': 'bg-danger', 'codes': ['achat_voir', 'fournisseur_voir']},
        {'title': 'Comptabilité', 'subtitle': 'Journaux et écritures', 'icon': 'fa-calculator', 'link': 'comptabilite_page', 'color_class': 'bg-purple', 'codes': ['ecriture_voir', 'journal_voir', 'rapport_comptable_voir']},
        {'title': 'Contacts', 'subtitle': 'Clients et fournisseurs', 'icon': 'fa-address-book', 'link': 'contacts_page', 'color_class': 'bg-teal', 'codes': ['client_voir', 'contact_voir', 'fournisseur_voir']},
        {'title': 'Statistique', 'subtitle': 'Analyses et tableaux de bord', 'icon': 'fa-chart-pie', 'link': 'statistiques', 'color_class': 'bg-success', 'codes': ['statistique_voir', 'rapport_voir']},
        {'title': 'Paramètre', 'subtitle': 'Sociétés et utilisateurs', 'icon': 'fa-gear', 'link': 'parametres_page', 'color_class': 'bg-dark', 'codes': ['utilisateur_voir', 'role_voir', 'societe_voir']},
    ]

    modules = [m for m in all_modules if has(*m['codes'])]

    return render(request, 'core/accueil.html', {'modules': modules})


@login_required
def produits_stock_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    return render(
        request,
        'core/produits_stock_page.html',
        {
            'societes': societes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def ventes_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    return render(
        request,
        'core/ventes_page.html',
        {
            'societes': societes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def achats_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    return render(
        request,
        'core/achats_page.html',
        {
            'societes': societes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def comptabilite_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    return render(
        request,
        'core/comptabilite_page.html',
        {
            'societes': societes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def comptes_tiers_gestion_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    clients = Client.objects.all()
    fournisseurs = Fournisseur.objects.all()
    if selected_societe_id:
        clients = clients.filter(societe_id=selected_societe_id)
        fournisseurs = fournisseurs.filter(societe_id=selected_societe_id)
    else:
        clients = clients.none()
        fournisseurs = fournisseurs.none()

    return render(
        request,
        'core/comptes_tiers_gestion_page.html',
        {
            'clients': clients.order_by('raison_sociale', 'nom')[:100],
            'fournisseurs': fournisseurs.order_by('raison_sociale')[:100],
        },
    )


@login_required
def recherche_ecriture_page(request):
    q = request.GET.get('q', '').strip()
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    ecritures = EcritureComptable.objects.select_related('journal').prefetch_related('lignes__compte').all()
    if selected_societe_id:
        ecritures = ecritures.filter(societe_id=selected_societe_id)
    else:
        ecritures = ecritures.none()
    if q:
        ecritures = ecritures.filter(
            Q(reference__icontains=q)
            | Q(numero_ecriture__icontains=q)
            | Q(intitule__icontains=q)
            | Q(libelle_ecriture__icontains=q)
            | Q(compte__icontains=q)
            | Q(lignes__compte__numero_compte__icontains=q)
            | Q(lignes__compte__nom_compte__icontains=q)
            | Q(journal__nom__icontains=q)
        ).distinct()
    ecritures = ecritures.annotate(total_debit=Sum('lignes__debit'), total_credit=Sum('lignes__credit')).order_by('-date_ecriture', '-id')
    return render(request, 'core/recherche_ecriture_page.html', {'ecritures': ecritures[:200], 'q': q})


@login_required
def caisse_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    caisses = Caisse.objects.select_related('agence', 'agence__societe', 'responsable').all()
    mouvements = MouvementCaisse.objects.select_related('caisse', 'utilisateur').all()
    if selected_societe_id:
        caisses = caisses.filter(agence__societe_id=selected_societe_id)
        mouvements = mouvements.filter(caisse__agence__societe_id=selected_societe_id)
    else:
        caisses = caisses.none()
        mouvements = mouvements.none()
    return render(
        request,
        'core/caisse_list.html',
        {
            'caisses': caisses.order_by('nom_caisse'),
            'mouvements': mouvements.order_by('-date_mouvement')[:40],
        },
    )


@login_required
def caisse_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = CaisseForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Caisse ajoutée avec succès.')
        return _redirect_with_standalone(request, 'caisse_list')
    return render(request, 'core/caisse_form.html', {'form': form, 'title': 'Ajouter une caisse'})


@login_required
def caisse_update(request, pk):
    caisse = get_object_or_404(Caisse, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or caisse.agence.societe_id
    form = CaisseForm(request.POST or None, instance=caisse)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Caisse modifiée avec succès.')
        return _redirect_with_standalone(request, 'caisse_list')
    return render(request, 'core/caisse_form.html', {'form': form, 'title': 'Modifier la caisse'})


@login_required
def caisse_delete(request, pk):
    caisse = get_object_or_404(Caisse, pk=pk)
    if request.method == 'POST':
        caisse.delete()
        messages.success(request, 'Caisse supprimée avec succès.')
        return _redirect_with_standalone(request, 'caisse_list')
    return render(request, 'core/caisse_confirm_delete.html', {'caisse': caisse})


@login_required
def mouvement_caisse_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = MouvementCaisseForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        mouvement = form.save()
        caisse = mouvement.caisse
        if mouvement.type_mouvement == 'Entree':
            caisse.solde_actuel = (caisse.solde_actuel or 0) + mouvement.montant
        else:
            caisse.solde_actuel = (caisse.solde_actuel or 0) - mouvement.montant
        caisse.save(update_fields=['solde_actuel'])
        messages.success(request, 'Mouvement de caisse enregistré avec succès.')
        return _redirect_with_standalone(request, 'caisse_list')
    return render(request, 'core/caisse_form.html', {'form': form, 'title': 'Nouveau mouvement de caisse', 'is_mouvement': True})


@login_required
def banque_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    banques = Banque.objects.select_related('agence', 'agence__societe', 'responsable').all()
    mouvements = MouvementBanque.objects.select_related('banque', 'utilisateur').all()
    if selected_societe_id:
        banques = banques.filter(agence__societe_id=selected_societe_id)
        mouvements = mouvements.filter(banque__agence__societe_id=selected_societe_id)
    else:
        banques = banques.none()
        mouvements = mouvements.none()
    return render(
        request,
        'core/banque_page.html',
        {
            'banques': banques.order_by('nom_banque'),
            'mouvements': mouvements.order_by('-date_mouvement')[:40],
        },
    )


@login_required
def banque_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = BanqueForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Banque ajoutée avec succès.')
        return _redirect_with_standalone(request, 'banque_page')
    return render(request, 'core/banque_form.html', {'form': form, 'title': 'Ajouter une banque'})


@login_required
def banque_update(request, pk):
    banque = get_object_or_404(Banque, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or banque.agence.societe_id
    form = BanqueForm(request.POST or None, instance=banque)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Banque modifiée avec succès.')
        return _redirect_with_standalone(request, 'banque_page')
    return render(request, 'core/banque_form.html', {'form': form, 'title': 'Modifier la banque'})


@login_required
def banque_delete(request, pk):
    banque = get_object_or_404(Banque, pk=pk)
    if request.method == 'POST':
        banque.delete()
        messages.success(request, 'Banque supprimée avec succès.')
        return _redirect_with_standalone(request, 'banque_page')
    return render(request, 'core/banque_confirm_delete.html', {'banque': banque})


@login_required
def mouvement_banque_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = MouvementBanqueForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        mouvement = form.save()
        banque = mouvement.banque
        if mouvement.type_mouvement == 'Entree':
            banque.solde_actuel = (banque.solde_actuel or 0) + mouvement.montant
        else:
            banque.solde_actuel = (banque.solde_actuel or 0) - mouvement.montant
        banque.save(update_fields=['solde_actuel'])
        messages.success(request, 'Mouvement bancaire enregistré avec succès.')
        return _redirect_with_standalone(request, 'banque_page')
    return render(request, 'core/banque_form.html', {'form': form, 'title': 'Nouveau mouvement bancaire', 'is_mouvement': True})


@login_required
def comptabilite_configuration_page(request):
    return render(request, 'core/comptabilite_configuration_page.html')


@login_required
def comptabilisation_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)

    if not selected_societe_id:
        messages.warning(request, "Aucune société accessible pour paramétrer la comptabilisation.")
        return render(
            request,
            'core/comptabilisation_page.html',
            {
                'form': None,
                'selected_societe': None,
            },
        )

    parametre, _ = ComptabilisationParametre.objects.get_or_create(societe_id=selected_societe_id)

    if request.method == 'POST':
        form = ComptabilisationParametreForm(request.POST, instance=parametre, selected_societe_id=selected_societe_id)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres de comptabilisation enregistrés avec succès.')
            return _redirect_with_standalone(request, 'comptabilisation_page')
    else:
        form = ComptabilisationParametreForm(instance=parametre, selected_societe_id=selected_societe_id)

    selected_societe = societes.filter(id=selected_societe_id).first()
    return render(
        request,
        'core/comptabilisation_page.html',
        {
            'form': form,
            'selected_societe': selected_societe,
        },
    )


@login_required
def parametres_page(request):
    return render(request, 'core/parametres_page.html')


@login_required
def contacts_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    return render(
        request,
        'core/contacts_page.html',
        {
            'societes': societes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def etat_ventes_page(request):
    factures, _, _ = _get_filtered_factures(request)
    factures = factures.order_by('-date_vente')
    total_factures = factures.count()
    montant_total = factures.aggregate(total=Sum('montant_ttc'))['total'] or 0
    etats = factures.values('statut_vente').annotate(nombre=Count('id'), montant=Sum('montant_ttc')).order_by('statut_vente')

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
    factures, _, _ = _get_filtered_factures(request)
    factures = factures.order_by('-date_vente')
    lignes = []
    total_ttc = 0
    total_ht = 0
    total_tva = 0

    for facture in factures:
        montant_ttc = facture.montant_ttc or 0
        montant_ht = montant_ttc / (1 + tva_rate)
        montant_tva = montant_ttc - montant_ht
        total_ttc += montant_ttc
        total_ht += montant_ht
        total_tva += montant_tva
        lignes.append(
            {
                'reference': facture.reference,
                'client': facture.client.nom if facture.client else '-',
                'date_emission': facture.date_vente,
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
def paiements_ventes_page(request):
    factures, _, _ = _get_filtered_factures(request)
    factures = factures.order_by('-date_vente')
    total_factures = factures.count()
    total_paye = factures.aggregate(total=Sum('montant_paye'))['total'] or 0
    total_restant = factures.aggregate(total=Sum('montant_restant'))['total'] or 0
    factures_soldees = factures.filter(montant_restant__lte=0).count()
    return render(
        request,
        'core/paiements_ventes_page.html',
        {
            'factures': factures[:50],
            'total_factures': total_factures,
            'total_paye': total_paye,
            'total_restant': total_restant,
            'factures_soldees': factures_soldees,
        },
    )


@login_required
def etat_clients_ventes_page(request):
    factures, _, _ = _get_filtered_factures(request)
    etats_clients = (
        factures.values('client__raison_sociale')
        .annotate(
            nombre=Count('id'),
            total_ttc=Sum('montant_ttc'),
            total_paye=Sum('montant_paye'),
            total_restant=Sum('montant_restant'),
        )
        .order_by('-total_ttc')
    )
    return render(
        request,
        'core/etat_clients_ventes_page.html',
        {
            'etats_clients': etats_clients,
        },
    )


@login_required
def rapport_general_ventes_page(request):
    factures, _, _ = _get_filtered_factures(request)
    total_ventes = factures.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_ht = factures.aggregate(total=Sum('montant_ht'))['total'] or 0
    total_tva = factures.aggregate(total=Sum('montant_tva'))['total'] or 0
    par_type = factures.values('type_vente').annotate(nombre=Count('id'), montant=Sum('montant_ttc')).order_by('type_vente')
    par_statut = factures.values('statut_vente').annotate(nombre=Count('id'), montant=Sum('montant_ttc')).order_by('statut_vente')
    top_clients = (
        factures.values('client__raison_sociale')
        .annotate(total=Sum('montant_ttc'))
        .order_by('-total')[:10]
    )
    return render(
        request,
        'core/rapport_general_ventes_page.html',
        {
            'total_ventes': total_ventes,
            'total_ht': total_ht,
            'total_tva': total_tva,
            'par_type': par_type,
            'par_statut': par_statut,
            'top_clients': top_clients,
        },
    )


@login_required
def tableau_bord_ventes_page(request):
    factures, _, _ = _get_filtered_factures(request)
    total_factures = factures.count()
    total_ventes = factures.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_restant = factures.aggregate(total=Sum('montant_restant'))['total'] or 0
    ventes_comptant = factures.filter(type_vente='Comptant').aggregate(total=Sum('montant_ttc'))['total'] or 0
    ventes_credit = factures.filter(type_vente='Credit').aggregate(total=Sum('montant_ttc'))['total'] or 0
    recentes = factures.order_by('-date_vente')[:10]
    return render(
        request,
        'core/tableau_bord_ventes_page.html',
        {
            'total_factures': total_factures,
            'total_ventes': total_ventes,
            'total_restant': total_restant,
            'ventes_comptant': ventes_comptant,
            'ventes_credit': ventes_credit,
            'factures': recentes,
        },
    )


@login_required
def etat_achats_page(request):
    achats, _, _ = _get_filtered_achats(request)
    achats = achats.order_by('-date_achat')
    total_achats = achats.count()
    montant_total = achats.aggregate(total=Sum('montant_ttc'))['total'] or 0
    etats = achats.values('statut_achat').annotate(nombre=Count('id'), montant=Sum('montant_ttc')).order_by('statut_achat')
    return render(
        request,
        'core/etat_achats_page.html',
        {
            'achats': achats[:20],
            'total_achats': total_achats,
            'montant_total': montant_total,
            'etats': etats,
        },
    )


@login_required
def etat_fournisseurs_achats_page(request):
    achats, _, _ = _get_filtered_achats(request)
    etats_fournisseurs = (
        achats.values('fournisseur__raison_sociale')
        .annotate(
            nombre=Count('id'),
            total_ttc=Sum('montant_ttc'),
            total_paye=Sum('montant_paye'),
            total_restant=Sum('montant_restant'),
        )
        .order_by('-total_ttc')
    )
    return render(
        request,
        'core/etat_fournisseurs_achats_page.html',
        {
            'etats_fournisseurs': etats_fournisseurs,
        },
    )


@login_required
def declaration_fiscale_achats_page(request):
    tva_rate = 0.18
    achats, _, _ = _get_filtered_achats(request)
    achats = achats.order_by('-date_achat')
    lignes = []
    total_ttc = 0
    total_ht = 0
    total_tva = 0
    for achat in achats:
        montant_ttc = achat.montant_ttc or 0
        montant_ht = achat.montant_ht or (montant_ttc / (1 + tva_rate) if montant_ttc else 0)
        montant_tva = achat.montant_tva or (montant_ttc - montant_ht)
        total_ttc += montant_ttc
        total_ht += montant_ht
        total_tva += montant_tva
        lignes.append(
            {
                'reference': achat.numero_achat,
                'fournisseur': achat.fournisseur.nom if achat.fournisseur else '-',
                'date_achat': achat.date_achat,
                'montant_ht': montant_ht,
                'montant_tva': montant_tva,
                'montant_ttc': montant_ttc,
            }
        )
    return render(
        request,
        'core/declaration_fiscale_achats_page.html',
        {
            'tva_rate': int(tva_rate * 100),
            'lignes': lignes[:50],
            'total_ttc': total_ttc,
            'total_ht': total_ht,
            'total_tva': total_tva,
        },
    )


@login_required
def rapport_general_achats_page(request):
    achats, _, _ = _get_filtered_achats(request)
    total_achats = achats.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_ht = achats.aggregate(total=Sum('montant_ht'))['total'] or 0
    total_tva = achats.aggregate(total=Sum('montant_tva'))['total'] or 0
    par_statut = achats.values('statut_achat').annotate(nombre=Count('id'), montant=Sum('montant_ttc')).order_by('statut_achat')
    top_fournisseurs = (
        achats.values('fournisseur__raison_sociale')
        .annotate(total=Sum('montant_ttc'))
        .order_by('-total')[:10]
    )
    return render(
        request,
        'core/rapport_general_achats_page.html',
        {
            'total_achats': total_achats,
            'total_ht': total_ht,
            'total_tva': total_tva,
            'par_statut': par_statut,
            'top_fournisseurs': top_fournisseurs,
        },
    )


@login_required
def tableau_bord_achats_page(request):
    achats, _, _ = _get_filtered_achats(request)
    total_achats_count = achats.count()
    total_achats = achats.aggregate(total=Sum('montant_ttc'))['total'] or 0
    total_restant = achats.aggregate(total=Sum('montant_restant'))['total'] or 0
    total_paye = achats.aggregate(total=Sum('montant_paye'))['total'] or 0
    recentes = achats.order_by('-date_achat')[:10]
    return render(
        request,
        'core/tableau_bord_achats_page.html',
        {
            'total_achats_count': total_achats_count,
            'total_achats': total_achats,
            'total_restant': total_restant,
            'total_paye': total_paye,
            'achats': recentes,
        },
    )


@login_required
def etat_comptabilite_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    ecritures = EcritureComptable.objects.select_related('journal').prefetch_related('lignes__compte').annotate(total_debit=Sum('lignes__debit'), total_credit=Sum('lignes__credit')).order_by('-date_ecriture')
    if selected_societe_id:
        ecritures = ecritures.filter(societe_id=selected_societe_id)
    else:
        ecritures = ecritures.none()
    lignes = LigneEcriture.objects.filter(ecriture__in=ecritures)
    total_ecritures = ecritures.count()
    total_debit = lignes.aggregate(total=Sum('debit'))['total'] or 0
    total_credit = lignes.aggregate(total=Sum('credit'))['total'] or 0
    solde = total_debit - total_credit
    etats_journaux = (
        lignes.values('ecriture__journal__nom')
        .annotate(nombre=Count('ecriture_id', distinct=True), total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('ecriture__journal__nom')
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    comptes = PlanComptable.objects.all()
    if selected_societe_id:
        comptes = comptes.filter(societe_id=selected_societe_id)
    else:
        comptes = comptes.none()
    comptes = comptes.order_by('numero_compte')

    return render(
        request,
        'core/plan_comptable_page.html',
        {
            'comptes': comptes,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def comptes_generaux_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    comptes_mouvementes = (
        LigneEcriture.objects
        .select_related('compte', 'ecriture')
        .values('compte_id', 'compte__numero_compte', 'compte__nom_compte')
        .annotate(
            total_debit=Coalesce(Sum('debit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
            total_credit=Coalesce(Sum('credit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
        )
        .annotate(solde=F('total_debit') - F('total_credit'))
        .order_by('compte__numero_compte')
    )

    if selected_societe_id:
        comptes_mouvementes = comptes_mouvementes.filter(
            compte__societe_id=selected_societe_id,
            ecriture__societe_id=selected_societe_id,
        )
    else:
        comptes_mouvementes = comptes_mouvementes.none()

    return render(
        request,
        'core/comptes_generaux_page.html',
        {
            'comptes_mouvementes': comptes_mouvementes,
            'selected_societe_id': selected_societe_id,
        },
    )


@permission_required('ecriture_ajouter')
def plan_comptable_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = PlanComptableForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Compte comptable ajouté avec succès.')
        return _redirect_with_standalone(request, 'plan_comptable_page')
    return render(request, 'core/plan_comptable_form.html', {'form': form, 'title': 'Ajouter un compte comptable'})


@permission_required('ecriture_modifier')
def plan_comptable_update(request, pk):
    compte = get_object_or_404(PlanComptable, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or compte.societe_id
    form = PlanComptableForm(request.POST or None, instance=compte)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Compte comptable modifié avec succès.')
        return _redirect_with_standalone(request, 'plan_comptable_page')
    return render(request, 'core/plan_comptable_form.html', {'form': form, 'title': 'Modifier le compte comptable'})


@permission_required('ecriture_supprimer')
def plan_comptable_delete(request, pk):
    compte = get_object_or_404(PlanComptable, pk=pk)
    if request.method == 'POST':
        compte.delete()
        messages.success(request, 'Compte comptable supprimé avec succès.')
        return _redirect_with_standalone(request, 'plan_comptable_page')
    return render(request, 'core/plan_comptable_confirm_delete.html', {'compte': compte})


@permission_required('ecriture_ajouter')
@permission_required('ecriture_ajouter')
def plan_comptable_import(request):
    """Import plan comptable from Excel file"""
    from django.core.management import call_command
    import tempfile
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get selected society
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    
    logger.debug(f'[IMPORT DEBUG] User: {request.user}, Accessible societes: {list(societes.values_list("id", flat=True))}, Selected: {selected_societe_id}')
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        # Check if selected society has any line movements
        if selected_societe_id:
            has_movements = LigneEcriture.objects.filter(
                ecriture__societe_id=selected_societe_id
            ).exists()
            
            logger.debug(f'[IMPORT DEBUG] Society {selected_societe_id} has_movements: {has_movements}')
            
            if has_movements:
                messages.error(
                    request, 
                    '❌ Impossible d\'importer le plan comptable: cette société contient déjà des écritures comptables. '
                    'Vous ne pouvez importer le plan comptable que pour une société vierge.'
                )
                return _redirect_with_standalone(request, 'plan_comptable_page')
        
        try:
            excel_file = request.FILES['excel_file']
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', mode='wb') as tmp_file:
                for chunk in excel_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            try:
                # Call import command with societe_id and --clear flag
                cmd_args = [tmp_file_path]
                if selected_societe_id:
                    cmd_args.extend(['--societe_id', str(selected_societe_id)])
                cmd_args.append('--clear')
                call_command('import_plan_comptable', *cmd_args)
                messages.success(request, '✅ Plan comptable importé avec succès!')
            except Exception as e:
                messages.error(request, f'❌ Erreur lors de l\'import: {str(e)}')
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_file_path)
                except Exception:
                    pass
                
        except Exception as e:
            messages.error(request, f'❌ Erreur lors du traitement du fichier: {str(e)}')
    
    return _redirect_with_standalone(request, 'plan_comptable_page')


@permission_required('ecriture_voir')
def ligne_ecriture_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    lignes = LigneEcriture.objects.select_related('ecriture', 'ecriture__journal', 'ecriture__client', 'ecriture__fournisseur', 'compte', 'compte__societe').all()
    if selected_societe_id:
        lignes = lignes.filter(ecriture__societe_id=selected_societe_id)
    else:
        lignes = lignes.none()
    return render(request, 'core/ligne_ecriture_list.html', {'lignes': lignes.order_by('-ecriture__date_ecriture', '-id')})


@permission_required('ecriture_ajouter')
def ligne_ecriture_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = LigneEcritureForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ligne d\'écriture ajoutée avec succès.')
        return _redirect_with_standalone(request, 'ligne_ecriture_list')
    return render(request, 'core/ligne_ecriture_form.html', {'form': form, 'title': 'Ajouter une ligne d\'écriture'})


@permission_required('ecriture_modifier')
def ligne_ecriture_update(request, pk):
    ligne = get_object_or_404(LigneEcriture, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or ligne.ecriture.societe_id
    form = LigneEcritureForm(request.POST or None, instance=ligne)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ligne d\'écriture modifiée avec succès.')
        return _redirect_with_standalone(request, 'ligne_ecriture_list')
    return render(request, 'core/ligne_ecriture_form.html', {'form': form, 'title': 'Modifier la ligne d\'écriture'})


@permission_required('ecriture_supprimer')
def ligne_ecriture_delete(request, pk):
    ligne = get_object_or_404(LigneEcriture, pk=pk)
    if request.method == 'POST':
        ligne.delete()
        messages.success(request, 'Ligne d\'écriture supprimée avec succès.')
        return _redirect_with_standalone(request, 'ligne_ecriture_list')
    return render(request, 'core/ligne_ecriture_confirm_delete.html', {'ligne': ligne})


@login_required
def code_journaux_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    journaux = Journal.objects.select_related('societe', 'compte_defaut').annotate(ecritures_count=Count('ecritures')).order_by('code')
    if selected_societe_id:
        journaux = journaux.filter(societe_id=selected_societe_id)
    else:
        journaux = journaux.none()
    return render(
        request,
        'core/code_journaux_page.html',
        {
            'journaux': journaux,
            'selected_societe_id': selected_societe_id,
        },
    )


@login_required
def brouillard_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    selected_societe = societes.filter(pk=selected_societe_id).first() if selected_societe_id else None
    compte_debut = (request.GET.get('compte_debut') or '').strip()
    compte_fin = (request.GET.get('compte_fin') or '').strip()
    journal_debut = (request.GET.get('journal_debut') or '').strip()
    journal_fin = (request.GET.get('journal_fin') or '').strip()
    date_debut = (request.GET.get('date_debut') or '').strip()
    date_fin = (request.GET.get('date_fin') or '').strip()
    export_format = (request.GET.get('export') or '').strip().lower()

    ecritures = EcritureComptable.objects.select_related('journal').prefetch_related('lignes__compte').annotate(total_debit=Sum('lignes__debit'), total_credit=Sum('lignes__credit')).order_by('-date_ecriture', '-id')
    if selected_societe_id:
        ecritures = ecritures.filter(societe_id=selected_societe_id)
    else:
        ecritures = ecritures.none()

    if journal_debut:
        ecritures = ecritures.filter(journal__code__gte=journal_debut)
    if journal_fin:
        ecritures = ecritures.filter(journal__code__lte=journal_fin)
    if date_debut:
        ecritures = ecritures.filter(date_ecriture__gte=date_debut)
    if date_fin:
        ecritures = ecritures.filter(date_ecriture__lte=date_fin)
    if compte_debut:
        ecritures = ecritures.filter(lignes__compte__numero_compte__gte=compte_debut)
    if compte_fin:
        ecritures = ecritures.filter(lignes__compte__numero_compte__lte=compte_fin)

    ecritures = ecritures.distinct()
    lignes_export = LigneEcriture.objects.select_related(
        'ecriture',
        'ecriture__journal',
        'ecriture__client',
        'ecriture__fournisseur',
        'compte',
    ).filter(ecriture_id__in=ecritures.values_list('id', flat=True)).order_by('ecriture__date_ecriture', 'ecriture__id', 'id')

    if export_format == 'pdf':
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=18,
            rightMargin=18,
            topMargin=18,
            bottomMargin=18,
        )
        styles = getSampleStyleSheet()
        story = []

        societe_label = 'Toutes les sociétés'
        if selected_societe:
            societe_label = f"{selected_societe.raison_sociale} ({selected_societe.code_societe})"
        period_label = f"Du {date_debut or '-'} au {date_fin or '-'}"
        filtre_parts = [f"Période: {period_label}"]
        if compte_debut or compte_fin:
            filtre_parts.append(f"Comptes: {compte_debut or '-'} à {compte_fin or '-'}")
        if journal_debut or journal_fin:
            filtre_parts.append(f"Journaux: {journal_debut or '-'} à {journal_fin or '-'}")

        story.append(Paragraph('Brouillard de saisie - Détail des lignes', styles['Title']))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Société: {societe_label}", styles['Normal']))
        story.append(Paragraph('Filtres: ' + ' | '.join(filtre_parts), styles['Normal']))
        story.append(Spacer(1, 10))

        table_data = [[
            'Code journal',
            'Date',
            'Pièce',
            'Compte',
            'Code tiers',
            'Intitulé',
            'Débit',
            'Crédit',
        ]]
        for ligne in lignes_export:
            code_tiers = getattr(getattr(ligne.ecriture, 'client', None), 'code_client', '') or getattr(getattr(ligne.ecriture, 'fournisseur', None), 'code_fournisseur', '') or '-'
            table_data.append([
                ligne.ecriture.journal.code if ligne.ecriture.journal else '-',
                ligne.ecriture.date_ecriture.strftime('%d/%m/%Y') if ligne.ecriture.date_ecriture else '',
                ligne.ecriture.numero_ecriture or ligne.ecriture.reference or '',
                f"{ligne.compte.numero_compte} - {ligne.compte.nom_compte}",
                code_tiers,
                ligne.ecriture.libelle_ecriture or ligne.ecriture.intitule or '',
                _amount_to_display(ligne.debit),
                _amount_to_display(ligne.credit),
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (6, 1), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(table)
        document.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=brouillard_saisie_{timezone.localdate().year}.pdf'
        return response

    if export_format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=brouillard_saisie_{timezone.localdate().year}.xls'
        columns = ['Code journal', 'Date', 'Pièce', 'Compte', 'Code tiers', 'Intitulé', 'Débit', 'Crédit']
        rows = [
            '<tr>' + ''.join(f'<th>{col}</th>' for col in columns) + '</tr>'
        ]
        for ligne in lignes_export:
            code_tiers = '-'
            if ligne.ecriture.client:
                code_tiers = ligne.ecriture.client.code or ligne.ecriture.client.code_client or '-'
            elif ligne.ecriture.fournisseur:
                code_tiers = ligne.ecriture.fournisseur.code or ligne.ecriture.fournisseur.code_fournisseur or '-'
            debit_value = _amount_to_int(ligne.debit)
            credit_value = _amount_to_int(ligne.credit)
            debit_cell = '<td></td>' if debit_value == 0 else f"<td x:num=\"{debit_value}\" style=\"mso-number-format:'0';text-align:right;\">{debit_value}</td>"
            credit_cell = '<td></td>' if credit_value == 0 else f"<td x:num=\"{credit_value}\" style=\"mso-number-format:'0';text-align:right;\">{credit_value}</td>"
            rows.append(
                '<tr>'
                f"<td>{ligne.ecriture.journal.code if ligne.ecriture.journal else '-'}</td>"
                f"<td>{ligne.ecriture.date_ecriture.strftime('%d/%m/%Y') if ligne.ecriture.date_ecriture else ''}</td>"
                f"<td>{ligne.ecriture.numero_ecriture or ligne.ecriture.reference or ''}</td>"
                f"<td>{ligne.compte.numero_compte} - {ligne.compte.nom_compte}</td>"
                f"<td>{code_tiers}</td>"
                f"<td>{ligne.ecriture.libelle_ecriture or ligne.ecriture.intitule or ''}</td>"
                f"{debit_cell}"
                f"{credit_cell}"
                '</tr>'
            )
        response.write('<html><head><meta charset="utf-8"></head><body><table border="1">')
        response.write(''.join(rows))
        response.write('</table></body></html>')
        return response

    return render(
        request,
        'core/brouillard_page.html',
        {
            'ecritures': ecritures[:100],
            'compte_debut': compte_debut,
            'compte_fin': compte_fin,
            'journal_debut': journal_debut,
            'journal_fin': journal_fin,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'selected_societe': selected_societe,
        },
    )


@login_required
def etat_journaux_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    lignes = LigneEcriture.objects.select_related('ecriture__journal')
    if selected_societe_id:
        lignes = lignes.filter(ecriture__societe_id=selected_societe_id)
    else:
        lignes = lignes.none()
    journaux = (
        lignes.values('ecriture__journal__code', 'ecriture__journal__nom')
        .annotate(nombre=Count('ecriture_id', distinct=True), total_debit=Sum('debit'), total_credit=Sum('credit'))
        .order_by('ecriture__journal__code')
    )
    return render(request, 'core/etat_journaux_page.html', {'journaux': journaux})


@login_required
def balance_comptes_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    compte_debut = (request.GET.get('compte_debut') or '').strip()
    compte_fin = (request.GET.get('compte_fin') or '').strip()
    journal_debut = (request.GET.get('journal_debut') or '').strip()
    journal_fin = (request.GET.get('journal_fin') or '').strip()
    date_debut = (request.GET.get('date_debut') or '').strip()
    date_fin = (request.GET.get('date_fin') or '').strip()
    type_balance = (request.GET.get('type_balance') or '6').strip()
    export_format = (request.GET.get('export') or '').strip().lower()
    annee_n = timezone.localdate().year
    debut_annee = timezone.localdate().replace(month=1, day=1)

    if type_balance not in {'4', '6'}:
        type_balance = '6'

    lignes = LigneEcriture.objects.select_related('compte', 'ecriture__journal')
    if selected_societe_id:
        lignes = lignes.filter(compte__societe_id=selected_societe_id)
    else:
        lignes = lignes.none()

    if compte_debut:
        lignes = lignes.filter(compte__numero_compte__gte=compte_debut)
    if compte_fin:
        lignes = lignes.filter(compte__numero_compte__lte=compte_fin)
    if journal_debut:
        lignes = lignes.filter(ecriture__journal__code__gte=journal_debut)
    if journal_fin:
        lignes = lignes.filter(ecriture__journal__code__lte=journal_fin)

    ouverture_limite = debut_annee
    mouvement_q = Q(ecriture__date_ecriture__gte=debut_annee)
    if date_debut:
        ouverture_limite = date_debut
        mouvement_q = Q(ecriture__date_ecriture__gte=date_debut)
    if date_fin:
        mouvement_q &= Q(ecriture__date_ecriture__lte=date_fin)

    balances = list(
        lignes.values('compte__numero_compte', 'compte__nom_compte')
        .annotate(
            ouverture_debit=Coalesce(
                Sum('debit', filter=Q(ecriture__date_ecriture__lt=ouverture_limite)),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
            ouverture_credit=Coalesce(
                Sum('credit', filter=Q(ecriture__date_ecriture__lt=ouverture_limite)),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
            mouvement_debit=Coalesce(
                Sum('debit', filter=mouvement_q),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
            mouvement_credit=Coalesce(
                Sum('credit', filter=mouvement_q),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
        )
        .order_by('compte__numero_compte')
    )

    periode_debut_label = date_debut or debut_annee.strftime('%Y-%m-%d')
    periode_fin_label = date_fin or timezone.localdate().strftime('%Y-%m-%d')

    for ligne in balances:
        periode_debit = (ligne['ouverture_debit'] or 0) + (ligne['mouvement_debit'] or 0)
        periode_credit = (ligne['ouverture_credit'] or 0) + (ligne['mouvement_credit'] or 0)
        solde_cloture = periode_debit - periode_credit
        ligne['periode_debit'] = periode_debit
        ligne['periode_credit'] = periode_credit
        ligne['solde_ouverture_debit'] = ligne['ouverture_debit'] or 0
        ligne['solde_ouverture_credit'] = ligne['ouverture_credit'] or 0
        ligne['solde_mouvement_debit'] = ligne['mouvement_debit'] or 0
        ligne['solde_mouvement_credit'] = ligne['mouvement_credit'] or 0
        ligne['solde_cloture_debit'] = solde_cloture if solde_cloture > 0 else 0
        ligne['solde_cloture_credit'] = abs(solde_cloture) if solde_cloture < 0 else 0
        ligne['numero_compte'] = ligne.pop('compte__numero_compte')
        ligne['nom_compte'] = ligne.pop('compte__nom_compte')

    if export_format == 'pdf':
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=18,
            rightMargin=18,
            topMargin=18,
            bottomMargin=18,
        )
        styles = getSampleStyleSheet()
        story = []
        societe = Societe.objects.filter(pk=selected_societe_id).only('raison_sociale', 'code_societe').first() if selected_societe_id else None
        period_debut = '/'.join(reversed(periode_debut_label.split('-'))) if '-' in periode_debut_label else periode_debut_label
        period_fin = '/'.join(reversed(periode_fin_label.split('-'))) if '-' in periode_fin_label else periode_fin_label
        filtre_parts = []
        if compte_debut or compte_fin:
            filtre_parts.append(f"Comptes: {compte_debut or '-'} à {compte_fin or '-'}")
        if journal_debut or journal_fin:
            filtre_parts.append(f"Journaux: {journal_debut or '-'} à {journal_fin or '-'}")
        filtre_parts.append(f"Type: {type_balance} colonnes")

        story.append(Paragraph(f"Balance des comptes - Année {annee_n}", styles['Title']))
        story.append(Spacer(1, 8))
        societe_label = 'Toutes les sociétés'
        if societe:
            societe_label = f"{societe.raison_sociale} ({societe.code_societe})"
        story.append(Paragraph(f"Société: {societe_label}", styles['Normal']))
        story.append(Paragraph(f"Période: du {period_debut} au {period_fin}", styles['Normal']))
        story.append(Paragraph('Filtres: ' + ' | '.join(filtre_parts), styles['Normal']))
        story.append(Spacer(1, 10))

        if type_balance == '6':
            table_data = [[
                'Compte',
                'Ouverture débit',
                'Ouverture crédit',
                'Mouvements débit',
                'Mouvements crédit',
                'Clôture débit',
                'Clôture crédit',
            ]]
            for ligne in balances:
                table_data.append([
                    f"{ligne['numero_compte']} - {ligne['nom_compte']}",
                    _amount_to_display(ligne['solde_ouverture_debit']),
                    _amount_to_display(ligne['solde_ouverture_credit']),
                    _amount_to_display(ligne['solde_mouvement_debit']),
                    _amount_to_display(ligne['solde_mouvement_credit']),
                    _amount_to_display(ligne['solde_cloture_debit']),
                    _amount_to_display(ligne['solde_cloture_credit']),
                ])
        else:
            table_data = [[
                'Compte',
                'Ouverture + mouvements débit',
                'Ouverture + mouvements crédit',
                'Clôture débit',
                'Clôture crédit',
            ]]
            for ligne in balances:
                table_data.append([
                    f"{ligne['numero_compte']} - {ligne['nom_compte']}",
                    _amount_to_display(ligne['periode_debit']),
                    _amount_to_display(ligne['periode_credit']),
                    _amount_to_display(ligne['solde_cloture_debit']),
                    _amount_to_display(ligne['solde_cloture_credit']),
                ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(table)
        document.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=balance_comptable_{annee_n}.pdf'
        return response

    if export_format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=balance_comptable_{annee_n}.xls'
        columns = ['Compte', 'Intitulé']
        if type_balance == '6':
            columns.extend(['Ouverture débit', 'Ouverture crédit', 'Mouvements débit', 'Mouvements crédit', 'Clôture débit', 'Clôture crédit'])
        else:
            columns.extend(['Ouverture + mouvements débit', 'Ouverture + mouvements crédit', 'Clôture débit', 'Clôture crédit'])
        rows = [
            '<tr>' + ''.join(f'<th>{col}</th>' for col in columns) + '</tr>'
        ]
        for ligne in balances:
            current = [
                ligne['numero_compte'],
                ligne['nom_compte'],
            ]
            if type_balance == '6':
                current.extend([
                    _amount_to_display(ligne['solde_ouverture_debit']),
                    _amount_to_display(ligne['solde_ouverture_credit']),
                    _amount_to_display(ligne['solde_mouvement_debit']),
                    _amount_to_display(ligne['solde_mouvement_credit']),
                    _amount_to_display(ligne['solde_cloture_debit']),
                    _amount_to_display(ligne['solde_cloture_credit']),
                ])
            else:
                current.extend([
                    _amount_to_display(ligne['periode_debit']),
                    _amount_to_display(ligne['periode_credit']),
                    _amount_to_display(ligne['solde_cloture_debit']),
                    _amount_to_display(ligne['solde_cloture_credit']),
                ])
            rows.append('<tr>' + ''.join(f'<td>{value}</td>' for value in current) + '</tr>')
        response.write('<html><head><meta charset="utf-8"></head><body><table border="1">')
        response.write(''.join(rows))
        response.write('</table></body></html>')
        return response

    context = {
        'balances': balances,
        'compte_debut': compte_debut,
        'compte_fin': compte_fin,
        'journal_debut': journal_debut,
        'journal_fin': journal_fin,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'type_balance': type_balance if type_balance in {'4', '6'} else '6',
        'annee_n': annee_n,
        'print_mode': export_format == 'pdf',
    }
    return render(request, 'core/balance_comptes_page.html', context)


@login_required
def grand_livre_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    selected_societe = societes.filter(pk=selected_societe_id).first() if selected_societe_id else None
    compte_debut = (request.GET.get('compte_debut') or '').strip()
    compte_fin = (request.GET.get('compte_fin') or '').strip()
    journal_debut = (request.GET.get('journal_debut') or '').strip()
    journal_fin = (request.GET.get('journal_fin') or '').strip()
    date_debut = (request.GET.get('date_debut') or '').strip()
    date_fin = (request.GET.get('date_fin') or '').strip()
    export_format = (request.GET.get('export') or '').strip().lower()

    lignes = LigneEcriture.objects.select_related('ecriture', 'ecriture__journal', 'ecriture__client', 'ecriture__fournisseur', 'compte').order_by('compte__numero_compte', 'ecriture__date_ecriture', 'id')
    if selected_societe_id:
        lignes = lignes.filter(ecriture__societe_id=selected_societe_id)
    else:
        lignes = lignes.none()

    if compte_debut:
        lignes = lignes.filter(compte__numero_compte__gte=compte_debut)
    if compte_fin:
        lignes = lignes.filter(compte__numero_compte__lte=compte_fin)
    if journal_debut:
        lignes = lignes.filter(ecriture__journal__code__gte=journal_debut)
    if journal_fin:
        lignes = lignes.filter(ecriture__journal__code__lte=journal_fin)
    if date_debut:
        lignes = lignes.filter(ecriture__date_ecriture__gte=date_debut)
    if date_fin:
        lignes = lignes.filter(ecriture__date_ecriture__lte=date_fin)

    lignes = list(lignes[:500])
    last_compte = None
    solde_progressif = 0
    for ligne in lignes:
        compte_key = ligne.compte.numero_compte
        if compte_key != last_compte:
            solde_progressif = 0
            last_compte = compte_key
        solde_progressif += (ligne.debit or 0) - (ligne.credit or 0)
        ligne.solde_progressif = solde_progressif

    annee_n = timezone.localdate().year
    period_label = 'Toutes les dates'
    if date_debut or date_fin:
        period_label = f"Du {date_debut or '-'} au {date_fin or '-'}"

    if export_format == 'pdf':
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=18,
            rightMargin=18,
            topMargin=18,
            bottomMargin=18,
        )
        styles = getSampleStyleSheet()
        story = []

        societe_label = 'Toutes les sociétés'
        if selected_societe:
            societe_label = f"{selected_societe.raison_sociale} ({selected_societe.code_societe})"
        filtre_parts = [f"Période: {period_label}"]
        if compte_debut or compte_fin:
            filtre_parts.append(f"Comptes: {compte_debut or '-'} à {compte_fin or '-'}")
        if journal_debut or journal_fin:
            filtre_parts.append(f"Journaux: {journal_debut or '-'} à {journal_fin or '-'}")

        story.append(Paragraph('Grand livre', styles['Title']))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Société: {societe_label}", styles['Normal']))
        story.append(Paragraph('Filtres: ' + ' | '.join(filtre_parts), styles['Normal']))
        story.append(Spacer(1, 10))

        table_data = [[
            'Code journaux',
            'Date',
            'Pièce',
            'Compte',
            'Code tiers',
            'Intitulés',
            'Débit',
            'Crédit',
            'Solde progressif',
        ]]
        for ligne in lignes:
            table_data.append([
                ligne.ecriture.journal.code if ligne.ecriture.journal else '-',
                ligne.ecriture.date_ecriture.strftime('%d/%m/%Y') if ligne.ecriture.date_ecriture else '',
                ligne.ecriture.numero_ecriture or ligne.ecriture.reference or '',
                f"{ligne.compte.numero_compte} - {ligne.compte.nom_compte}",
                getattr(getattr(ligne.ecriture, 'client', None), 'code_client', '') or getattr(getattr(ligne.ecriture, 'fournisseur', None), 'code_fournisseur', '') or '-',
                ligne.ecriture.libelle_ecriture or ligne.ecriture.intitule or '',
                _amount_to_display(ligne.debit),
                _amount_to_display(ligne.credit),
                _amount_to_display(ligne.solde_progressif),
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (6, 1), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(table)
        document.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=grand_livre_{annee_n}.pdf'
        return response

    if export_format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=grand_livre_{annee_n}.xls'
        columns = ['Code journaux', 'Date', 'Pièce', 'Compte', 'Code tiers', 'Intitulés', 'Débit', 'Crédit', 'Solde progressif']
        rows = [
            '<tr>' + ''.join(f'<th>{col}</th>' for col in columns) + '</tr>'
        ]
        for ligne in lignes:
            code_tiers = '-'
            if ligne.ecriture.client:
                code_tiers = ligne.ecriture.client.code or ligne.ecriture.client.code_client or '-'
            elif ligne.ecriture.fournisseur:
                code_tiers = ligne.ecriture.fournisseur.code or ligne.ecriture.fournisseur.code_fournisseur or '-'
            debit_value = _amount_to_int(ligne.debit)
            credit_value = _amount_to_int(ligne.credit)
            solde_value = _amount_to_int(ligne.solde_progressif)
            debit_cell = '<td></td>' if debit_value == 0 else f"<td x:num=\"{debit_value}\" style=\"mso-number-format:'0';text-align:right;\">{debit_value}</td>"
            credit_cell = '<td></td>' if credit_value == 0 else f"<td x:num=\"{credit_value}\" style=\"mso-number-format:'0';text-align:right;\">{credit_value}</td>"
            solde_cell = '<td></td>' if solde_value == 0 else f"<td x:num=\"{solde_value}\" style=\"mso-number-format:'0';text-align:right;\">{solde_value}</td>"
            rows.append(
                '<tr>'
                f"<td>{ligne.ecriture.journal.code if ligne.ecriture.journal else '-'}</td>"
                f"<td>{ligne.ecriture.date_ecriture.strftime('%d/%m/%Y') if ligne.ecriture.date_ecriture else ''}</td>"
                f"<td>{ligne.ecriture.numero_ecriture or ligne.ecriture.reference or ''}</td>"
                f"<td>{ligne.compte.numero_compte}</td>"
                f"<td>{code_tiers}</td>"
                f"<td>{ligne.ecriture.libelle_ecriture or ligne.ecriture.intitule or ''}</td>"
                f"{debit_cell}"
                f"{credit_cell}"
                f"{solde_cell}"
                '</tr>'
            )
        response.write('<html><head><meta charset="utf-8"></head><body><table border="1">')
        response.write(''.join(rows))
        response.write('</table></body></html>')
        return response

    return render(
        request,
        'core/grand_livre_page.html',
        {
            'lignes': lignes,
            'compte_debut': compte_debut,
            'compte_fin': compte_fin,
            'journal_debut': journal_debut,
            'journal_fin': journal_fin,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'selected_societe': selected_societe,
            'period_label': period_label,
        },
    )


@login_required
def etats_tiers_page(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    
    # Récupérer les lignes d'écriture des comptes tiers (401, 411, etc.)
    lignes_tiers = (
        LigneEcriture.objects
        .select_related('ecriture', 'compte')
        .filter(
            compte__numero_compte__regex=r'^(40|41)',  # Comptes tiers (401=Fournisseurs, 411=Clients)
            ecriture__societe_id=selected_societe_id if selected_societe_id else Q()
        )
    )
    
    if not selected_societe_id:
        lignes_tiers = lignes_tiers.none()
    
    # Mouvements par client (débits/crédits des comptes tiers)
    top_clients = (
        lignes_tiers
        .filter(ecriture__client__isnull=False)
        .values('ecriture__client__id', 'ecriture__client__raison_sociale', 'ecriture__client__code_client')
        .annotate(
            nombre_ecritures=Count('ecriture__id', distinct=True),
            total_debit=Coalesce(Sum('debit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
            total_credit=Coalesce(Sum('credit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
        )
        .annotate(
            solde=F('total_debit') - F('total_credit')
        )
        .order_by('-total_debit')
    )
    
    # Mouvements par fournisseur (débits/crédits des comptes tiers)
    top_fournisseurs = (
        lignes_tiers
        .filter(ecriture__fournisseur__isnull=False)
        .values('ecriture__fournisseur__id', 'ecriture__fournisseur__raison_sociale', 'ecriture__fournisseur__code_fournisseur')
        .annotate(
            nombre_ecritures=Count('ecriture__id', distinct=True),
            total_debit=Coalesce(Sum('debit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
            total_credit=Coalesce(Sum('credit'), Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))),
        )
        .annotate(
            solde=F('total_debit') - F('total_credit')
        )
        .order_by('-total_debit')
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)

    produits = Produit.objects.annotate(
        quantite_stock_calculee=Coalesce(Sum('stocks__quantite_disponible'), 0)
    ).order_by('nom_produit')

    if selected_societe_id:
        produits = produits.filter(societe_id=selected_societe_id)
        total_quantite = Stock.objects.filter(produit__societe_id=selected_societe_id).aggregate(total=Sum('quantite_disponible'))['total'] or 0
    else:
        produits = produits.none()
        total_quantite = 0

    total_produits = produits.count()
    produits_rupture = sum(1 for produit in produits if produit.quantite_stock_calculee <= (produit.stock_alerte or 0))

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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)

    stocks_qs = (
        Stock.objects.select_related('produit', 'agence', 'produit__categorie')
        .order_by('produit__nom_produit', 'agence__nom')
    )
    if selected_societe_id:
        stocks_qs = stocks_qs.filter(produit__societe_id=selected_societe_id)
    else:
        stocks_qs = stocks_qs.none()

    stocks = list(stocks_qs)
    return render(request, 'core/inventaire_stock_page.html', {'stocks': stocks})


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
        return _redirect_with_standalone(request, 'societe_list')
    return render(request, 'core/societe_form.html', {'form': form, 'title': 'Ajouter une société'})


@login_required
def societe_update(request, pk):
    societe = get_object_or_404(Societe, pk=pk)
    form = SocieteForm(request.POST or None, instance=societe)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Société modifiée avec succès.')
        return _redirect_with_standalone(request, 'societe_list')
    return render(request, 'core/societe_form.html', {'form': form, 'title': 'Modifier la société'})


@login_required
def societe_delete(request, pk):
    societe = get_object_or_404(Societe, pk=pk)
    if request.method == 'POST':
        societe.delete()
        messages.success(request, 'Société supprimée avec succès.')
        return _redirect_with_standalone(request, 'societe_list')
    return render(request, 'core/societe_confirm_delete.html', {'societe': societe})


@permission_required('client_voir')
def client_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    clients = Client.objects.select_related('societe').all()
    if selected_societe_id:
        clients = clients.filter(societe_id=selected_societe_id)
    else:
        clients = clients.none()
    return render(request, 'core/client_list.html', {'clients': clients})


@permission_required('client_ajouter')
def client_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = ClientForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Client ajouté avec succès.')
        return _redirect_with_standalone(request, 'client_list')
    return render(request, 'core/client_form.html', {'form': form, 'title': 'Ajouter un client'})


@permission_required('client_voir')
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or client.societe_id
    form = ClientForm(request.POST or None, instance=client)
    _configure_form_for_societe(form, request.user, selected_societe_id)
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    factures = Facture.objects.select_related('client', 'agence', 'societe', 'projet').all()
    if selected_societe_id:
        factures = factures.filter(societe_id=selected_societe_id)
    else:
        factures = factures.none()
    return render(request, 'core/facture_list.html', {'factures': factures})


@permission_required('facture_ajouter')
def facture_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    facture = Facture()
    form = FactureForm(request.POST or None, instance=facture)
    line_formset = LigneVenteFormSet(request.POST or None, instance=facture, prefix='lignes')
    line_products = _get_line_products(selected_societe_id)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_line_formset_for_societe(line_formset, selected_societe_id)
    is_valid = request.method == 'POST' and form.is_valid() and line_formset.is_valid()
    if is_valid and _validate_line_designations(form.cleaned_data.get('type_vente'), line_formset) and _validate_facture_stock(form, line_formset, facture):
        with transaction.atomic():
            instance = form.save(commit=False)
            instance.utilisateur = request.user
            instance.save()
            line_formset.instance = instance
            line_formset.save()
            instance.recalculer_totaux()
            _sync_facture_stock(instance)
        messages.success(request, 'Vente ajoutée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_form.html', {'form': form, 'line_formset': line_formset, 'line_products': line_products, 'title': 'Ajouter une vente'})


@permission_required('facture_modifier')
def facture_update(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or facture.societe_id
    form = FactureForm(request.POST or None, instance=facture)
    line_formset = LigneVenteFormSet(request.POST or None, instance=facture, prefix='lignes')
    line_products = _get_line_products(selected_societe_id)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_line_formset_for_societe(line_formset, selected_societe_id)
    is_valid = request.method == 'POST' and form.is_valid() and line_formset.is_valid()
    if is_valid and _validate_line_designations(form.cleaned_data.get('type_vente'), line_formset) and _validate_facture_stock(form, line_formset, facture):
        with transaction.atomic():
            instance = form.save(commit=False)
            if not instance.utilisateur_id:
                instance.utilisateur = request.user
            instance.save()
            line_formset.instance = instance
            line_formset.save()
            instance.recalculer_totaux()
            _sync_facture_stock(instance)
        messages.success(request, 'Vente modifiée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_form.html', {'form': form, 'line_formset': line_formset, 'line_products': line_products, 'title': 'Modifier la vente'})


@permission_required('facture_supprimer')
def facture_delete(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        _reverse_generated_stock_movements(f"AUTO-VENTE-{facture.pk}-")
        facture.delete()
        messages.success(request, 'Facture supprimée avec succès.')
        return _redirect_with_standalone(request, 'facture_list')
    return render(request, 'core/facture_confirm_delete.html', {'facture': facture})


@permission_required('produit_voir')
def produit_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    produits = Produit.objects.all()
    if selected_societe_id:
        produits = produits.filter(societe_id=selected_societe_id)
    else:
        produits = produits.none()
    return render(request, 'core/produit_list.html', {'produits': produits})


@permission_required('produit_ajouter')
def produit_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = ProduitForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit ajouté avec succès.')
        return _redirect_with_standalone(request, 'produit_list')
    return render(request, 'core/produit_form.html', {'form': form, 'title': 'Ajouter un produit'})


@permission_required('produit_modifier')
def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or produit.societe_id
    form = ProduitForm(request.POST or None, instance=produit)
    _configure_form_for_societe(form, request.user, selected_societe_id)
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    q = request.GET.get('q', '').strip()
    ville = request.GET.get('ville', '').strip()
    agences = Agence.objects.select_related('societe').all()
    selected_societe = None

    if selected_societe_id:
        selected_societe = get_object_or_404(Societe, pk=selected_societe_id)
        agences = agences.filter(societe_id=selected_societe_id)
    else:
        agences = agences.none()

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

    villes = Agence.objects.exclude(ville__isnull=True).exclude(ville__exact='')
    if selected_societe_id:
        villes = villes.filter(societe_id=selected_societe_id)
    else:
        villes = villes.none()
    villes = villes.order_by('ville').values_list('ville', flat=True).distinct()

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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = AgenceForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        if selected_societe_id:
            instance.societe_id = selected_societe_id
        instance.save()
        messages.success(request, 'Agence ajoutée avec succès.')
        return _redirect_with_standalone(request, 'agence_list')
    context = {
        'form': form,
        'title': 'Ajouter une agence',
        'societe_id': selected_societe_id,
    }
    return render(request, 'core/agence_form.html', context)


@login_required
def agence_update(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or agence.societe_id
    form = AgenceForm(request.POST or None, instance=agence)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agence modifiée avec succès.')
        return _redirect_with_standalone(request, 'agence_list')
    return render(request, 'core/agence_form.html', {'form': form, 'title': 'Modifier l\'agence', 'societe_id': selected_societe_id})


@login_required
def agence_delete(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    if request.method == 'POST':
        agence.delete()
        messages.success(request, 'Agence supprimée avec succès.')
        return _redirect_with_standalone(request, 'agence_list')
    return render(request, 'core/agence_confirm_delete.html', {'agence': agence})


# ============ CATEGORIE CRUD ============

@login_required
def categorie_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    categories = Categorie.objects.all()
    if selected_societe_id:
        categories = categories.filter(societe_id=selected_societe_id)
    else:
        categories = categories.none()
    return render(request, 'core/categorie_list.html', {'categories': categories})


@login_required
def categorie_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = CategorieForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Catégorie ajoutée avec succès.')
        return _redirect_with_standalone(request, 'categorie_list')
    return render(request, 'core/categorie_form.html', {'form': form, 'title': 'Ajouter une catégorie'})


@login_required
def categorie_update(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or categorie.societe_id
    form = CategorieForm(request.POST or None, instance=categorie)
    _configure_form_for_societe(form, request.user, selected_societe_id)
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    projets = Projet.objects.select_related('societe', 'agence').all()
    if selected_societe_id:
        projets = projets.filter(societe_id=selected_societe_id)
    else:
        projets = projets.none()
    return render(request, 'core/projet_list.html', {'projets': projets})


@login_required
def projet_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = ProjetForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet ajouté avec succès.')
        return _redirect_with_standalone(request, 'projet_list')
    return render(request, 'core/projet_form.html', {'form': form, 'title': 'Ajouter un projet'})


@login_required
def projet_update(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or projet.societe_id
    form = ProjetForm(request.POST or None, instance=projet)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet modifié avec succès.')
        return _redirect_with_standalone(request, 'projet_list')
    return render(request, 'core/projet_form.html', {'form': form, 'title': 'Modifier le projet'})


@login_required
def projet_delete(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    if request.method == 'POST':
        projet.delete()
        messages.success(request, 'Projet supprimé avec succès.')
        return _redirect_with_standalone(request, 'projet_list')
    return render(request, 'core/projet_confirm_delete.html', {'projet': projet})


@login_required
def marche_list(request):
    return render(request, 'core/marche_list.html')


# ============ FOURNISSEUR CRUD ============

@permission_required('fournisseur_voir')
def fournisseur_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    fournisseurs = Fournisseur.objects.select_related('societe').all()
    if selected_societe_id:
        fournisseurs = fournisseurs.filter(societe_id=selected_societe_id)
    else:
        fournisseurs = fournisseurs.none()
    return render(request, 'core/fournisseur_list.html', {'fournisseurs': fournisseurs})


@permission_required('fournisseur_ajouter')
def fournisseur_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = FournisseurForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fournisseur ajouté avec succès.')
        return _redirect_with_standalone(request, 'fournisseur_list')
    return render(request, 'core/fournisseur_form.html', {'form': form, 'title': 'Ajouter un fournisseur'})


@permission_required('fournisseur_voir')
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or fournisseur.societe_id
    form = FournisseurForm(request.POST or None, instance=fournisseur)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fournisseur modifié avec succès.')
        return _redirect_with_standalone(request, 'fournisseur_list')
    return render(request, 'core/fournisseur_form.html', {'form': form, 'title': 'Modifier le fournisseur'})


@permission_required('fournisseur_voir')
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
        return _redirect_with_standalone(request, 'fournisseur_list')
    return render(request, 'core/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})


# ============ ACHAT CRUD ============

@permission_required('achat_voir')
def achat_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    achats = Achat.objects.select_related('fournisseur', 'agence', 'societe', 'projet').all()
    if selected_societe_id:
        achats = achats.filter(societe_id=selected_societe_id)
    else:
        achats = achats.none()
    return render(request, 'core/achat_list.html', {'achats': achats})


@permission_required('achat_ajouter')
def achat_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    achat = Achat()
    form = AchatForm(request.POST or None, instance=achat)
    line_formset = LigneAchatFormSet(request.POST or None, instance=achat, prefix='lignes')
    line_products = _get_line_products(selected_societe_id)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_line_formset_for_societe(line_formset, selected_societe_id)
    is_valid = request.method == 'POST' and form.is_valid() and line_formset.is_valid()
    if is_valid and _validate_line_designations(form.cleaned_data.get('type_achat'), line_formset):
        with transaction.atomic():
            instance = form.save(commit=False)
            instance.utilisateur = request.user
            instance.save()
            line_formset.instance = instance
            line_formset.save()
            instance.recalculer_totaux()
            _sync_achat_stock(instance)
        messages.success(request, 'Achat ajouté avec succès.')
        return _redirect_with_standalone(request, 'achat_list')
    return render(request, 'core/achat_form.html', {'form': form, 'line_formset': line_formset, 'line_products': line_products, 'title': 'Ajouter un achat'})


@permission_required('achat_modifier')
def achat_update(request, pk):
    achat = get_object_or_404(Achat, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or achat.societe_id
    form = AchatForm(request.POST or None, instance=achat)
    line_formset = LigneAchatFormSet(request.POST or None, instance=achat, prefix='lignes')
    line_products = _get_line_products(selected_societe_id)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_line_formset_for_societe(line_formset, selected_societe_id)
    is_valid = request.method == 'POST' and form.is_valid() and line_formset.is_valid()
    if is_valid and _validate_line_designations(form.cleaned_data.get('type_achat'), line_formset):
        with transaction.atomic():
            instance = form.save(commit=False)
            if not instance.utilisateur_id:
                instance.utilisateur = request.user
            instance.save()
            line_formset.instance = instance
            line_formset.save()
            instance.recalculer_totaux()
            _sync_achat_stock(instance)
        messages.success(request, 'Achat modifié avec succès.')
        return _redirect_with_standalone(request, 'achat_list')
    return render(request, 'core/achat_form.html', {'form': form, 'line_formset': line_formset, 'line_products': line_products, 'title': 'Modifier l\'achat'})


@permission_required('achat_supprimer')
def achat_delete(request, pk):
    achat = get_object_or_404(Achat, pk=pk)
    if request.method == 'POST':
        _reverse_generated_stock_movements(f"AUTO-ACHAT-{achat.pk}-")
        achat.delete()
        messages.success(request, 'Achat supprimé avec succès.')
        return _redirect_with_standalone(request, 'achat_list')
    return render(request, 'core/achat_confirm_delete.html', {'achat': achat})


# ============ DEPENSE CRUD ============

@login_required
def depense_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    depenses = Depense.objects.select_related('societe', 'agence', 'projet').all()
    if selected_societe_id:
        depenses = depenses.filter(societe_id=selected_societe_id)
    else:
        depenses = depenses.none()
    return render(request, 'core/depense_list.html', {'depenses': depenses})


@login_required
def depense_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = DepenseForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        if selected_societe_id:
            instance.societe_id = selected_societe_id
        instance.save()
        messages.success(request, 'Dépense ajoutée avec succès.')
        return _redirect_with_standalone(request, 'depense_list')
    return render(request, 'core/depense_form.html', {'form': form, 'title': 'Ajouter une dépense'})


@login_required
def depense_update(request, pk):
    depense = get_object_or_404(Depense, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or depense.societe_id
    form = DepenseForm(request.POST or None, instance=depense)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Dépense modifiée avec succès.')
        return _redirect_with_standalone(request, 'depense_list')
    return render(request, 'core/depense_form.html', {'form': form, 'title': 'Modifier la dépense'})


@login_required
def depense_delete(request, pk):
    depense = get_object_or_404(Depense, pk=pk)
    if request.method == 'POST':
        depense.delete()
        messages.success(request, 'Dépense supprimée avec succès.')
        return _redirect_with_standalone(request, 'depense_list')
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
        return _redirect_with_standalone(request, 'role_list')
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Ajouter un rôle'})


@permission_required('role_modifier')
def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Rôle modifié avec succès.')
        return _redirect_with_standalone(request, 'role_list')
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Modifier le rôle'})


@permission_required('role_modifier')
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Rôle supprimé avec succès.')
        return _redirect_with_standalone(request, 'role_list')
    return render(request, 'core/role_confirm_delete.html', {'role': role})


# ============ UTILISATEUR CRUD ============

@permission_required('utilisateur_voir')
def utilisateur_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    utilisateur_direction = request.GET.get('direction')
    utilisateurs = UtilisateurProfile.objects.select_related('user', 'societe', 'agence', 'role')
    if selected_societe_id:
        utilisateurs = utilisateurs.filter(societe_id=selected_societe_id)
    else:
        utilisateurs = utilisateurs.none()
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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = UtilisateurProfileForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Utilisateur ajouté avec succès.')
        return _redirect_with_standalone(request, 'utilisateur_list')
    return render(request, 'core/utilisateur_form.html', {'form': form, 'title': 'Ajouter un utilisateur'})


@permission_required('utilisateur_modifier')
def utilisateur_update(request, pk):
    utilisateur = get_object_or_404(UtilisateurProfile, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or utilisateur.societe_id
    form = UtilisateurProfileForm(request.POST or None, instance=utilisateur)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Vider le cache permissions si le rôle a changé
        clear_permissions_cache(utilisateur.user_id)
        messages.success(request, 'Utilisateur modifié avec succès.')
        return _redirect_with_standalone(request, 'utilisateur_list')
    return render(request, 'core/utilisateur_form.html', {'form': form, 'title': 'Modifier l\'utilisateur'})


@permission_required('utilisateur_supprimer')
def utilisateur_delete(request, pk):
    utilisateur = get_object_or_404(UtilisateurProfile, pk=pk)
    if request.method == 'POST':
        clear_permissions_cache(utilisateur.user_id)
        utilisateur.delete()
        messages.success(request, 'Utilisateur supprimé avec succès.')
        return _redirect_with_standalone(request, 'utilisateur_list')
    return render(request, 'core/utilisateur_confirm_delete.html', {'utilisateur': utilisateur})


# ============ JOURNAL CRUD ============

@permission_required('journal_voir')
def journal_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    journaux = Journal.objects.select_related('societe').all()
    if selected_societe_id:
        journaux = journaux.filter(societe_id=selected_societe_id)
    else:
        journaux = journaux.none()
    return render(request, 'core/journal_list.html', {'journaux': journaux})


@permission_required('journal_voir')
def journal_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = JournalForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Journal ajouté avec succès.')
        return _redirect_with_standalone(request, 'journal_list')
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Ajouter un journal'})


@permission_required('journal_voir')
def journal_update(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or journal.societe_id
    form = JournalForm(request.POST or None, instance=journal)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Journal modifié avec succès.')
        return _redirect_with_standalone(request, 'journal_list')
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Modifier le journal'})


@permission_required('journal_voir')
def journal_delete(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    if request.method == 'POST':
        if journal.ecritures.exists():
            messages.error(request, "Suppression impossible: ce code journal contient déjà des enregistrements.")
            target_route = 'code_journaux_page' if request.GET.get('from_comptabilite') == '1' else 'journal_list'
            return _redirect_with_standalone(request, target_route)
        journal.delete()
        messages.success(request, 'Journal supprimé avec succès.')
        target_route = 'code_journaux_page' if request.GET.get('from_comptabilite') == '1' else 'journal_list'
        return _redirect_with_standalone(request, target_route)
    return render(request, 'core/journal_confirm_delete.html', {'journal': journal})


# ============ ECRITURE COMPTABLE CRUD ============

@permission_required('ecriture_voir')
def ecriture_list(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    ecritures = (
        EcritureComptable.objects
        .select_related('societe', 'agence', 'journal', 'utilisateur', 'client', 'fournisseur')
        .annotate(
            total_debit=Coalesce(
                Sum('lignes__debit'),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
            total_credit=Coalesce(
                Sum('lignes__credit'),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
            ),
        )
        .all()
    )
    if selected_societe_id:
        ecritures = ecritures.filter(societe_id=selected_societe_id)
    else:
        ecritures = ecritures.none()

    journaux = Journal.objects.none()
    if selected_societe_id:
        journaux = Journal.objects.filter(societe_id=selected_societe_id, actif=True).order_by('code')

    selected_journal = (request.GET.get('journal') or '').strip()
    date_debut = (request.GET.get('date_debut') or '').strip()
    date_fin = (request.GET.get('date_fin') or '').strip()
    etat = (request.GET.get('etat') or '').strip()
    selected_client = (request.GET.get('client') or '').strip()
    selected_fournisseur = (request.GET.get('fournisseur') or '').strip()
    selected_journal_obj = journaux.filter(pk=selected_journal).first() if selected_journal else None

    if selected_journal:
        ecritures = ecritures.filter(journal_id=selected_journal)
    if date_debut:
        ecritures = ecritures.filter(date_ecriture__gte=date_debut)
    if date_fin:
        ecritures = ecritures.filter(date_ecriture__lte=date_fin)
    if selected_client:
        ecritures = ecritures.filter(client_id=selected_client)
    if selected_fournisseur:
        ecritures = ecritures.filter(fournisseur_id=selected_fournisseur)
    if etat == 'equilibree':
        ecritures = ecritures.filter(total_debit=F('total_credit'))
    elif etat == 'desequilibree':
        ecritures = ecritures.exclude(total_debit=F('total_credit'))

    ecritures = ecritures.order_by('-date_ecriture', '-id')
    paginator = Paginator(ecritures, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    reset_params = {}
    for key in ['standalone', 'embed', 'from_comptabilite', 'societe']:
        value = request.GET.get(key)
        if value:
            reset_params[key] = value

    return render(
        request,
        'core/ecriture_list.html',
        {
            'ecritures': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.paginator.num_pages > 1,
            'journaux': journaux,
            'selected_journal': selected_journal,
            'selected_journal_obj': selected_journal_obj,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'etat': etat,
            'selected_client': selected_client,
            'selected_fournisseur': selected_fournisseur,
            'query_string': query_params.urlencode(),
            'reset_query_string': urlencode(reset_params),
        },
    )


@permission_required('ecriture_ajouter')
def ecriture_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    ecriture = EcritureComptable()
    form = EcritureComptableForm(request.POST or None, instance=ecriture)
    line_formset = LigneEcritureFormSet(request.POST or None, instance=ecriture, prefix='lignes')
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_ligne_ecriture_formset_for_societe(line_formset, selected_societe_id)

    # Journal prérempli automatiquement pour la saisie depuis le journal concerné.
    requested_journal = (request.GET.get('journal') or '').strip()
    comptabilisation_parametre = ComptabilisationParametre.objects.filter(societe_id=selected_societe_id).first() if selected_societe_id else None
    default_journal = None
    if requested_journal and form.fields['journal'].queryset.filter(pk=requested_journal).exists():
        default_journal = form.fields['journal'].queryset.filter(pk=requested_journal).first()
    elif selected_societe_id:
        parametre = comptabilisation_parametre
        if parametre and parametre.journal_defaut_id and form.fields['journal'].queryset.filter(pk=parametre.journal_defaut_id).exists():
            default_journal = parametre.journal_defaut
    if not default_journal:
        default_journal = form.fields['journal'].queryset.first()

    if default_journal and not form.is_bound:
        # Affectation explicite pour garantir la valeur du champ caché.
        form.initial['journal'] = default_journal.id
        form.fields['journal'].initial = default_journal.id
        racine_numero = _resolve_numero_racine(selected_societe_id, default_journal)
        form.initial['numero_ecriture'] = _next_numero_ecriture(selected_societe_id, default_journal.id, racine_numero)
    elif not form.is_bound:
        racine_numero = _resolve_numero_racine(selected_societe_id)
        form.initial['numero_ecriture'] = _next_numero_ecriture(selected_societe_id, racine=racine_numero)

    if 'journal' in form.fields:
        form.fields['journal'].widget = forms.HiddenInput()

    selected_journal_label = None
    selected_journal_id = form.data.get('journal') if form.is_bound else form.initial.get('journal')
    if not selected_journal_id and default_journal:
        selected_journal_id = default_journal.id
    if selected_journal_id:
        selected_journal = form.fields['journal'].queryset.filter(pk=selected_journal_id).first()
        if selected_journal:
            selected_journal_label = f"{selected_journal.code} - {selected_journal.nom}"

    journal_types = {str(j.id): j.type_journal for j in form.fields['journal'].queryset}
    suggested_client_compte_id = ''
    suggested_fournisseur_compte_id = ''
    if selected_societe_id:
        parametre = comptabilisation_parametre
        suggested_client_compte = parametre.compte_tiers_client if parametre else None
        suggested_fournisseur_compte = parametre.compte_tiers_fournisseur if parametre else None
        if not suggested_client_compte:
            suggested_client_compte = PlanComptable.objects.filter(
                societe_id=selected_societe_id,
                actif=True,
                numero_compte__startswith='411',
            ).order_by('numero_compte').first()
        if not suggested_fournisseur_compte:
            suggested_fournisseur_compte = PlanComptable.objects.filter(
                societe_id=selected_societe_id,
                actif=True,
                numero_compte__startswith='401',
            ).order_by('numero_compte').first()
        suggested_client_compte_id = str(suggested_client_compte.id) if suggested_client_compte else ''
        suggested_fournisseur_compte_id = str(suggested_fournisseur_compte.id) if suggested_fournisseur_compte else ''
    if 'agence' in form.fields:
        form.fields['agence'].widget = forms.HiddenInput()
        if not form.is_bound and hasattr(request.user, 'utilisateurprofile'):
            form.initial.setdefault('agence', request.user.utilisateurprofile.agence_id)
    if 'utilisateur' in form.fields:
        form.fields['utilisateur'].widget = forms.HiddenInput()
    if selected_societe_id and not form.is_bound:
        form.initial.setdefault('societe', selected_societe_id)
        form.initial['date_ecriture'] = timezone.localdate()
    if request.user.is_authenticated and hasattr(request.user, 'utilisateurprofile') and not form.is_bound:
        form.initial.setdefault('utilisateur', request.user.utilisateurprofile.pk)
    if request.method == 'POST' and form.is_valid() and line_formset.is_valid():
        with transaction.atomic():
            instance = form.save(commit=False)
            if not instance.societe_id and instance.journal_id:
                instance.societe_id = instance.journal.societe_id
            if not instance.numero_ecriture:
                racine = _resolve_numero_racine(instance.societe_id, instance.journal)
                instance.numero_ecriture = _next_numero_ecriture(instance.societe_id, instance.journal_id, racine)
            if hasattr(request.user, 'utilisateurprofile'):
                instance.utilisateur = request.user.utilisateurprofile
                if not instance.agence_id:
                    instance.agence_id = request.user.utilisateurprofile.agence_id
            instance.reference = instance.numero_ecriture
            instance.intitule = (instance.libelle_ecriture or '')[:200]
            instance.save()
            line_formset.instance = instance
            line_formset.save()
        messages.success(request, 'Écriture ajoutée avec succès.')
        return _redirect_with_standalone(request, 'ecriture_list')
    return render(
        request,
        'core/ecriture_form.html',
        {
            'form': form,
            'line_formset': line_formset,
            'title': 'Ajouter une écriture',
            'is_create': True,
            'selected_journal_label': selected_journal_label,
            'journal_types_json': json.dumps(journal_types),
            'suggested_client_compte_id': suggested_client_compte_id,
            'suggested_fournisseur_compte_id': suggested_fournisseur_compte_id,
        },
    )


@permission_required('ecriture_modifier')
def ecriture_update(request, pk):
    ecriture = get_object_or_404(EcritureComptable, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or ecriture.societe_id
    form = EcritureComptableForm(request.POST or None, instance=ecriture)
    line_formset = LigneEcritureFormSet(request.POST or None, instance=ecriture, prefix='lignes')
    _configure_form_for_societe(form, request.user, selected_societe_id)
    _configure_ligne_ecriture_formset_for_societe(line_formset, selected_societe_id)
    journal_types = {str(j.id): j.type_journal for j in form.fields['journal'].queryset}
    selected_journal_label = None
    selected_journal_id = form.data.get('journal') if form.is_bound else (form.initial.get('journal') or ecriture.journal_id)
    if selected_journal_id:
        selected_journal = form.fields['journal'].queryset.filter(pk=selected_journal_id).first()
        if selected_journal:
            selected_journal_label = f"{selected_journal.code} - {selected_journal.nom}"
    suggested_client_compte_id = ''
    suggested_fournisseur_compte_id = ''
    if selected_societe_id:
        parametre = ComptabilisationParametre.objects.filter(societe_id=selected_societe_id).first()
        suggested_client_compte = parametre.compte_tiers_client if parametre else None
        suggested_fournisseur_compte = parametre.compte_tiers_fournisseur if parametre else None
        if not suggested_client_compte:
            suggested_client_compte = PlanComptable.objects.filter(
                societe_id=selected_societe_id,
                actif=True,
                numero_compte__startswith='411',
            ).order_by('numero_compte').first()
        if not suggested_fournisseur_compte:
            suggested_fournisseur_compte = PlanComptable.objects.filter(
                societe_id=selected_societe_id,
                actif=True,
                numero_compte__startswith='401',
            ).order_by('numero_compte').first()
        suggested_client_compte_id = str(suggested_client_compte.id) if suggested_client_compte else ''
        suggested_fournisseur_compte_id = str(suggested_fournisseur_compte.id) if suggested_fournisseur_compte else ''
    if 'agence' in form.fields:
        form.fields['agence'].widget = forms.HiddenInput()
    if 'utilisateur' in form.fields:
        form.fields['utilisateur'].widget = forms.HiddenInput()
    if request.method == 'POST' and form.is_valid() and line_formset.is_valid():
        with transaction.atomic():
            instance = form.save(commit=False)
            if not instance.societe_id and instance.journal_id:
                instance.societe_id = instance.journal.societe_id
            if not instance.utilisateur_id and hasattr(request.user, 'utilisateurprofile'):
                instance.utilisateur = request.user.utilisateurprofile
            instance.reference = instance.numero_ecriture
            instance.intitule = (instance.libelle_ecriture or '')[:200]
            instance.save()
            line_formset.instance = instance
            line_formset.save()
        messages.success(request, 'Écriture modifiée avec succès.')
        return _redirect_with_standalone(request, 'ecriture_list')
    return render(
        request,
        'core/ecriture_form.html',
        {
            'form': form,
            'line_formset': line_formset,
            'title': 'Modifier l\'écriture',
            'is_create': False,
            'selected_journal_label': selected_journal_label,
            'journal_types_json': json.dumps(journal_types),
            'suggested_client_compte_id': suggested_client_compte_id,
            'suggested_fournisseur_compte_id': suggested_fournisseur_compte_id,
        },
    )


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
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    mouvements = MouvementStock.objects.select_related('produit', 'agence', 'agence_destination', 'utilisateur').all()
    if selected_societe_id:
        mouvements = mouvements.filter(produit__societe_id=selected_societe_id)
    else:
        mouvements = mouvements.none()
    return render(request, 'core/mouvement_list.html', {'mouvements': mouvements})


@permission_required('mouvement_ajouter')
def mouvement_create(request):
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes)
    form = MouvementStockForm(request.POST or None)
    _configure_form_for_societe(form, request.user, selected_societe_id)
    if request.method == 'POST' and form.is_valid():
        mouvement = form.save(commit=False)
        mouvement.utilisateur = request.user
        mouvement.save()

        stock_source, _ = Stock.objects.get_or_create(
            produit=mouvement.produit,
            agence=mouvement.agence,
            defaults={
                'quantite_disponible': 0,
                'quantite_reservee': 0,
                'valeur_stock': 0,
            },
        )

        if mouvement.type_mouvement == 'entree':
            stock_source.quantite_disponible += mouvement.quantite
        elif mouvement.type_mouvement == 'sortie':
            stock_source.quantite_disponible = max(0, stock_source.quantite_disponible - mouvement.quantite)
        elif mouvement.type_mouvement in ['ajustement', 'inventaire']:
            stock_source.quantite_disponible = max(0, mouvement.quantite)
        elif mouvement.type_mouvement == 'transfert' and mouvement.agence_destination:
            stock_source.quantite_disponible = max(0, stock_source.quantite_disponible - mouvement.quantite)
            stock_destination, _ = Stock.objects.get_or_create(
                produit=mouvement.produit,
                agence=mouvement.agence_destination,
                defaults={
                    'quantite_disponible': 0,
                    'quantite_reservee': 0,
                    'valeur_stock': 0,
                },
            )
            stock_destination.quantite_disponible += mouvement.quantite
            stock_destination.valeur_stock = stock_destination.quantite_disponible * (mouvement.prix_unitaire or mouvement.produit.prix_achat_ht or 0)
            stock_destination.date_dernier_mouvement = mouvement.date_mouvement
            stock_destination.save()

        stock_source.valeur_stock = stock_source.quantite_disponible * (mouvement.prix_unitaire or mouvement.produit.prix_achat_ht or 0)
        stock_source.date_dernier_mouvement = mouvement.date_mouvement
        stock_source.save()

        messages.success(request, 'Mouvement ajouté avec succès.')
        return _redirect_with_standalone(request, 'mouvement_list')
    return render(request, 'core/mouvement_form.html', {'form': form, 'title': 'Ajouter un mouvement'})


@permission_required('stock_voir')
def mouvement_update(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    societes = _get_accessible_societes(request.user)
    selected_societe_id = _get_selected_societe_id(request, societes) or mouvement.produit.societe_id
    form = MouvementStockForm(request.POST or None, instance=mouvement)
    _configure_form_for_societe(form, request.user, selected_societe_id)
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
        return _redirect_with_standalone(request, 'role_list')
    
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
