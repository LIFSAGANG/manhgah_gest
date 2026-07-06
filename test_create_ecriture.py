import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manhgah_gest.settings')
django.setup()

from core.models import EcritureComptable, LigneEcriture, PlanComptable, Societe, Agence, Journal

societe = Societe.objects.get(id=2)  # PS / PANTSERV
agence = Agence.objects.first()
journal = Journal.objects.filter(societe=societe).first()
compte = PlanComptable.objects.filter(societe=societe).first()

if not journal or not compte:
    print('Données manquantes')
else:
    ecriture = EcritureComptable.objects.create(
        reference='FINAL-TEST',
        intitule='Final Test Ecriture',
        date_ecriture=datetime.now().date(),
        societe=societe,
        agence=agence,
        journal=journal
    )
    LigneEcriture.objects.create(
        ecriture=ecriture,
        compte=compte,
        debit=5000
    )
    print('✅ Ecriture de test créée')
    count = LigneEcriture.objects.filter(ecriture__societe=societe).count()
    print(f'PS a maintenant: {count} ligne(s)')
