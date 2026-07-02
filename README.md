# Manhgah Gest

Application de gestion construite avec Django (backend), Django REST Framework (API), PostgreSQL (base de donnees) et React + Vite (frontend).

## Prerequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Installation backend

1. Creer un environnement virtuel.
2. Installer les dependances:

```bash
pip install -r requirements.txt
```

3. Copier `.env.example` vers `.env` et adapter les valeurs PostgreSQL.
4. Appliquer les migrations:

```bash
python manage.py migrate
```

5. Lancer Django:

```bash
python manage.py runserver
```

## Installation frontend React

```bash
cd frontend
npm install
npm run dev
```

Le frontend tourne sur `http://127.0.0.1:5173`.

## API

Les endpoints REST sont exposes via `/api/`.
Exemples:

- `/api/clients/`
- `/api/produits/`
- `/api/achats/`
- `/api/status/`

## Notes

- En developpement React, Vite proxyfie automatiquement `/api`, `/login` et `/logout` vers Django.
- Si vous n'utilisez pas PostgreSQL, le projet peut encore fonctionner en SQLite (fallback via settings).
