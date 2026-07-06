from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.utils import timezone


def _currency(value):
    return Decimal(value or 0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Societe(models.Model):
    code_societe = models.CharField(max_length=20, unique=True, verbose_name='Code Société', db_index=True)
    raison_sociale = models.CharField(max_length=200, verbose_name='Raison Sociale')
    forme_juridique = models.CharField(max_length=50, blank=True, null=True, verbose_name='Forme Juridique')
    numero_registre = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numéro Registre')
    numero_fiscal = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numéro Fiscal')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    code_postal = models.CharField(max_length=20, blank=True, null=True, verbose_name='Code Postal')
    pays = models.CharField(max_length=100, default='Burkina Faso', verbose_name='Pays')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    site_web = models.CharField(max_length=200, blank=True, null=True, verbose_name='Site Web')
    logo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Logo')
    actif = models.BooleanField(default=True, verbose_name='Actif', db_index=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')

    class Meta:
        verbose_name = 'Société'
        verbose_name_plural = 'Sociétés'
        ordering = ['raison_sociale']
        indexes = [
            models.Index(fields=['code_societe']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        return self.raison_sociale


class Produit(models.Model):
    TYPE_PRODUIT_CHOICES = [
        ('Bien', 'Bien'),
        ('Service', 'Service'),
        ('Consommable', 'Consommable'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société', db_index=True)
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Catégorie', db_index=True)
    code_produit = models.CharField(max_length=50, unique=True, verbose_name='Code produit')
    code_barre = models.CharField(max_length=100, blank=True, null=True, verbose_name='Code barre')
    nom_produit = models.CharField(max_length=200, verbose_name='Nom produit')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    type_produit = models.CharField(max_length=20, choices=TYPE_PRODUIT_CHOICES, default='Bien', verbose_name='Type produit')
    unite_mesure = models.CharField(max_length=20, default='Unité', verbose_name='Unité de mesure')
    prix_achat_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Prix achat HT')
    prix_vente_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Prix vente HT')
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Taux TVA')
    stock_min = models.PositiveIntegerField(default=0, verbose_name='Stock minimum')
    stock_max = models.PositiveIntegerField(default=0, verbose_name='Stock maximum')
    stock_alerte = models.PositiveIntegerField(default=0, verbose_name='Stock alerte')
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name='Image')
    actif = models.BooleanField(default=True, verbose_name='Actif', db_index=True)
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['nom_produit']
        indexes = [
            models.Index(fields=['societe']),
            models.Index(fields=['categorie']),
            models.Index(fields=['actif']),
            models.Index(fields=['nom_produit']),
        ]

    def __str__(self):
        return f"{self.nom_produit} ({self.code_produit})"

    # Compatibilité rétroactive avec les anciens templates/champs.
    @property
    def reference(self):
        return self.code_produit

    @reference.setter
    def reference(self, value):
        self.code_produit = value

    @property
    def nom(self):
        return self.nom_produit

    @nom.setter
    def nom(self, value):
        self.nom_produit = value

    @property
    def prix_unitaire(self):
        return self.prix_vente_ht

    @prix_unitaire.setter
    def prix_unitaire(self, value):
        self.prix_vente_ht = value

    @property
    def quantite_stock(self):
        aggregate = self.stocks.aggregate(total=models.Sum('quantite_disponible'))
        return aggregate.get('total') or 0


class Client(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='clients', verbose_name='Société', null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, verbose_name='Code client', blank=True)
    code_client = models.CharField(max_length=50, unique=True, verbose_name='Code client', blank=True, null=True)
    type_client = models.CharField(
        max_length=20,
        choices=[('Particulier', 'Particulier'), ('Entreprise', 'Entreprise')],
        default='Particulier',
        verbose_name='Type client',
    )
    raison_sociale = models.CharField(max_length=200, blank=True, null=True, verbose_name='Raison sociale')
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nom')
    prenom = models.CharField(max_length=100, blank=True, null=True, verbose_name='Prénom')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    code_postal = models.CharField(max_length=20, blank=True, null=True, verbose_name='Code postal')
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name='Pays')
    numero_fiscal = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numéro fiscal')
    condition_paiement = models.CharField(max_length=50, blank=True, null=True, verbose_name='Condition de paiement')
    limite_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Limite de crédit')
    actif = models.BooleanField(default=True, verbose_name='Actif', db_index=True)
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['raison_sociale', 'nom', 'prenom']
        indexes = [
            models.Index(fields=['societe', 'actif']),
            models.Index(fields=['code_client']),
            models.Index(fields=['raison_sociale']),
        ]

    def save(self, *args, **kwargs):
        if self.code_client and not self.code:
            self.code = self.code_client
        elif self.code and not self.code_client:
            self.code_client = self.code
        if self.raison_sociale and not self.nom:
            self.nom = self.raison_sociale
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.raison_sociale or self.nom or self.prenom or 'Client'} ({self.code_client or self.code})"


class Facture(models.Model):
    TYPE_VENTE_CHOICES = [
        ('Produit', 'Produit'),
        ('Service', 'Service'),
        ('Travaux', 'Travaux'),
    ]
    STATUT_VENTE_CHOICES = [
        ('Brouillon', 'Brouillon'),
        ('Validee', 'Validee'),
        ('Annulee', 'Annulee'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='ventes', verbose_name='Société', db_index=True, null=True)
    agence = models.ForeignKey('Agence', on_delete=models.CASCADE, related_name='ventes', verbose_name='Agence', db_index=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='ventes', verbose_name='Client', blank=True, null=True, db_index=True)
    projet = models.ForeignKey('Projet', on_delete=models.SET_NULL, related_name='ventes', verbose_name='Projet', blank=True, null=True)
    numero_vente = models.CharField(max_length=50, unique=True, verbose_name='Numéro vente', null=True)
    date_vente = models.DateTimeField(default=timezone.now, verbose_name='Date vente', db_index=True)
    type_vente = models.CharField(max_length=20, choices=TYPE_VENTE_CHOICES, default='Produit', verbose_name='Type vente')
    statut_vente = models.CharField(max_length=20, choices=STATUT_VENTE_CHOICES, default='Brouillon', verbose_name='Statut vente', db_index=True)
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TTC')
    remise = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Remise')
    montant_paye = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant payé')
    montant_restant = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant restant')
    utilisateur = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='ventes', verbose_name='Utilisateur', null=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')

    class Meta:
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        ordering = ['-date_vente', 'numero_vente']
        indexes = [
            models.Index(fields=['agence', 'date_vente']),
            models.Index(fields=['statut_vente', 'date_vente']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f"{self.numero_vente}"

    def recalculer_totaux(self, save=True):
        totaux = self.lignes_vente.aggregate(
            total_ht=models.Sum('montant_ht'),
            total_tva=models.Sum('montant_tva'),
            total_ttc=models.Sum('montant_ttc'),
            total_remise=models.Sum('remise'),
        )
        self.montant_ht = _currency(totaux.get('total_ht'))
        self.montant_tva = _currency(totaux.get('total_tva'))
        self.montant_ttc = _currency(totaux.get('total_ttc'))
        self.remise = _currency(totaux.get('total_remise'))
        self.montant_restant = _currency(max(self.montant_ttc - Decimal(self.montant_paye or 0), Decimal('0')))
        if save and self.pk:
            self.save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc', 'remise', 'montant_restant', 'date_modification'])

    # Compatibilité avec les anciens noms de champs/templates.
    @property
    def reference(self):
        return self.numero_vente

    @reference.setter
    def reference(self, value):
        self.numero_vente = value

    @property
    def date_emission(self):
        return self.date_vente

    @date_emission.setter
    def date_emission(self, value):
        self.date_vente = value

    @property
    def montant_total(self):
        return self.montant_ttc

    @montant_total.setter
    def montant_total(self, value):
        self.montant_ttc = value

    @property
    def statut(self):
        return self.statut_vente

    @statut.setter
    def statut(self, value):
        self.statut_vente = value


class LigneVente(models.Model):
    vente = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes_vente', verbose_name='Vente')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_vente', verbose_name='Produit', blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True, verbose_name='Désignation')
    quantite = models.IntegerField(verbose_name='Quantité')
    prix_unitaire_ht = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Prix unitaire HT')
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Taux TVA')
    remise = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Remise')
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant TTC')

    class Meta:
        verbose_name = 'Ligne vente'
        verbose_name_plural = 'Lignes vente'
        indexes = [
            models.Index(fields=['vente']),
        ]

    def save(self, *args, **kwargs):
        if self.produit_id:
            if not self.prix_unitaire_ht:
                self.prix_unitaire_ht = self.produit.prix_vente_ht
            if self.taux_tva is None:
                self.taux_tva = self.produit.taux_tva
            if not self.designation:
                self.designation = self.produit.nom_produit

        quantite = Decimal(self.quantite or 0)
        prix_unitaire = Decimal(self.prix_unitaire_ht or 0)
        remise = Decimal(self.remise or 0)
        taux_tva = Decimal(self.taux_tva or 0)
        montant_ht = max((quantite * prix_unitaire) - remise, Decimal('0'))
        self.montant_ht = _currency(montant_ht)
        self.montant_tva = _currency(montant_ht * taux_tva / Decimal('100'))
        self.montant_ttc = _currency(self.montant_ht + self.montant_tva)
        super().save(*args, **kwargs)

    def __str__(self):
        line_name = self.designation or (self.produit.nom_produit if self.produit_id else 'Sans désignation')
        return f"{self.vente.numero_vente} - {line_name}"


class Agence(models.Model):
    AGENCE_TYPES = [
        ('Siege', 'Siège'),
        ('Succursale', 'Succursale'),
        ('Depot', 'Dépôt'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code agence')
    nom = models.CharField(max_length=150, verbose_name='Nom agence')
    type_agence = models.CharField(max_length=20, choices=AGENCE_TYPES, default='Succursale', verbose_name='Type d’agence')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    code_postal = models.CharField(max_length=20, blank=True, null=True, verbose_name='Code postal')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    responsable = models.CharField(max_length=200, blank=True, null=True, verbose_name='Responsable')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_ouverture = models.DateField(blank=True, null=True, verbose_name='Date d’ouverture')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Agence'
        verbose_name_plural = 'Agences'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code})"


class Role(models.Model):
    DIRECTION_CHOICES = [
        ('Direction Commerciale', 'Direction Commerciale'),
        ('Direction des Achats', 'Direction des Achats'),
        ('Direction des Ressources Humaines', 'Direction des Ressources Humaines'),
        ('Direction de la Production', 'Direction de la Production'),
        ('Direction Logistique & Stock', 'Direction Logistique & Stock'),
        ('Direction Informatique', 'Direction Informatique'),
        ('Direction Juridique', 'Direction Juridique'),
        ('Direction des Projets', 'Direction des Projets'),
    ]

    nom = models.CharField(max_length=50, unique=True, verbose_name='Nom du rôle')
    direction = models.CharField(max_length=50, choices=DIRECTION_CHOICES, blank=True, null=True, verbose_name='Direction')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    niveau_acces = models.IntegerField(default=1, verbose_name='Niveau d’accès')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Rôle'
        verbose_name_plural = 'Rôles'
        ordering = ['direction', 'niveau_acces', 'nom']

    def __str__(self):
        return self.nom


class AppPermission(models.Model):
    nom_permission = models.CharField(max_length=100, unique=True, verbose_name='Nom de la permission')
    code_permission = models.CharField(max_length=50, unique=True, verbose_name='Code permission')
    module = models.CharField(max_length=50, verbose_name='Module', db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['module', 'nom_permission']

    def __str__(self):
        return self.nom_permission


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Rôle')
    permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE, verbose_name='Permission')

    class Meta:
        verbose_name = 'Permission de rôle'
        verbose_name_plural = 'Permissions de rôle'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role} → {self.permission}"


class UtilisateurProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, verbose_name='Compte auth')
    societe = models.ForeignKey(Societe, on_delete=models.PROTECT, verbose_name='Société')
    agence = models.ForeignKey(Agence, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Agence')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name='Rôle')
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    email = models.EmailField(max_length=100, unique=True, verbose_name='Email')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    photo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Photo')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    derniere_connexion = models.DateTimeField(blank=True, null=True, verbose_name='Dernière Connexion')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['societe', 'agence', 'actif']),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.user.username})"

    @property
    def nom_utilisateur(self):
        return self.user.username


class Projet(models.Model):
    TYPE_PROJET_CHOICES = [
        ('Interne', 'Interne'),
        ('Externe', 'Externe'),
        ('Vente', 'Vente'),
        ('Service', 'Service'),
    ]

    STATUT_PROJET_CHOICES = [
        ('EnCours', 'EnCours'),
        ('Termine', 'Termine'),
        ('Suspendu', 'Suspendu'),
        ('Annule', 'Annule'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Agence')
    reference_projet = models.CharField(max_length=50, unique=True, verbose_name='ReferenceProjet')
    libelle_projet = models.CharField(max_length=200, verbose_name='LibelleProjet')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Client')
    type_projet = models.CharField(max_length=20, choices=TYPE_PROJET_CHOICES, default='Externe', verbose_name='Type projet')
    statut_projet = models.CharField(max_length=20, choices=STATUT_PROJET_CHOICES, default='EnCours', verbose_name='Statut projet')
    date_debut = models.DateField(verbose_name='Date de début')
    date_fin_prevue = models.DateField(blank=True, null=True, verbose_name='Date de fin prévue')
    date_fin_reelle = models.DateField(blank=True, null=True, verbose_name='Date de fin réelle')
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TTC')
    budget_previsionnel = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Budget prévisionnel')
    responsable = models.ForeignKey('UtilisateurProfile', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Responsable')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['libelle_projet']
        indexes = [
            models.Index(fields=['societe']),
            models.Index(fields=['client']),
            models.Index(fields=['statut_projet']),
        ]

    def __str__(self):
        return f"{self.libelle_projet} ({self.reference_projet})"

    # Compatibilité rétroactive avec les templates/listes existants.
    @property
    def code(self):
        return self.reference_projet

    @code.setter
    def code(self, value):
        self.reference_projet = value

    @property
    def nom(self):
        return self.libelle_projet

    @nom.setter
    def nom(self, value):
        self.libelle_projet = value

    @property
    def budget(self):
        return self.budget_previsionnel

    @budget.setter
    def budget(self, value):
        self.budget_previsionnel = value

    @property
    def date_fin(self):
        return self.date_fin_prevue

    @date_fin.setter
    def date_fin(self, value):
        self.date_fin_prevue = value


class Categorie(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société', db_index=True)
    code_categorie = models.CharField(max_length=20, unique=True, verbose_name='Code catégorie')
    nom_categorie = models.CharField(max_length=100, verbose_name='Nom catégorie')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    categorie_parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Catégorie parente', related_name='enfants')
    actif = models.BooleanField(default=True, verbose_name='Actif', db_index=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom_categorie']
        indexes = [
            models.Index(fields=['societe']),
        ]

    def __str__(self):
        return self.nom_categorie

    # Compatibilité rétroactive.
    @property
    def code(self):
        return self.code_categorie

    @code.setter
    def code(self, value):
        self.code_categorie = value

    @property
    def nom(self):
        return self.nom_categorie

    @nom.setter
    def nom(self, value):
        self.nom_categorie = value

    @property
    def parent(self):
        return self.categorie_parent

    @parent.setter
    def parent(self, value):
        self.categorie_parent = value


class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks', verbose_name='Produit')
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='stocks', verbose_name='Agence')
    quantite_disponible = models.IntegerField(default=0, verbose_name='Quantité disponible')
    quantite_reservee = models.IntegerField(default=0, verbose_name='Quantité réservée')
    valeur_stock = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Valeur stock')
    date_dernier_mouvement = models.DateTimeField(blank=True, null=True, verbose_name='Date dernier mouvement')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ('produit', 'agence')
        indexes = [
            models.Index(fields=['agence']),
        ]

    def __str__(self):
        return f"{self.produit} - {self.agence}"


class Fournisseur(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='fournisseurs', verbose_name='Société', null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, verbose_name='Code fournisseur', blank=True)
    code_fournisseur = models.CharField(max_length=50, unique=True, verbose_name='Code fournisseur', blank=True, null=True)
    raison_sociale = models.CharField(max_length=200, verbose_name='Raison sociale')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    code_postal = models.CharField(max_length=20, blank=True, null=True, verbose_name='Code postal')
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name='Pays')
    numero_fiscal = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numéro fiscal')
    condition_paiement = models.CharField(max_length=50, blank=True, null=True, verbose_name='Condition de paiement')
    actif = models.BooleanField(default=True, verbose_name='Actif', db_index=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['raison_sociale']
        indexes = [
            models.Index(fields=['societe', 'actif']),
            models.Index(fields=['code_fournisseur']),
            models.Index(fields=['raison_sociale']),
        ]

    def save(self, *args, **kwargs):
        if self.code_fournisseur and not self.code:
            self.code = self.code_fournisseur
        elif self.code and not self.code_fournisseur:
            self.code_fournisseur = self.code
        super().save(*args, **kwargs)

    @property
    def nom(self):
        return self.raison_sociale

    def __str__(self):
        return f"{self.raison_sociale} ({self.code_fournisseur or self.code})"


class Achat(models.Model):
    TYPE_ACHAT_CHOICES = [
        ('Produit', 'Produit'),
        ('Service', 'Service'),
        ('Travaux', 'Travaux'),
    ]

    STATUT_ACHAT_CHOICES = [
        ('Brouillon', 'Brouillon'),
        ('Validee', 'Validee'),
        ('Receptionnee', 'Receptionnee'),
        ('Annulee', 'Annulee'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='achats', verbose_name='Société', db_index=True, null=True)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='achats', verbose_name='Agence', db_index=True, null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='achats', verbose_name='Fournisseur', db_index=True)
    projet = models.ForeignKey('Projet', on_delete=models.SET_NULL, related_name='achats', verbose_name='Projet', blank=True, null=True)
    numero_achat = models.CharField(max_length=50, unique=True, verbose_name='Numéro achat', null=True)
    date_achat = models.DateTimeField(default=timezone.now, verbose_name='Date achat', db_index=True)
    type_achat = models.CharField(max_length=20, choices=TYPE_ACHAT_CHOICES, default='Produit', verbose_name='Type achat')
    statut_achat = models.CharField(max_length=20, choices=STATUT_ACHAT_CHOICES, default='Brouillon', verbose_name='Statut achat')
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TTC')
    montant_paye = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant payé')
    montant_restant = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant restant')
    utilisateur = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='achats', verbose_name='Utilisateur', null=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')

    class Meta:
        verbose_name = 'Achat'
        verbose_name_plural = 'Achats'
        ordering = ['-date_achat', 'numero_achat']
        indexes = [
            models.Index(fields=['agence', 'date_achat']),
            models.Index(fields=['fournisseur']),
        ]

    def __str__(self):
        return f"{self.numero_achat} - {self.fournisseur.nom}"

    def recalculer_totaux(self, save=True):
        totaux = self.lignes_achat.aggregate(
            total_ht=models.Sum('montant_ht'),
            total_tva=models.Sum('montant_tva'),
            total_ttc=models.Sum('montant_ttc'),
        )
        self.montant_ht = _currency(totaux.get('total_ht'))
        self.montant_tva = _currency(totaux.get('total_tva'))
        self.montant_ttc = _currency(totaux.get('total_ttc'))
        self.montant_restant = _currency(max(self.montant_ttc - Decimal(self.montant_paye or 0), Decimal('0')))
        if save and self.pk:
            self.save(update_fields=['montant_ht', 'montant_tva', 'montant_ttc', 'montant_restant', 'date_modification'])

    # Compatibilité avec les anciens noms de champs/templates.
    @property
    def reference(self):
        return self.numero_achat

    @reference.setter
    def reference(self, value):
        self.numero_achat = value

    @property
    def date_commande(self):
        return self.date_achat

    @date_commande.setter
    def date_commande(self, value):
        self.date_achat = value

    @property
    def montant_total(self):
        return self.montant_ttc

    @montant_total.setter
    def montant_total(self, value):
        self.montant_ttc = value

    @property
    def statut(self):
        return self.statut_achat

    @statut.setter
    def statut(self, value):
        self.statut_achat = value


class LigneAchat(models.Model):
    achat = models.ForeignKey(Achat, on_delete=models.CASCADE, related_name='lignes_achat', verbose_name='Achat')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_achat', verbose_name='Produit', blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True, verbose_name='Désignation')
    quantite = models.IntegerField(verbose_name='Quantité')
    prix_unitaire_ht = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Prix unitaire HT')
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Taux TVA')
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant TTC')
    quantite_recue = models.IntegerField(default=0, verbose_name='Quantité reçue')

    class Meta:
        verbose_name = 'Ligne achat'
        verbose_name_plural = 'Lignes achat'
        indexes = [
            models.Index(fields=['achat']),
        ]

    def save(self, *args, **kwargs):
        if self.produit_id:
            if not self.prix_unitaire_ht:
                self.prix_unitaire_ht = self.produit.prix_achat_ht
            if self.taux_tva is None:
                self.taux_tva = self.produit.taux_tva
            if not self.designation:
                self.designation = self.produit.nom_produit

        quantite = Decimal(self.quantite or 0)
        prix_unitaire = Decimal(self.prix_unitaire_ht or 0)
        taux_tva = Decimal(self.taux_tva or 0)
        montant_ht = quantite * prix_unitaire
        self.montant_ht = _currency(montant_ht)
        self.montant_tva = _currency(montant_ht * taux_tva / Decimal('100'))
        self.montant_ttc = _currency(self.montant_ht + self.montant_tva)
        super().save(*args, **kwargs)

    def __str__(self):
        line_name = self.designation or (self.produit.nom_produit if self.produit_id else 'Sans désignation')
        return f"{self.achat.numero_achat} - {line_name}"


class Depense(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    agence = models.ForeignKey(Agence, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Agence')
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Projet')
    reference = models.CharField(max_length=100, unique=True, verbose_name='Référence dépense')
    description = models.TextField(verbose_name='Description')
    montant = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant')
    date_depense = models.DateField(verbose_name='Date de dépense')
    type_depense = models.CharField(max_length=100, blank=True, null=True, verbose_name='Type de dépense')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date_depense', 'reference']

    def __str__(self):
        return f"{self.reference} - {self.montant}"


class PlanComptable(models.Model):
    TYPE_COMPTE_CHOICES = [
        ('Actif', 'Actif'),
        ('Passif', 'Passif'),
        ('Charge', 'Charge'),
        ('Produit', 'Produit'),
        ('Resultat', 'Resultat'),
        ('Actifs circulants', 'Actifs circulants'),
        ('Actifs immobilisés', 'Actifs immobilisés'),
        ('Autres produits', 'Autres produits'),
        ('Banque et espèces', 'Banque et espèces'),
        ('Bénéfices de l\'exercice en cours', 'Bénéfices de l\'exercice en cours'),
        ('Capitaux propres', 'Capitaux propres'),
        ('Charges', 'Charges'),
        ('Client', 'Client'),
        ('Dettes à court terme', 'Dettes à court terme'),
        ('Fournisseur', 'Fournisseur'),
        ('Hors bilan', 'Hors bilan'),
        ('Revenus', 'Revenus'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='comptes_comptables', verbose_name='Société')
    numero_compte = models.CharField(max_length=20, verbose_name='Numéro compte')
    nom_compte = models.CharField(max_length=200, verbose_name='Nom compte')
    type_compte = models.CharField(max_length=50, choices=TYPE_COMPTE_CHOICES, verbose_name='Type compte')
    classe = models.IntegerField(verbose_name='Classe')
    compte_parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='sous_comptes', verbose_name='Compte parent')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')

    class Meta:
        verbose_name = 'Plan comptable'
        verbose_name_plural = 'Plan comptable'
        ordering = ['numero_compte']
        constraints = [
            models.UniqueConstraint(fields=['societe', 'numero_compte'], name='uniq_plancomptable_societe_numero'),
        ]
        indexes = [
            models.Index(fields=['societe', 'numero_compte']),
            models.Index(fields=['type_compte']),
        ]

    def __str__(self):
        return f"{self.numero_compte} - {self.nom_compte}"

    def save(self, *args, **kwargs):
        numero = (self.numero_compte or '').strip()
        if numero:
            if len(numero) <= 4:
                numero = f"{numero.zfill(4)}00"
            elif len(numero) < 6:
                numero = numero.zfill(6)
        self.numero_compte = numero
        super().save(*args, **kwargs)


class Journal(models.Model):
    TYPE_NUMEROTATION_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('continue_journal', 'Continue par journal'),
    ]

    TYPE_JOURNAL_CHOICES = [
        ('Achat', 'Achat'),
        ('Vente', 'Vente'),
        ('Banque', 'Banque'),
        ('Caisse', 'Caisse'),
        ('OD', 'OD'),
    ]

    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='journaux', verbose_name='Société')
    code = models.CharField(max_length=10, unique=True, verbose_name='Code journal')
    nom = models.CharField(max_length=100, verbose_name='Nom journal')
    type_journal = models.CharField(max_length=20, choices=TYPE_JOURNAL_CHOICES, verbose_name='Type journal', default='OD')
    racine_numero_ecriture = models.CharField(max_length=20, blank=True, null=True, verbose_name='Racine numéro écriture')
    type_numerotation = models.CharField(max_length=20, choices=TYPE_NUMEROTATION_CHOICES, default='mensuel', verbose_name='Type de numérotation')
    compte_defaut = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, blank=True, null=True, related_name='journaux_par_defaut', verbose_name='Compte par défaut')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaux'
        ordering = ['code']
        indexes = [
            models.Index(fields=['societe']),
        ]

    def __str__(self):
        return self.nom

    @property
    def code_journal(self):
        return self.code

    @code_journal.setter
    def code_journal(self, value):
        self.code = value

    @property
    def nom_journal(self):
        return self.nom

    @nom_journal.setter
    def nom_journal(self, value):
        self.nom = value


class ComptabilisationParametre(models.Model):
    TYPE_NUMEROTATION_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('continue_journal', 'Continue par journal'),
    ]

    MODE_ANNULATION_CHOICES = [
        ('contrepassation', 'Contrepassation automatique'),
        ('suppression', 'Suppression avec trace'),
    ]

    societe = models.OneToOneField(Societe, on_delete=models.CASCADE, related_name='parametres_comptabilisation', verbose_name='Société')
    journal_defaut = models.ForeignKey(Journal, on_delete=models.SET_NULL, blank=True, null=True, related_name='parametres_par_defaut', verbose_name='Journal par défaut')
    compte_tiers_client = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, blank=True, null=True, related_name='parametres_tiers_client', verbose_name='Compte tiers client')
    compte_tiers_fournisseur = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, blank=True, null=True, related_name='parametres_tiers_fournisseur', verbose_name='Compte tiers fournisseur')
    racine_numero_ecriture = models.CharField(max_length=20, default='ECR', verbose_name='Racine numéro écriture')
    equilibre_obligatoire = models.BooleanField(default=True, verbose_name='Équilibre débit/crédit obligatoire')
    numerotation_auto = models.BooleanField(default=True, verbose_name='Numérotation automatique des écritures')
    type_numerotation = models.CharField(max_length=20, choices=TYPE_NUMEROTATION_CHOICES, default='mensuel', verbose_name='Type de numérotation')
    verrouillage_periode = models.BooleanField(default=False, verbose_name='Contrôle de période comptable')
    champs_facultatifs_actifs = models.BooleanField(default=True, verbose_name='Activer les champs facultatifs')
    modeles_recurrents_actifs = models.BooleanField(default=False, verbose_name='Activer les modèles d\'écriture récurrents')
    mode_annulation = models.CharField(max_length=20, choices=MODE_ANNULATION_CHOICES, default='contrepassation', verbose_name='Mode d\'annulation')
    motif_annulation_obligatoire = models.BooleanField(default=True, verbose_name='Motif d\'annulation obligatoire')
    roles_autorises_annulation = models.ManyToManyField(Role, blank=True, related_name='parametres_annulation', verbose_name='Rôles autorisés à annuler')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')

    class Meta:
        verbose_name = 'Paramètre de comptabilisation'
        verbose_name_plural = 'Paramètres de comptabilisation'
        ordering = ['societe__raison_sociale']

    def __str__(self):
        return f"Paramètres comptabilisation - {self.societe.raison_sociale}"


class EcritureComptable(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name='ecritures_comptables', verbose_name='Société', null=True, blank=True)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='ecritures_comptables', verbose_name='Agence', null=True, blank=True)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='ecritures', verbose_name='Journal')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='ecritures_comptables', verbose_name='Client', null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, related_name='ecritures_comptables', verbose_name='Fournisseur', null=True, blank=True)
    numero_ecriture = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='Numéro écriture')
    date_ecriture = models.DateField(verbose_name='Date écriture')
    reference = models.CharField(max_length=100, verbose_name='Référence écriture')
    libelle_ecriture = models.TextField(blank=True, null=True, verbose_name='Libellé écriture')
    intitule = models.CharField(max_length=200, verbose_name='Intitulé')
    piece_comptable = models.CharField(max_length=50, blank=True, null=True, verbose_name='Pièce comptable')
    compte = models.CharField(max_length=100, verbose_name='Compte')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Débit')
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Crédit')
    valide = models.BooleanField(default=False, verbose_name='Validé')
    utilisateur = models.ForeignKey('UtilisateurProfile', on_delete=models.SET_NULL, related_name='ecritures_comptables', blank=True, null=True, verbose_name='Utilisateur')
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Projet')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date modification')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Écriture comptable'
        verbose_name_plural = 'Écritures comptables'
        ordering = ['-date_ecriture', 'reference']
        indexes = [
            models.Index(fields=['agence', 'date_ecriture']),
            models.Index(fields=['journal']),
        ]

    def save(self, *args, **kwargs):
        if not self.numero_ecriture and self.reference:
            self.numero_ecriture = self.reference
        if not self.reference and self.numero_ecriture:
            self.reference = self.numero_ecriture
        if not self.libelle_ecriture and self.intitule:
            self.libelle_ecriture = self.intitule
        if not self.intitule and self.libelle_ecriture:
            self.intitule = self.libelle_ecriture[:200]
        if self.societe_id is None and self.journal_id:
            self.societe_id = self.journal.societe_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.journal}"


