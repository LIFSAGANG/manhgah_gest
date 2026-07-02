from django.db import models


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
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    reference = models.CharField(max_length=100, unique=True, verbose_name='Référence')
    nom = models.CharField(max_length=200, verbose_name='Nom')
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Catégorie')
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Prix unitaire')
    quantite_stock = models.PositiveIntegerField(default=0, verbose_name='Quantité en stock')
    date_creation = models.DateField(verbose_name='Date de création')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.reference})"


class Client(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom')
    code = models.CharField(max_length=50, unique=True, verbose_name='Code client')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telephone = models.CharField(max_length=40, blank=True, null=True, verbose_name='Téléphone')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name='Pays')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code})"


class Facture(models.Model):
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
    ]

    reference = models.CharField(max_length=100, unique=True, verbose_name='Référence facture')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures', verbose_name='Client')
    date_emission = models.DateField(verbose_name='Date d’émission')
    montant_total = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant total')
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon', verbose_name='Statut')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission', 'reference']

    def __str__(self):
        return f"{self.reference} - {self.client.nom}"


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
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Agence')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code projet')
    nom = models.CharField(max_length=200, verbose_name='Nom du projet')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    date_debut = models.DateField(blank=True, null=True, verbose_name='Date de début')
    date_fin = models.DateField(blank=True, null=True, verbose_name='Date de fin')
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Budget')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Categorie(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code catégorie')
    nom = models.CharField(max_length=100, verbose_name='Nom catégorie')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Catégorie parente')
    date_creation = models.DateField(verbose_name='Date de création')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    code = models.CharField(max_length=50, unique=True, verbose_name='Code fournisseur')
    nom = models.CharField(max_length=200, verbose_name='Nom fournisseur')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telephone = models.CharField(max_length=40, blank=True, null=True, verbose_name='Téléphone')
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville')
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name='Pays')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Achat(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('commande', 'Commande'),
        ('recu', 'Reçu'),
        ('payee', 'Payée'),
    ]

    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, verbose_name='Fournisseur')
    reference = models.CharField(max_length=100, unique=True, verbose_name='Référence achat')
    date_commande = models.DateField(verbose_name='Date de commande')
    montant_total = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Montant total')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon', verbose_name='Statut')
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Projet')
    agence = models.ForeignKey(Agence, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Agence')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Achat'
        verbose_name_plural = 'Achats'
        ordering = ['-date_commande', 'reference']

    def __str__(self):
        return f"{self.reference} - {self.fournisseur.nom}"


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


class Journal(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name='Société')
    code = models.CharField(max_length=50, unique=True, verbose_name='Code journal')
    nom = models.CharField(max_length=200, verbose_name='Nom journal')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    actif = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaux'
        ordering = ['code']

    def __str__(self):
        return self.nom


class EcritureComptable(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, verbose_name='Journal')
    date_ecriture = models.DateField(verbose_name='Date écriture')
    reference = models.CharField(max_length=100, verbose_name='Référence écriture')
    intitule = models.CharField(max_length=200, verbose_name='Intitulé')
    compte = models.CharField(max_length=100, verbose_name='Compte')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Débit')
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Crédit')
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Projet')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Écriture comptable'
        verbose_name_plural = 'Écritures comptables'
        ordering = ['-date_ecriture', 'reference']

    def __str__(self):
        return f"{self.reference} - {self.journal}"


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('transfert', 'Transfert'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name='Produit')
    agence = models.ForeignKey(Agence, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Agence')
    quantite = models.IntegerField(verbose_name='Quantité')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, default='entree', verbose_name='Type de mouvement')
    date_mouvement = models.DateField(verbose_name='Date du mouvement')
    remarque = models.TextField(blank=True, null=True, verbose_name='Remarque')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-date_mouvement']

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
