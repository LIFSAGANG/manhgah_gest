# 📋 RÉSUMÉ TECHNIQUE - PROJET MANHGAH_GEST

## 1. VUE D'ENSEMBLE

**Nom du projet** : `manhgah_gest`  
**Type** : Application web de gestion comptable et commerciale  
**Stack** : Django 5.2.9 (Backend) + Bootstrap 5.3 (Frontend UI)  
**Base de données** : SQLite3 (local)  
**Serveur** : http://127.0.0.1:8000/  
**Langue** : Français

---

## 2. ARCHITECTURE GLOBALE

```
manhgah_gest/
├── Backend Django
│   ├── core/ (App principale)
│   ├── manhgah_gest/ (Configuration Django)
│   └── db.sqlite3 (Base de données SQLite)
├── Frontend
│   ├── templates/ (Fichiers HTML)
│   ├── static/ (CSS, JS, images)
│   └── frontend/ (Vite.js - non actif actuellement)
└── Configuration
    ├── manage.py (Ligne de commande Django)
    ├── requirements.txt (Dépendances Python)
    └── settings.py (Configuration Django)
```

---

## 3. BACKEND - DJANGO

### 3.1 Structure des Applications

**App principale** : `core/`

#### Fichiers essentiels :
- `models.py` → Définition des modèles de données (tables DB)
- `views.py` → Logique métier (fonctions qui répondent aux requêtes)
- `forms.py` → Formulaires HTML (validation des données)
- `urls.py` → Routes (chemins d'accès)
- `serializers.py` → Conversion modèles ↔ JSON (API)
- `middleware.py` → Interception des requêtes (logs)
- `signals.py` → Actions automatiques (événements)
- `migrations/` → Historique des changements BD

---

## 4. BASE DE DONNÉES - MODÈLES (core/models.py)

### 4.1 Relation entre les tables

```
Societe (entreprise principale)
├─ Produit (produits de la société)
│  ├─ Categorie (catégories de produits)
│  └─ MouvementStock (entrées/sorties stock)
├─ Agence (succursales/filiales)
├─ Client (clients de la société)
│  └─ Facture (factures vendues aux clients)
├─ Fournisseur (fournisseurs)
│  └─ Achat (achats chez fournisseurs)
├─ Depense (dépenses)
├─ Ecriture (écritures comptables)
├─ Journal (journaux comptables)
├─ PlanComptable (plan comptable)
├─ Categorie (déjà listée - hiérarchie)
├─ Role (rôles utilisateurs)
└─ Departement (départements)
```

### 4.2 Modèles clés créés/modifiés

#### **SOCIETE**
```python
Nom de table : core_societe
Champs :
- id (INTEGER, PRIMARY KEY)
- nom (VARCHAR 200) ← Obligatoire
- code (VARCHAR 50, UNIQUE) ← Obligatoire
- email (EMAIL) ← Optionnel
- telephone (VARCHAR 40) ← Optionnel
- adresse (TEXT) ← Optionnel
- ville (VARCHAR 100) ← Optionnel
- pays (VARCHAR 100) ← Optionnel
- actif (BOOLEAN) ← Défaut: True
- created_at (DATETIME) ← Auto
- updated_at (DATETIME) ← Auto
```

#### **PRODUIT** (Modifié récemment)
```python
Nom de table : core_produit
Champs :
- id (INTEGER, PRIMARY KEY)
- societe_id (INTEGER, FOREIGN KEY) ← ✅ NOUVEAU - Relie à Societe
- reference (VARCHAR 100, UNIQUE) ← Obligatoire
- nom (VARCHAR 200) ← Obligatoire
- categorie_id (INTEGER, FOREIGN KEY) ← Optionnel (peut être NULL)
- prix_unitaire (DECIMAL 12,2) ← Obligatoire
- quantite_stock (POSITIVE INTEGER) ← Défaut: 0
- date_creation (DATE) ← ✅ NOUVEAU - Obligatoire
- actif (BOOLEAN) ← Défaut: True
- created_at (DATETIME) ← Auto
- updated_at (DATETIME) ← Auto

Relations :
- societe_id → FK core_societe.id (CASCADE delete)
- categorie_id → FK core_categorie.id (SET_NULL)
```

#### **CATEGORIE** (Modifié)
```python
Nom de table : core_categorie
Champs :
- id (INTEGER, PRIMARY KEY)
- societe_id (INTEGER, FOREIGN KEY) ← Obligatoire
- code (VARCHAR 20, UNIQUE) ← Obligatoire
- nom (VARCHAR 100) ← Obligatoire
- description (TEXT) ← Optionnel
- parent_id (INTEGER, SELF FK) ← Hiérarchie optionnelle
- date_creation (DATE) ← ✅ NOUVEAU - Obligatoire
- actif (BOOLEAN) ← Défaut: True
- created_at (DATETIME) ← Auto

Relations :
- societe_id → FK core_societe.id (CASCADE)
- parent_id → FK core_categorie.id (hiérarchie)
```

#### **CLIENT**
```python
Nom de table : core_client
Champs :
- nom, code, email, téléphone, adresse, ville, pays, actif
- Pas de lien societe (à améliorer)
```

#### **FACTURE**
```python
Nom de table : core_facture
Champs :
- reference (UNIQUE) ← Obligatoire
- client_id (FK) ← Relie à Client
- date_emission (DATE)
- montant_total (DECIMAL 14,2)
- statut (CHOICE: brouillon/envoyée/payée)
- notes (TEXT)
```

#### **MOUVEMENT_STOCK**
```python
Nom de table : core_mouvementstock
Champs :
- produit_id (FK) ← Relie à Produit
- type_mouvement (CHOICE: entree/sortie)
- quantite (POSITIVE INTEGER)
Fonction : Chaque création AUTOMET à jour produit.quantite_stock
```

---

## 5. FRONTEND - TEMPLATES

### 5.1 Structure des fichiers HTML

**Chemin** : `templates/core/`

#### Architecture de navigation (IFRAME)
```
Accueil (accueil.html)
│
├─ Produits et Stock (produits_stock_page.html) ← CONTENEUR
│  ├─ Menu topbar : Accueil | Produits ▼ | Etats ▼
│  └─ iframe src="etat_stock_page.html?standalone=1"
│     ├─ Etat du stock (etat_stock_page.html)
│     ├─ Mouvements (mouvement_list.html)
│     ├─ Inventaire (inventaire_stock_page.html)
│     ├─ Produits (produit_list.html)
│     │  ├─ Ajouter → produit_form.html
│     │  └─ Modifier → produit_form.html
│     └─ Catégories (categorie_list.html)
│        ├─ Ajouter → categorie_form.html
│        └─ Modifier → categorie_form.html
│
├─ Ventes (ventes_page.html) ← CONTENEUR
│  ├─ Menu : Accueil | Factures ▼ | Etats ▼ | Clients ▼
│  └─ iframe → Factures/Clients/TVA
│
├─ Achats (achats_page.html) ← À faire
│  └─ iframe → Achats/Fournisseurs
│
├─ Comptabilité (comptabilite_page.html) ← CONTENEUR
│  ├─ Menu : Accueil | Plan comptable | Journaux | Écritures ▼
│  └─ iframe → Plans/Journaux/Brouillard/Balances/Tiers
│
├─ Contacts (contacts_page.html) ← À faire
│  └─ iframe → Clients/Fournisseurs
│
├─ Statistique (statistique_page.html) ← À faire
│  └─ iframe → Graphiques/Rapports
│
└─ Paramètre (parametre_page.html) ← À faire
   └─ iframe → Sociétés/Roles/Utilisateurs
```

### 5.2 Système d'affichage fullscreen (standalone)

**Fonctionnement** :
1. Menu clique → Charge URL avec `?standalone=1`
2. Base template (`base.html`) détecte `?standalone=1`
3. CSS spécial s'applique : padding=0, margin=0, fullscreen
4. Contenu remplit 100% de l'écran
5. Topbar reste visible avec logo + Déconnexion

**Fichiers modifiés** :
- `base.html` (bloc standalone CSS)
- `static/css/style.css` (classes fullscreen)
- `produits_stock_page.html` (iframe + JavaScript)
- `ventes_page.html` (iframe + JavaScript)
- `comptabilite_page.html` (iframe + JavaScript)

---

## 6. FORMULAIRES - VALIDATION

**Chemin** : `core/forms.py`

### 6.1 Formulaires créés/modifiés

#### **ProduitForm**
```python
Fields affichés :
1. societe (Select dropdown) ← Obligatoire
2. reference (TextInput) ← Obligatoire
3. nom (TextInput) ← Obligatoire
4. categorie (Select dropdown) ← Optionnel mais montré
5. prix_unitaire (NumberInput, step=0.01) ← Obligatoire
6. date_creation (DateInput, type=date) ← ✅ NOUVEAU
7. quantite_stock (NumberInput) ← Optionnel
8. actif (CheckboxInput) ← Défaut: True

Validation :
- Django valide automatiquement les types
- DB rejette si champ obligatoire vide
```

#### **CategorieForm**
```python
Fields :
1. societe (Select) ← Obligatoire
2. code (TextInput) ← Obligatoire, unique
3. nom (TextInput) ← Obligatoire
4. date_creation (DateInput) ← ✅ NOUVEAU
5. description (Textarea) ← Optionnel
6. actif (Checkbox) ← Défaut: True
```

---

## 7. VUES - LOGIQUE MÉTIER

**Chemin** : `core/views.py`

### 7.1 Vues principales (fonctions)

#### **Produits**
```python
produit_list() → Affiche tous les produits
├─ GET request → HTML list
└─ Filtre par societe/categorie

produit_create() → Ajouter produit
├─ GET → Affiche formulaire vide
├─ POST → Validation + Sauvegarde BD
└─ Redirection → produit_list

produit_update(pk) → Modifier produit
├─ GET → Affiche formulaire pré-rempli
├─ POST → Validation + Mise à jour BD
└─ Redirection → produit_list

produit_delete(pk) → Supprimer produit
├─ GET → Demande confirmation
├─ POST → Delete BD
└─ Redirection → produit_list
```

#### **Catégories**
```python
categorie_create() → Ajouter catégorie
├─ GET → Form vide
├─ POST → Validation + Save
└─ Inclut : societe, code, nom, date_creation

categorie_update(pk) → Modifier
categorie_delete(pk) → Supprimer
categorie_list() → Affiche toutes catégories
```

#### **Mouvements Stock** (Spécial)
```python
mouvement_create() → Ajouter mouvement
├─ Crée enregistrement MouvementStock
├─ PUIS met à jour produit.quantite_stock :
│  ├─ Si type='entree' → +quantité
│  └─ Si type='sortie' → -quantité (min 0)
└─ Sauvegarde tout en BD

Erreur possible :
- Si type ni 'entree' ni 'sortie' → erreur validation
- Si quantité < 0 → clampée à 0
```

---

## 8. MIGRATIONS - HISTORIQUE DB

**Chemin** : `core/migrations/`

### 8.1 Migrations existantes

| N° | Fichier | Description |
|---|---|---|
| 0001 | initial | Tables initiales (Societe, Produit, Client, etc.) |
| 0002 | produit | (Support ancien) |
| 0003 | client_facture | Client + Facture tables |
| 0004 | roles_permissions | Permissions + Roles |
| 0005 | alter_role_options | Modification Role |
| 0006 | activitylog | Table ActivityLog (logs) |
| 0007 | alter_produit_categorie | `categorie` CharField → ForeignKey |
| 0008 | categorie_date_creation | ✅ Ajout champ `date_creation` sur Categorie |
| 0009 | produit_date_creation_societe | ✅ Ajout `date_creation` + `societe` sur Produit |

### 8.2 Comment appliquer migrations

```bash
# Créer migration (détecte changements models.py)
python manage.py makemigrations

# Appliquer migration en BD
python manage.py migrate

# Voir état migrations
python manage.py showmigrations

# Annuler migration (dangereuse)
python manage.py migrate core 0007
```

---

## 9. API REST (BONUS)

**Chemin** : `core/api_views.py`, `core/serializers.py`

Endpoints disponibles (si utilisés) :
```
/api/produits/ → GET: liste produits | POST: créer
/api/produits/<id>/ → GET: détail | PUT: modifier | DELETE
/api/categories/ → CRUD catégories
/api/clients/ → CRUD clients
/api/factures/ → CRUD factures
```

Actuellement peu utilisé (frontend préfère HTML/Django templates).

---

## 10. CONFIGURATION DJANGO

**Chemin** : `manhgah_gest/settings.py`

### 10.1 Paramètres clés

```python
DEBUG = True                              # Mode développement
ALLOWED_HOSTS = ['*']                     # Accepte toutes requêtes
SECRET_KEY = 'django-insecure-...'       # Clé de chiffrement

INSTALLED_APPS = [
    'django.contrib.admin',               # Admin Django
    'django.contrib.auth',                # Authentification
    'rest_framework',                     # API REST
    'corsheaders',                        # CORS pour requêtes cross-domain
    'core',                               # Notre app principale
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Fichier BD local
    }
}

X_FRAME_OPTIONS = 'SAMEORIGIN'           # Permet iframes même domaine
STATICFILES_DIRS = [BASE_DIR / 'static'] # Dossier CSS/JS static
```

---

## 11. WORKFLOW D'UNE REQUÊTE

### 11.1 Exemple : Ajouter un produit

```
1. USER ACTION
   Utilisateur clique "Ajouter produit"
   ↓
2. URL ROUTING (urls.py)
   URL : /produits/ajouter/
   Django → core.views.produit_create
   ↓
3. VUE (views.py)
   a) GET request :
      - Crée ProduitForm() vide
      - Passe au template
   
   b) POST request :
      - Récupère données du formulaire
      - ProduitForm.is_valid() → Valide champs
      ↓
4. FORMULAIRE (forms.py)
   Valide :
   - societe_id existe ? (SELECT * WHERE id=...)
   - reference unique ? (SELECT * WHERE reference=...)
   - prix_unitaire est nombre ?
   - date_creation au format date ?
   ↓
5. MODÈLE (models.py)
   Si tout OK :
   - Produit(**data) → Crée objet Python
   - .save() → INSERT INTO core_produit VALUES(...)
   ↓
6. BASE DE DONNÉES (db.sqlite3)
   INSERT exécuté :
   → Nouvelle ligne ajoutée table core_produit
   → societe_id = valeur sélectionnée
   → categorie_id = valeur sélectionnée (ou NULL)
   ↓
7. RÉPONSE
   Vue redirige → /produits/ (produit_list)
   Affiche message : "Produit ajouté ✓"
```

---

## 12. ERREURS FRÉQUENTES & SOLUTIONS

| Erreur | Cause | Solution |
|---|---|---|
| **OperationalError: no such column** | Colonne pas en BD | `python manage.py migrate` |
| **IntegrityError: NOT NULL constraint failed** | Champ obligatoire vide | Remplir le champ dans formulaire |
| **IntegrityError: UNIQUE constraint failed** | Valeur déjà existe | Utiliser valeur unique |
| **FieldError: Unknown field** | Champ pas dans form fields | Ajouter dans `fields = [...]` |
| **NoReverseMatch** | URL nommée inexistante | Vérifier `@path()` dans urls.py |
| **TemplateDoesNotExist** | Fichier .html manquant | Créer fichier dans `templates/` |
| **FormatError: Invalid date** | Date pas au bon format | Utiliser `YYYY-MM-DD` ou DateInput |

---

## 13. FICHIERS CRÉÉS/MODIFIÉS (SESSION ACTUELLE)

### 13.1 Modèles (models.py)
✅ `Produit.societe` → ForeignKey(Societe)  
✅ `Produit.date_creation` → DateField  
✅ `Categorie.date_creation` → DateField  

### 13.2 Formulaires (forms.py)
✅ `ProduitForm` → Ajout societe + date_creation  
✅ `CategorieForm` → Ajout societe + date_creation  

### 13.3 Templates
✅ `produit_form.html` → Affiche societe + date_creation  

### 13.4 Migrations
✅ `0008_categorie_date_creation.py` → Catégorie  
✅ `0009_produit_date_creation_societe.py` → Produit  

---

## 14. POINTS D'AMÉLIORATION FUTURS

- [ ] Lier Client → Societe (actuellement orphelin)
- [ ] Lier Fournisseur → Achat (gérer stocks depuis achats)
- [ ] Lier Facture → Societe (tracer revenu par société)
- [ ] Module Achats/Contacts/Statistiques/Paramètres (à créer)
- [ ] API REST complète + Frontend React/Vue
- [ ] Dashboard avec graphiques

---

## 15. COMMANDES UTILES (Terminal)

```bash
# Démarrer serveur
python manage.py runserver 8000

# Vérifier erreurs
python manage.py check

# Créer migrations
python manage.py makemigrations

# Appliquer migrations
python manage.py migrate

# Admin Django
python manage.py createsuperuser  # Créer utilisateur admin
# Puis : http://127.0.0.1:8000/admin

# Shell Python (teste code)
python manage.py shell
>>> from core.models import Produit
>>> Produit.objects.all()  # Liste produits
```

---

## Conclusion

**En résumé pour un informaticien** :

C'est une **application web monolithique Django** utilisant :
- **Frontend** : Django Templates + Bootstrap + iframes (pas de SPA)
- **Backend** : Logique métier en views.py + validation forms.py
- **BD** : SQLite3 avec relations FK et contraintes
- **Middleware** : Logs d'activité automatiques
- **Architecture** : Modèle MVC classique (Models → Views → Templates)

Flux : **URL → View → Form validation → Model.save() → DB update → Template render**

Les erreurs viennent généralement de :
1. Migrations non appliquées
2. Champs obligatoires manquants dans formulaires
3. Contraintes DB (UNIQUE, NOT NULL)
4. Champs manquants dans `form.fields = [...]`

Pour déboguer : Vérifier **logs terminal**, **erreur exacte**, puis **migrations en cours**.
