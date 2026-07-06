import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manhgah_gest.settings')
django.setup()

from core.models import PlanComptable
from django.db.models import Count

societes = ['Société Central', 'WENDINSO SERVICE']

for societe_name in societes:
    print(f'\n=== {societe_name} ===')
    par_type = (
        PlanComptable.objects
        .filter(societe__raison_sociale=societe_name)
        .values('type_compte')
        .annotate(count=Count('id'))
        .order_by('type_compte')
    )
    
    for t in par_type:
        print(f"  {t['type_compte']}: {t['count']} comptes")
    
    # Exemples
    print(f'\n  Exemples comptes:')
    exemples = PlanComptable.objects.filter(societe__raison_sociale=societe_name)[:3]
    for e in exemples:
        print(f'    {e.numero_compte} - {e.nom_compte} ({e.type_compte})')
