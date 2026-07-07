from decimal import Decimal

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from .models import Agence, Categorie, Projet, Fournisseur, Achat, LigneAchat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, MouvementStock, Societe, Produit, Client, Facture, LigneVente, Caisse, MouvementCaisse, Banque, MouvementBanque, PlanComptable, LigneEcriture, ComptabilisationParametre


def _compute_currency(value):
    return Decimal(value or 0).quantize(Decimal('0.01'))


class SocieteForm(forms.ModelForm):
    class Meta:
        model = Societe
        fields = ['code_societe', 'raison_sociale', 'forme_juridique', 'numero_registre', 'numero_fiscal', 'adresse', 'ville', 'code_postal', 'pays', 'telephone', 'email', 'site_web', 'logo', 'actif']
        widgets = {
            'code_societe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code unique (max 20 caractères)'}),
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raison sociale (obligatoire)'}),
            'forme_juridique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SARL, SA, etc.'}),
            'numero_registre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de registre du commerce'}),
            'numero_fiscal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro fiscal'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse complète'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code postal'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'adresse@email.com'}),
            'site_web': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),
            'logo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chemin du logo'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'societe', 'categorie', 'code_produit', 'code_barre', 'nom_produit', 'description',
            'type_produit', 'unite_mesure', 'prix_achat_ht', 'prix_vente_ht', 'taux_tva',
            'stock_min', 'stock_max', 'stock_alerte', 'image', 'actif'
        ]
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'code_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'code_barre': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_produit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'type_produit': forms.Select(attrs={'class': 'form-select'}),
            'unite_mesure': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_achat_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_alerte': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['societe', 'code_client', 'type_client', 'raison_sociale', 'nom', 'prenom', 'email', 'telephone', 'adresse', 'ville', 'code_postal', 'pays', 'numero_fiscal', 'condition_paiement', 'limite_credit', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code_client': forms.TextInput(attrs={'class': 'form-control'}),
            'type_client': forms.Select(attrs={'class': 'form-select'}),
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'condition_paiement': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FactureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['montant_ht', 'montant_tva', 'montant_ttc', 'remise', 'montant_restant']:
            self.fields[field_name].disabled = True

    class Meta:
        model = Facture
        fields = [
            'societe', 'agence', 'client', 'projet', 'numero_vente', 'type_vente', 'statut_vente',
            'montant_ht', 'montant_tva', 'montant_ttc', 'remise', 'montant_paye', 'montant_restant',
            'notes'
        ]
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'numero_vente': forms.TextInput(attrs={'class': 'form-control'}),
            'type_vente': forms.Select(attrs={'class': 'form-select'}),
            'statut_vente': forms.Select(attrs={'class': 'form-select'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remise': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_paye': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_restant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AgenceForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['societe', 'code', 'nom', 'type_agence', 'adresse', 'ville', 'code_postal', 'telephone', 'email', 'responsable', 'actif', 'date_ouverture']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_agence': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_ouverture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ProjetForm(forms.ModelForm):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    date_fin_prevue = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    date_fin_reelle = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)

    class Meta:
        model = Projet
        fields = [
            'societe', 'agence', 'reference_projet', 'libelle_projet', 'description', 'client',
            'type_projet', 'statut_projet', 'date_debut', 'date_fin_prevue', 'date_fin_reelle',
            'montant_ht', 'montant_tva', 'montant_ttc', 'budget_previsionnel', 'responsable', 'actif'
        ]
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'reference_projet': forms.TextInput(attrs={'class': 'form-control'}),
            'libelle_projet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'type_projet': forms.Select(attrs={'class': 'form-select'}),
            'statut_projet': forms.Select(attrs={'class': 'form-select'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'budget_previsionnel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['societe', 'code_fournisseur', 'raison_sociale', 'email', 'telephone', 'adresse', 'ville', 'code_postal', 'pays', 'numero_fiscal', 'condition_paiement', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code_fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'condition_paiement': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AchatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['montant_ht', 'montant_tva', 'montant_ttc', 'montant_restant']:
            self.fields[field_name].disabled = True

    class Meta:
        model = Achat
        fields = [
            'societe', 'agence', 'fournisseur', 'projet', 'numero_achat', 'type_achat', 'statut_achat',
            'montant_ht', 'montant_tva', 'montant_ttc', 'montant_paye', 'montant_restant',
            'notes'
        ]
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'numero_achat': forms.TextInput(attrs={'class': 'form-control'}),
            'type_achat': forms.Select(attrs={'class': 'form-select'}),
            'statut_achat': forms.Select(attrs={'class': 'form-select'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_paye': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_restant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BaseRequiredLineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        valid_rows = 0
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            cleaned = form.cleaned_data
            if not cleaned or cleaned.get('DELETE'):
                continue
            has_content = any(
                value not in (None, '', [])
                for key, value in cleaned.items()
                if key not in {'DELETE', 'id', 'vente', 'achat'}
            )
            if has_content:
                valid_rows += 1

        if valid_rows == 0:
            raise forms.ValidationError('Ajoutez au moins une ligne.')


class LigneVenteForm(forms.ModelForm):
    prix_unitaire_ht = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-price', 'step': '0.01'}))
    taux_tva = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-tax', 'step': '0.01'}))
    remise = forms.DecimalField(required=False, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-discount', 'step': '0.01'}))
    montant_ht = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-ht', 'step': '0.01', 'readonly': 'readonly'}))
    montant_tva = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-tax', 'step': '0.01', 'readonly': 'readonly'}))
    montant_ttc = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-ttc', 'step': '0.01', 'readonly': 'readonly'}))

    class Meta:
        model = LigneVente
        fields = ['produit', 'designation', 'quantite', 'prix_unitaire_ht', 'taux_tva', 'remise', 'montant_ht', 'montant_tva', 'montant_ttc']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select form-select-sm line-product'}),
            'designation': forms.TextInput(attrs={'class': 'form-control form-control-sm line-designation', 'placeholder': 'Désignation'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control form-control-sm line-qty', 'step': '1', 'min': '0'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned or cleaned.get('DELETE'):
            return cleaned

        produit = cleaned.get('produit')
        quantite = cleaned.get('quantite')
        prix = cleaned.get('prix_unitaire_ht')
        taux = cleaned.get('taux_tva')
        remise = cleaned.get('remise') or Decimal('0')

        if not any(value not in (None, '', []) for value in cleaned.values() if value is not False):
            return cleaned

        designation = (cleaned.get('designation') or '').strip()
        if not produit and not designation:
            self.add_error('designation', 'Saisissez une désignation ou choisissez un produit.')
            return cleaned
        if not quantite:
            self.add_error('quantite', 'Saisissez une quantité.')
            return cleaned

        prix = Decimal(prix if prix not in (None, '') else produit.prix_vente_ht or 0)
        taux = Decimal(taux if taux not in (None, '') else produit.taux_tva or 0)
        montant_ht = max((Decimal(quantite) * prix) - Decimal(remise), Decimal('0'))
        montant_tva = montant_ht * taux / Decimal('100')
        montant_ttc = montant_ht + montant_tva

        cleaned['prix_unitaire_ht'] = _compute_currency(prix)
        cleaned['taux_tva'] = _compute_currency(taux)
        cleaned['remise'] = _compute_currency(remise)
        cleaned['montant_ht'] = _compute_currency(montant_ht)
        cleaned['montant_tva'] = _compute_currency(montant_tva)
        cleaned['montant_ttc'] = _compute_currency(montant_ttc)
        if produit and not designation:
            cleaned['designation'] = produit.nom_produit
        return cleaned


class LigneAchatForm(forms.ModelForm):
    prix_unitaire_ht = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-price', 'step': '0.01'}))
    taux_tva = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-tax', 'step': '0.01'}))
    montant_ht = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-ht', 'step': '0.01', 'readonly': 'readonly'}))
    montant_tva = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-tax', 'step': '0.01', 'readonly': 'readonly'}))
    montant_ttc = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm line-total-ttc', 'step': '0.01', 'readonly': 'readonly'}))

    class Meta:
        model = LigneAchat
        fields = ['produit', 'designation', 'quantite', 'prix_unitaire_ht', 'taux_tva', 'montant_ht', 'montant_tva', 'montant_ttc', 'quantite_recue']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select form-select-sm line-product'}),
            'designation': forms.TextInput(attrs={'class': 'form-control form-control-sm line-designation', 'placeholder': 'Désignation'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control form-control-sm line-qty', 'step': '1', 'min': '0'}),
            'quantite_recue': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '1', 'min': '0'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned or cleaned.get('DELETE'):
            return cleaned

        produit = cleaned.get('produit')
        quantite = cleaned.get('quantite')
        prix = cleaned.get('prix_unitaire_ht')
        taux = cleaned.get('taux_tva')

        if not any(value not in (None, '', []) for value in cleaned.values() if value is not False):
            return cleaned

        designation = (cleaned.get('designation') or '').strip()
        if not produit and not designation:
            self.add_error('designation', 'Saisissez une désignation ou choisissez un produit.')
            return cleaned
        if not quantite:
            self.add_error('quantite', 'Saisissez une quantité.')
            return cleaned

        prix = Decimal(prix if prix not in (None, '') else produit.prix_achat_ht or 0)
        taux = Decimal(taux if taux not in (None, '') else produit.taux_tva or 0)
        montant_ht = Decimal(quantite) * prix
        montant_tva = montant_ht * taux / Decimal('100')
        montant_ttc = montant_ht + montant_tva

        cleaned['prix_unitaire_ht'] = _compute_currency(prix)
        cleaned['taux_tva'] = _compute_currency(taux)
        cleaned['montant_ht'] = _compute_currency(montant_ht)
        cleaned['montant_tva'] = _compute_currency(montant_tva)
        cleaned['montant_ttc'] = _compute_currency(montant_ttc)
        if produit and not designation:
            cleaned['designation'] = produit.nom_produit
        return cleaned


LigneVenteFormSet = inlineformset_factory(
    Facture,
    LigneVente,
    form=LigneVenteForm,
    formset=BaseRequiredLineFormSet,
    extra=1,
    can_delete=True,
)


LigneAchatFormSet = inlineformset_factory(
    Achat,
    LigneAchat,
    form=LigneAchatForm,
    formset=BaseRequiredLineFormSet,
    extra=1,
    can_delete=True,
)


class DepenseForm(forms.ModelForm):
    date_depense = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Depense
        fields = ['societe', 'agence', 'projet', 'reference', 'description', 'montant', 'date_depense', 'type_depense']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type_depense': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['societe', 'code_categorie', 'nom_categorie', 'categorie_parent', 'description', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code_categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie_parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nom', 'direction', 'description', 'niveau_acces', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'niveau_acces': forms.NumberInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AppPermissionForm(forms.ModelForm):
    class Meta:
        model = AppPermission
        fields = ['code_permission', 'nom_permission', 'module', 'description']
        widgets = {
            'code_permission': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_permission': forms.TextInput(attrs={'class': 'form-control'}),
            'module': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        fields = ['role', 'permission']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'permission': forms.Select(attrs={'class': 'form-select'}),
        }


class UtilisateurProfileForm(forms.ModelForm):
    # Champs venant de auth.User
    nom_utilisateur = forms.CharField(
        max_length=100, label='Nom utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mot_de_passe = forms.CharField(
        max_length=255, label='Mot de passe', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Laisser vide pour ne pas changer'})
    )

    class Meta:
        model = UtilisateurProfile
        fields = ['societe', 'agence', 'role', 'nom', 'prenom', 'email', 'telephone', 'photo', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['nom_utilisateur'].initial = self.instance.user.username

    def clean_nom_utilisateur(self):
        nom_utilisateur = self.cleaned_data.get('nom_utilisateur')
        from django.contrib.auth.models import User
        
        # Pour une modification, vérifier que le username n'est pas utilisé par un autre utilisateur
        if self.instance.pk and self.instance.user:
            # C'est une modification, vérifier que le username ne soit pas utilisé ailleurs
            existing_users = User.objects.filter(username=nom_utilisateur).exclude(id=self.instance.user_id)
            if existing_users.exists():
                raise forms.ValidationError(f"Le nom d'utilisateur '{nom_utilisateur}' est déjà utilisé.")
        else:
            # C'est une création, vérifier que le username n'existe pas
            if User.objects.filter(username=nom_utilisateur).exists():
                raise forms.ValidationError(f"Le nom d'utilisateur '{nom_utilisateur}' est déjà utilisé.")
        
        return nom_utilisateur

    def save(self, commit=True):
        profile = super().save(commit=False)
        nom_utilisateur = self.cleaned_data.get('nom_utilisateur')
        mot_de_passe = self.cleaned_data.get('mot_de_passe')
        from django.contrib.auth.models import User
        if profile.pk and hasattr(profile, 'user') and profile.user_id:
            user = profile.user
            user.username = nom_utilisateur
            if mot_de_passe:
                user.set_password(mot_de_passe)
        else:
            user = User(username=nom_utilisateur)
            if mot_de_passe:
                user.set_password(mot_de_passe)
            else:
                user.set_unusable_password()
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('prenom', '')
        user.last_name = self.cleaned_data.get('nom', '')
        if commit:
            user.save()
            profile.user = user
            profile.save()
        return profile


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['societe', 'code', 'nom', 'type_journal', 'racine_numero_ecriture', 'type_numerotation', 'compte_defaut', 'description', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_journal': forms.Select(attrs={'class': 'form-select'}),
            'racine_numero_ecriture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ACH'}),
            'type_numerotation': forms.Select(attrs={'class': 'form-select'}),
            'compte_defaut': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_racine_numero_ecriture(self):
        value = (self.cleaned_data.get('racine_numero_ecriture') or '').strip().upper()
        return value


class EcritureComptableForm(forms.ModelForm):
    date_ecriture = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['piece_comptable'].label = 'Référence'
        self.fields['piece_comptable'].required = True
        self.fields['numero_ecriture'].required = True
        self.fields['numero_ecriture'].label = 'Numéro écriture'
        self.fields['libelle_ecriture'].required = True
        self.fields['libelle_ecriture'].label = 'Libellé'
        self.fields['date_ecriture'].label = 'Date'
        if not self.is_bound and not self.instance.pk:
            self.initial.setdefault('date_ecriture', timezone.localdate())

    class Meta:
        model = EcritureComptable
        fields = [
            'societe', 'agence', 'journal', 'numero_ecriture', 'date_ecriture',
            'client', 'fournisseur', 'libelle_ecriture', 'piece_comptable', 'valide', 'utilisateur'
        ]
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'journal': forms.Select(attrs={'class': 'form-select'}),
            'numero_ecriture': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'libelle_ecriture': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'piece_comptable': forms.TextInput(attrs={'class': 'form-control'}),
            'valide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        journal = cleaned.get('journal')
        client = cleaned.get('client')
        fournisseur = cleaned.get('fournisseur')

        if journal:
            if journal.type_journal == 'Vente' and not client:
                self.add_error('client', 'Le client est obligatoire pour un journal de vente.')
            if journal.type_journal == 'Achat' and not fournisseur:
                self.add_error('fournisseur', 'Le fournisseur est obligatoire pour un journal d\'achat.')

            if journal.type_journal != 'Vente':
                cleaned['client'] = None
            if journal.type_journal != 'Achat':
                cleaned['fournisseur'] = None

        return cleaned


class PlanComptableForm(forms.ModelForm):
    class Meta:
        model = PlanComptable
        fields = ['societe', 'numero_compte', 'nom_compte', 'type_compte', 'classe', 'compte_parent', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'numero_compte': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_compte': forms.TextInput(attrs={'class': 'form-control'}),
            'type_compte': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.NumberInput(attrs={'class': 'form-control'}),
            'compte_parent': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComptabilisationParametreForm(forms.ModelForm):
    class Meta:
        model = ComptabilisationParametre
        fields = [
            'journal_defaut',
            'compte_tiers_client',
            'compte_tiers_fournisseur',
            'racine_numero_ecriture',
            'equilibre_obligatoire',
            'numerotation_auto',
            'type_numerotation',
            'verrouillage_periode',
            'champs_facultatifs_actifs',
            'modeles_recurrents_actifs',
            'mode_annulation',
            'motif_annulation_obligatoire',
            'roles_autorises_annulation',
        ]
        widgets = {
            'journal_defaut': forms.Select(attrs={'class': 'form-select'}),
            'compte_tiers_client': forms.Select(attrs={'class': 'form-select'}),
            'compte_tiers_fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'racine_numero_ecriture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ECR'}),
            'type_numerotation': forms.Select(attrs={'class': 'form-select'}),
            'mode_annulation': forms.Select(attrs={'class': 'form-select'}),
            'equilibre_obligatoire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numerotation_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verrouillage_periode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'champs_facultatifs_actifs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'modeles_recurrents_actifs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'motif_annulation_obligatoire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'roles_autorises_annulation': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        selected_societe_id = kwargs.pop('selected_societe_id', None)
        super().__init__(*args, **kwargs)
        self.selected_societe_id = selected_societe_id
        self.fields['roles_autorises_annulation'].queryset = Role.objects.filter(actif=True).order_by('direction', 'nom')
        if selected_societe_id:
            self.fields['journal_defaut'].queryset = Journal.objects.filter(societe_id=selected_societe_id, actif=True).order_by('code')
            comptes_queryset = PlanComptable.objects.filter(societe_id=selected_societe_id, actif=True).order_by('numero_compte')
            self.fields['compte_tiers_client'].queryset = comptes_queryset
            self.fields['compte_tiers_fournisseur'].queryset = comptes_queryset
        else:
            self.fields['journal_defaut'].queryset = Journal.objects.none()
            self.fields['compte_tiers_client'].queryset = PlanComptable.objects.none()
            self.fields['compte_tiers_fournisseur'].queryset = PlanComptable.objects.none()

    def clean_journal_defaut(self):
        journal = self.cleaned_data.get('journal_defaut')
        if not journal:
            return journal

        societe_id = self.instance.societe_id or self.selected_societe_id

        if societe_id and journal.societe_id != societe_id:
            raise forms.ValidationError('Le journal par défaut doit appartenir à la société sélectionnée.')
        return journal

    def _clean_compte_by_field(self, field_name, label):
        compte = self.cleaned_data.get(field_name)
        if not compte:
            return compte
        societe_id = self.instance.societe_id or self.selected_societe_id
        if societe_id and compte.societe_id != societe_id:
            raise forms.ValidationError(f'{label} doit appartenir à la société sélectionnée.')
        return compte

    def clean_compte_tiers_client(self):
        return self._clean_compte_by_field('compte_tiers_client', 'Le compte tiers client')

    def clean_compte_tiers_fournisseur(self):
        return self._clean_compte_by_field('compte_tiers_fournisseur', 'Le compte tiers fournisseur')

    def clean_racine_numero_ecriture(self):
        value = (self.cleaned_data.get('racine_numero_ecriture') or '').strip().upper()
        if not value:
            return 'ECR'
        return value


class LigneEcritureForm(forms.ModelForm):
    class Meta:
        model = LigneEcriture
        fields = ['ecriture', 'compte', 'debit', 'credit']
        widgets = {
            'ecriture': forms.Select(attrs={'class': 'form-select'}),
            'compte': forms.Select(attrs={'class': 'form-select'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

    def clean_debit(self):
        debit = self.cleaned_data.get('debit')
        return debit if debit is not None else Decimal('0')

    def clean_credit(self):
        credit = self.cleaned_data.get('credit')
        return credit if credit is not None else Decimal('0')


class LigneEcritureInlineForm(forms.ModelForm):
    debit = forms.DecimalField(required=False, decimal_places=0, max_digits=14, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '1', 'min': '0'}))
    credit = forms.DecimalField(required=False, decimal_places=0, max_digits=14, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '1', 'min': '0'}))
    
    class Meta:
        model = LigneEcriture
        fields = ['compte', 'debit', 'credit']
        widgets = {
            'compte': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

    def clean_debit(self):
        debit = self.cleaned_data.get('debit')
        return debit if debit is not None else Decimal('0')

    def clean_credit(self):
        credit = self.cleaned_data.get('credit')
        return credit if credit is not None else Decimal('0')

    def clean(self):
        cleaned = super().clean()
        if not cleaned or cleaned.get('DELETE'):
            return cleaned

        compte = cleaned.get('compte')
        debit = Decimal(cleaned.get('debit') or 0)
        credit = Decimal(cleaned.get('credit') or 0)

        has_any_value = bool(compte or debit or credit)
        if not has_any_value:
            return cleaned

        if not compte:
            self.add_error('compte', 'Le compte est obligatoire.')

        # Une ligne d'écriture doit avoir soit débit soit crédit (un seul, pas les deux)
        if debit == 0 and credit == 0:
            raise forms.ValidationError('Vous devez saisir un montant en débit ou en crédit.')

        if debit > 0 and credit > 0:
            raise forms.ValidationError('Une ligne d\'écriture ne peut pas avoir à la fois un débit et un crédit.')

        return cleaned


class BaseLigneEcritureFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        valid_rows = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            cleaned = form.cleaned_data
            if not cleaned or cleaned.get('DELETE'):
                continue

            compte = cleaned.get('compte')
            debit = Decimal(cleaned.get('debit') or 0)
            credit = Decimal(cleaned.get('credit') or 0)

            # Défense supplémentaire: éviter toute propagation de valeur NULL à la sauvegarde.
            cleaned['debit'] = debit
            cleaned['credit'] = credit

            if not (compte or debit or credit):
                continue

            valid_rows += 1
            total_debit += debit
            total_credit += credit

        if valid_rows < 2:
            raise forms.ValidationError('Ajoutez au moins deux lignes d\'écriture.')

        if total_debit != total_credit:
            raise forms.ValidationError('Écriture non équilibrée: le total débit doit être égal au total crédit.')


LigneEcritureFormSet = inlineformset_factory(
    EcritureComptable,
    LigneEcriture,
    form=LigneEcritureInlineForm,
    formset=BaseLigneEcritureFormSet,
    extra=3,
    can_delete=True,
)


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'agence', 'type_mouvement', 'quantite', 'prix_unitaire', 'agence_destination', 'reference', 'motif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'agence_destination': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CaisseForm(forms.ModelForm):
    class Meta:
        model = Caisse
        fields = ['agence', 'code_caisse', 'nom_caisse', 'solde_initial', 'solde_actuel', 'responsable', 'actif']
        widgets = {
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'code_caisse': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_caisse': forms.TextInput(attrs={'class': 'form-control'}),
            'solde_initial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'solde_actuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MouvementCaisseForm(forms.ModelForm):
    class Meta:
        model = MouvementCaisse
        fields = ['caisse', 'type_mouvement', 'montant', 'motif', 'reference', 'utilisateur']
        widgets = {
            'caisse': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
        }


class BanqueForm(forms.ModelForm):
    class Meta:
        model = Banque
        fields = ['agence', 'code_banque', 'nom_banque', 'solde_initial', 'solde_actuel', 'responsable', 'actif']
        widgets = {
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'code_banque': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_banque': forms.TextInput(attrs={'class': 'form-control'}),
            'solde_initial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'solde_actuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MouvementBanqueForm(forms.ModelForm):
    class Meta:
        model = MouvementBanque
        fields = ['banque', 'type_mouvement', 'montant', 'motif', 'reference', 'utilisateur']
        widgets = {
            'banque': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'utilisateur': forms.Select(attrs={'class': 'form-select'}),
        }
