import openpyxl
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PlanComptable, Societe


class Command(BaseCommand):
    help = 'Import plan comptable depuis un fichier Excel'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Chemin du fichier Excel')
        parser.add_argument('--clear', action='store_true', help='Supprimer les comptes existants avant import')
        parser.add_argument('--societe_id', type=int, default=None, help='ID de la société cible (si omis, importe dans toutes les sociétés)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        clear = options.get('clear', False)
        societe_id = options.get('societe_id', None)

        # Charger le fichier Excel
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lecture fichier: {e}'))
            return

        # Récupérer les sociétés cibles
        if societe_id:
            societes = Societe.objects.filter(id=societe_id)
            if not societes.exists():
                self.stdout.write(self.style.ERROR(f'Société avec ID {societe_id} non trouvée'))
                return
        else:
            societes = Societe.objects.all()
        
        if not societes.exists():
            self.stdout.write(self.style.ERROR('Aucune société trouvée en base'))
            return

        self.stdout.write(f'Sociétés cibles: {societes.count()}')
        for s in societes:
            self.stdout.write(f'  - {s.raison_sociale} (ID {s.id})')

        # Lire les comptes du fichier Excel
        comptes = []
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            numero_compte = (row[0] or '').strip()
            nom_compte = (row[1] or '').strip()
            type_raw = (row[2] or '').strip()

            if not numero_compte or not nom_compte:
                continue

            # Validation basique
            try:
                classe = int(numero_compte[0])
            except (ValueError, IndexError):
                self.stdout.write(self.style.WARNING(f'Row {row_idx}: Numéro compte invalide "{numero_compte}", ignoré'))
                continue

            comptes.append({
                'numero_compte': numero_compte,
                'nom_compte': nom_compte,
                'type_compte': type_raw,  # Garder le type tel quel
                'classe': classe,
            })

        self.stdout.write(f'\nComptes à importer: {len(comptes)}')

        # Importer pour chaque société
        for societe in societes:
            self.import_for_societe(societe, comptes, clear)

    def import_for_societe(self, societe, comptes, clear):
        self.stdout.write(f'\n--- Société: {societe.raison_sociale} ---')

        # Supprimer les comptes existants si --clear
        if clear:
            count = PlanComptable.objects.filter(societe=societe).count()
            PlanComptable.objects.filter(societe=societe).delete()
            self.stdout.write(f'✓ {count} comptes supprimés')

        # Import des comptes
        created = 0
        updated = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for compte in comptes:
                try:
                    obj, created_flag = PlanComptable.objects.update_or_create(
                        societe=societe,
                        numero_compte=compte['numero_compte'],
                        defaults={
                            'nom_compte': compte['nom_compte'],
                            'type_compte': compte['type_compte'],
                            'classe': compte['classe'],
                            'actif': True,
                        },
                    )
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors.append(f'{compte["numero_compte"]}: {e}')
                    skipped += 1

        # Résumé
        self.stdout.write(self.style.SUCCESS(f'✓ Import terminé!'))
        self.stdout.write(f'  Comptes créés: {created}')
        self.stdout.write(f'  Comptes mis à jour: {updated}')
        self.stdout.write(f'  Lignes ignorées: {skipped}')

        if errors:
            self.stdout.write(self.style.WARNING(f'⚠ {len(errors)} erreurs (premiers):'))
            for error in errors[:5]:
                self.stdout.write(f'  - {error}')

