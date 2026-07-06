import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manhgah_gest.settings')
django.setup()

from core.models import EcritureComptable, LigneEcriture, Societe, Journal, PlanComptable
from django.utils import timezone

# Get WENDINSO SERVICE
societe = Societe.objects.get(code_societe='WS')
print(f"Société: {societe.raison_sociale}")

# Get journal
journal = Journal.objects.filter(societe=societe).first()
if not journal:
    journal = Journal.objects.create(
        societe=societe, 
        code_journal='VTE',
        nom_journal='Ventes',
        type_journal='Vente'
    )
print(f"Journal: {journal.nom_journal}")

# Create an ecriture
ecriture = EcritureComptable.objects.create(
    societe=societe,
    journal=journal,
    numero_ecriture='TEST-0001',
    date_ecriture=timezone.localdate(),
)
print(f"Écriture créée: {ecriture.numero_ecriture}")

# Get a compte
compte = PlanComptable.objects.filter(societe=societe).first()
if compte:
    ligne = LigneEcriture.objects.create(
        ecriture=ecriture,
        compte=compte,
        debit=1000,
        credit=0
    )
    print(f"Ligne créée pour le compte: {compte.numero_compte}")
else:
    print("Aucun compte trouvé")

print(f"\n✓ Écriture test créée pour WENDINSO SERVICE!")
