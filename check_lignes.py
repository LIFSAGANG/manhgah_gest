from core.models import LigneEcriture, Societe
print("=== Total lignes par société ===")
for societe in Societe.objects.all():
    count = LigneEcriture.objects.filter(ecriture__societe=societe).count()
    print(f"{societe.name_societe} (id={societe.id}): {count} lignes")