class LigneEcriture(models.Model):
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.CASCADE, related_name='lignes', verbose_name='Écriture')
    compte = models.ForeignKey(PlanComptable, on_delete=models.PROTECT, related_name='lignes_ecriture', verbose_name='Compte')
    libelle = models.TextField(blank=True, null=True, verbose_name='Libellé')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Débit')
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Crédit')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')

    class Meta:
        verbose_name = 'Ligne écriture'
        verbose_name_plural = 'Lignes écritures'
        indexes = [
            models.Index(fields=['ecriture']),
            models.Index(fields=['compte']),
        ]

    def __str__(self):
        return f"{self.ecriture.numero_ecriture or self.ecriture.reference} - {self.compte.numero_compte}"


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('transfert', 'Transfert'),
        ('ajustement', 'Ajustement'),
        ('inventaire', 'Inventaire'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name='Produit')
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, verbose_name='Agence')
    quantite = models.IntegerField(verbose_name='Quantité')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Type de mouvement')
    prix_unitaire = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name='Prix unitaire')
    agence_destination = models.ForeignKey(Agence, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Agence destination', related_name='mouvements_destination')
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name='Référence')
    motif = models.TextField(blank=True, null=True, verbose_name='Motif')
    utilisateur = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name='Utilisateur')
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name='Date du mouvement')

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-date_mouvement']
        indexes = [
            models.Index(fields=['agence', 'date_mouvement']),
            models.Index(fields=['produit']),
            models.Index(fields=['type_mouvement']),
        ]

    def __str__(self):
        return f"{self.produit} - {self.type_mouvement} ({self.quantite})"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('VIEW', 'Consultation'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name='Utilisateur')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Action')
    content_type = models.CharField(max_length=100, verbose_name='Type de contenu')
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name='ID Objet')
    object_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nom de l\'objet')
    old_values = models.JSONField(blank=True, null=True, verbose_name='Valeurs précédentes')
    new_values = models.JSONField(blank=True, null=True, verbose_name='Nouvelles valeurs')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    details = models.TextField(blank=True, null=True, verbose_name='Détails supplémentaires')

    class Meta:
        verbose_name = 'Journal d\'activité'
        verbose_name_plural = 'Journaux d\'activité'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['content_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.content_type} ({self.timestamp})"


class Caisse(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='caisses', verbose_name='Agence')
    code_caisse = models.CharField(max_length=20, unique=True, verbose_name='Code caisse')
    nom_caisse = models.CharField(max_length=100, verbose_name='Nom caisse')
    solde_initial = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Solde initial')
    solde_actuel = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Solde actuel')
    responsable = models.ForeignKey('UtilisateurProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='caisses_responsable', verbose_name='Responsable')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')

    class Meta:
        verbose_name = 'Caisse'
        verbose_name_plural = 'Caisses'
        ordering = ['nom_caisse']
        indexes = [
            models.Index(fields=['agence']),
        ]

    def __str__(self):
        return f"{self.nom_caisse} ({self.code_caisse})"


class MouvementCaisse(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('Entree', 'Entree'),
        ('Sortie', 'Sortie'),
    ]

    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE, related_name='mouvements_caisse', verbose_name='Caisse')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT_CHOICES, verbose_name='Type mouvement')
    montant = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant')
    motif = models.TextField(blank=True, null=True, verbose_name='Motif')
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name='Référence')
    utilisateur = models.ForeignKey('UtilisateurProfile', on_delete=models.PROTECT, related_name='mouvements_caisse', verbose_name='Utilisateur')
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name='Date mouvement')

    class Meta:
        verbose_name = 'Mouvement caisse'
        verbose_name_plural = 'Mouvements caisse'
        ordering = ['-date_mouvement']
        indexes = [
            models.Index(fields=['caisse', 'date_mouvement']),
        ]

    def __str__(self):
        return f"{self.caisse.code_caisse} - {self.type_mouvement} - {self.montant}"


