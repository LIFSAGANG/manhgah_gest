from django import forms
from .models import Agence, Categorie, Projet, Fournisseur, Achat, Depense, Role, AppPermission, RolePermission, UtilisateurProfile, Journal, EcritureComptable, MouvementStock, Societe, Produit, Client, Facture


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
        fields = ['societe', 'reference', 'nom', 'categorie', 'prix_unitaire', 'date_creation', 'quantite_stock', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_creation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control'}),
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
    date_emission = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Facture
        fields = ['reference', 'client', 'date_emission', 'montant_total', 'statut', 'notes']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
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
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)

    class Meta:
        model = Projet
        fields = ['societe', 'agence', 'code', 'nom', 'description', 'date_debut', 'date_fin', 'budget', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
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
    date_commande = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Achat
        fields = ['fournisseur', 'reference', 'date_commande', 'montant_total', 'statut', 'projet', 'agence', 'notes']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


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
        fields = ['societe', 'code', 'nom', 'date_creation', 'description', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_creation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
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
        fields = ['societe', 'code', 'nom', 'description', 'actif']
        widgets = {
            'societe': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EcritureComptableForm(forms.ModelForm):
    date_ecriture = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = EcritureComptable
        fields = ['journal', 'date_ecriture', 'reference', 'intitule', 'compte', 'debit', 'credit', 'projet']
        widgets = {
            'journal': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'intitule': forms.TextInput(attrs={'class': 'form-control'}),
            'compte': forms.TextInput(attrs={'class': 'form-control'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
        }


class MouvementStockForm(forms.ModelForm):
    date_mouvement = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = MouvementStock
        fields = ['produit', 'agence', 'quantite', 'type_mouvement', 'date_mouvement', 'remarque']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
