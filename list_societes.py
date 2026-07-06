import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manhgah_gest.settings')
django.setup()

from core.models import Societe

print('Sociétés existantes:')
societes = Societe.objects.all()
for s in societes:
    print(f'  ID {s.id}: {s.raison_sociale} ({s.code_societe})')
