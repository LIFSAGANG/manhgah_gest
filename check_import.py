import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manhgah_gest.settings')
django.setup()

from core.models import PlanComptable
from django.db.models import Count

# Stats générales
total = PlanComptable.objects.count()
par_type = PlanComptable.objects.values('type_compte').annotate(count=Count('id')).order_by('type_compte')
par_classe = PlanComptable.objects.values('classe').annotate(count=Count('id')).order_by('classe')

print(f'Total comptes: {total}')
print(f'\nPar type:')
for t in par_type:
    print(f'  {t["type_compte"]}: {t["count"]}')

print(f'\nPar classe:')
for c in par_classe:
    print(f'  Classe {c["classe"]}: {c["count"]} comptes')

print(f'\nExemples comptes clients (41):')
clients = PlanComptable.objects.filter(numero_compte__startswith='41')[:3]
for c in clients:
    print(f'  {c.numero_compte} - {c.nom_compte}')

print(f'\nExemples comptes fournisseurs (40):')
fournisseurs = PlanComptable.objects.filter(numero_compte__startswith='40')[:3]
for c in fournisseurs:
    print(f'  {c.numero_compte} - {c.nom_compte}')