class Banque(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='banques', verbose_name='Agence')
    code_banque = models.CharField(max_length=20, unique=True, verbose_name='Code banque')
    nom_banque = models.CharField(max_length=100, verbose_name='Nom banque')
    solde_initial = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Solde initial')
    solde_actuel = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Solde actuel')
    responsable = models.ForeignKey('UtilisateurProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='banques_responsable', verbose_name='Responsable')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date création')

    class Meta:
        verbose_name = 'Banque'
        verbose_name_plural = 'Banques'
        ordering = ['nom_banque']
        indexes = [
            models.Index(fields=['agence']),
        ]

    def __str__(self):
        return f"{self.nom_banque} ({self.code_banque})"


class MouvementBanque(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('Entree', 'Entree'),
        ('Sortie', 'Sortie'),
    ]

    banque = models.ForeignKey(Banque, on_delete=models.CASCADE, related_name='mouvements_banque', verbose_name='Banque')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT_CHOICES, verbose_name='Type mouvement')
    montant = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant')
    motif = models.TextField(blank=True, null=True, verbose_name='Motif')
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name='Référence')
    utilisateur = models.ForeignKey('UtilisateurProfile', on_delete=models.PROTECT, related_name='mouvements_banque', verbose_name='Utilisateur')
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name='Date mouvement')

    class Meta:
        verbose_name = 'Mouvement banque'
        verbose_name_plural = 'Mouvements banque'
        ordering = ['-date_mouvement']
        indexes = [
            models.Index(fields=['banque', 'date_mouvement']),
        ]

    def __str__(self):
        return f"{self.banque.code_banque} - {self.type_mouvement} - {self.montant}"


class LogActivite(models.Model):
    utilisateur = models.ForeignKey('UtilisateurProfile', on_delete=models.SET_NULL, blank=True, null=True, related_name='logs_activite', verbose_name='Utilisateur')
    action = models.CharField(max_length=100, verbose_name='Action')
    table_cible = models.CharField(max_length=50, blank=True, null=True, verbose_name='Table cible')
    enregistrement_id = models.BigIntegerField(blank=True, null=True, verbose_name='Enregistrement ID')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    adresse_ip = models.CharField(max_length=45, blank=True, null=True, verbose_name='Adresse IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    date_action = models.DateTimeField(auto_now_add=True, verbose_name='Date action')

    class Meta:
        verbose_name = 'Log activité'
        verbose_name_plural = 'Logs activité'
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['utilisateur', 'date_action']),
            models.Index(fields=['table_cible']),
            models.Index(fields=['date_action']),
        ]

    def __str__(self):
        return f"{self.action} - {self.table_cible or '-'} ({self.date_action})"
