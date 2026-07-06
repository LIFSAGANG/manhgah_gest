from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import PlanComptable, Societe


SYSCOHADA_REVISE_ACCOUNTS = [
    ('1', 'Comptes de ressources durables'),
    ('10', 'Capital'),
    ('101', 'Capital social'),
    ('106', 'Reserves'),
    ('107', 'Report a nouveau'),
    ('109', 'Actionnaires, capital souscrit non appele'),
    ('11', 'Primes et ecarts'),
    ('12', 'Resultat de l exercice'),
    ('13', 'Subventions d investissement'),
    ('14', 'Provisions reglementees et fonds assimiles'),
    ('15', 'Provisions financieres pour risques et charges'),
    ('16', 'Emprunts et dettes assimilees'),
    ('17', 'Dettes de location-acquisition'),
    ('18', 'Dettes liees a des participations et comptes de liaison'),
    ('19', 'Provisions pour depreciation des comptes de ressources durables'),

    ('2', 'Comptes d actifs immobilises'),
    ('20', 'Charges immobilisees'),
    ('21', 'Immobilisations incorporelles'),
    ('22', 'Terrains'),
    ('23', 'Batiments, installations techniques et agencements'),
    ('24', 'Materiel'),
    ('26', 'Avances et acomptes verses sur immobilisations'),
    ('27', 'Immobilisations financieres'),
    ('28', 'Amortissements'),
    ('29', 'Provisions pour depreciation des immobilisations'),

    ('3', 'Comptes de stocks'),
    ('30', 'Marchandises'),
    ('31', 'Matieres premieres et fournitures liees'),
    ('32', 'Autres approvisionnements'),
    ('33', 'En-cours de production de biens'),
    ('34', 'En-cours de production de services'),
    ('35', 'Stocks de produits'),
    ('36', 'Stocks provenant d immobilisations'),
    ('37', 'Stocks a l exterieur'),
    ('38', 'Achats stockes'),
    ('39', 'Provisions pour depreciation des stocks'),

    ('4', 'Comptes de tiers'),
    ('40', 'Fournisseurs et comptes rattaches'),
    ('401', 'Fournisseurs'),
    ('402', 'Fournisseurs effets a payer'),
    ('403', 'Fournisseurs retenues de garantie'),
    ('404', 'Fournisseurs d immobilisations'),
    ('41', 'Clients et comptes rattaches'),
    ('411', 'Clients'),
    ('412', 'Clients effets a recevoir'),
    ('413', 'Clients retenues de garantie'),
    ('414', 'Clients douteux ou litigieux'),
    ('42', 'Personnel'),
    ('421', 'Personnel avances et acomptes'),
    ('422', 'Comites d entreprise, etablissements sociaux'),
    ('423', 'Personnel oppositions'),
    ('424', 'Personnel participation aux benefices'),
    ('43', 'Organismes sociaux'),
    ('431', 'Securite sociale'),
    ('438', 'Autres organismes sociaux'),
    ('44', 'Etat et collectivites publiques'),
    ('445', 'Etat TVA'),
    ('447', 'Etat impots et taxes'),
    ('448', 'Etat charges a payer et produits a recevoir'),
    ('45', 'Organismes internationaux'),
    ('46', 'Associes et groupe'),
    ('47', 'Debiteurs et crediteurs divers'),
    ('48', 'Creances et dettes hors activites ordinaires'),
    ('49', 'Provisions pour depreciation des comptes de tiers'),

    ('5', 'Comptes de tresorerie'),
    ('50', 'Titres de placement'),
    ('51', 'Valeurs a encaisser'),
    ('52', 'Banques'),
    ('53', 'Etablissements financiers et assimiles'),
    ('54', 'Instruments de tresorerie'),
    ('55', 'Instruments de tresorerie'),
    ('56', 'Banques, credits de tresorerie et d escompte'),
    ('57', 'Caisse'),
    ('58', 'Regies d avances, accreditifs et virements internes'),
    ('59', 'Provisions pour depreciation des comptes de tresorerie'),

    ('6', 'Comptes de charges des activites ordinaires'),
    ('60', 'Achats et variation de stocks'),
    ('601', 'Achats de marchandises'),
    ('602', 'Achats de matieres premieres et fournitures liees'),
    ('603', 'Variation des stocks de biens achetes'),
    ('604', 'Achats stockes de matieres et fournitures consommables'),
    ('605', 'Autres achats'),
    ('606', 'Achats non stockes de matieres et fournitures'),
    ('607', 'Transports'),
    ('608', 'Frais accessoires d achat'),
    ('609', 'Rabais, remises et ristournes obtenus'),
    ('61', 'Transports'),
    ('62', 'Services exterieurs A'),
    ('63', 'Services exterieurs B'),
    ('64', 'Impots et taxes'),
    ('65', 'Autres charges'),
    ('66', 'Charges de personnel'),
    ('67', 'Frais financiers et charges assimilees'),
    ('68', 'Dotations aux amortissements et provisions'),
    ('69', 'Impots sur les resultats et assimilies'),

    ('7', 'Comptes de produits des activites ordinaires'),
    ('70', 'Ventes'),
    ('701', 'Ventes de marchandises'),
    ('702', 'Ventes de produits finis'),
    ('703', 'Ventes de produits intermediaires et residuels'),
    ('704', 'Travaux'),
    ('705', 'Etudes'),
    ('706', 'Services vendus'),
    ('707', 'Produits des activites annexes'),
    ('708', 'Produits accessoires'),
    ('709', 'Rabais, remises et ristournes accordes'),
    ('71', 'Subventions d exploitation'),
    ('72', 'Production immobilisee'),
    ('73', 'Variation des stocks de biens et services produits'),
    ('74', 'Production de marchandises'),
    ('75', 'Autres produits'),
    ('76', 'Reprises de provisions'),
    ('77', 'Revenus financiers et produits assimiles'),
    ('78', 'Transferts de charges'),
    ('79', 'Reprises d amortissements et provisions'),

    ('8', 'Autres charges et autres produits'),
    ('81', 'Valeurs comptables des cessions d immobilisations'),
    ('82', 'Produits des cessions d immobilisations'),
    ('83', 'Charges hors activites ordinaires'),
    ('84', 'Produits hors activites ordinaires'),
    ('85', 'Dotations hors activites ordinaires'),
    ('86', 'Reprises hors activites ordinaires'),
    ('87', 'Participations des travailleurs'),
    ('88', 'Subventions d equilibre'),
    ('89', 'Impot sur le resultat hors activites ordinaires'),
]


TYPE_BY_CLASS = {
    '1': 'Passif',
    '2': 'Actif',
    '3': 'Actif',
    '4': 'Passif',
    '5': 'Actif',
    '6': 'Charge',
    '7': 'Produit',
    '8': 'Resultat',
    '9': 'Resultat',
}


class Command(BaseCommand):
    help = 'Charge le plan comptable SYSCOHADA revise dans PlanComptable pour une societe donnee.'

    def add_arguments(self, parser):
        parser.add_argument('--societe-id', type=int, required=True, help='ID de la societe cible')
        parser.add_argument('--dry-run', action='store_true', help='Affiche les operations sans ecrire en base')
        parser.add_argument('--reset', action='store_true', help='Supprime le plan existant de la societe avant rechargement')

    @staticmethod
    def _format_account_code(numero):
        """Format demande: base 4 caracteres puis suffixe 00 => 6 caracteres."""
        numero = (numero or '').strip()
        base4 = numero.zfill(4)
        return f'{base4}00'

    @transaction.atomic
    def handle(self, *args, **options):
        societe_id = options['societe_id']
        dry_run = options['dry_run']
        reset = options['reset']

        try:
            societe = Societe.objects.get(pk=societe_id)
        except Societe.DoesNotExist as exc:
            raise CommandError(f'Societe introuvable: id={societe_id}') from exc

        created_count = 0
        updated_count = 0

        if reset:
            deleted = PlanComptable.objects.filter(societe=societe).count()
            if not dry_run:
                PlanComptable.objects.filter(societe=societe).delete()
            self.stdout.write(self.style.WARNING(f'Reset actif: {deleted} comptes supprimes pour la societe {societe.id}.'))

        original_to_formatted = {numero: self._format_account_code(numero) for numero, _ in SYSCOHADA_REVISE_ACCOUNTS}

        # 1) Creation / mise a jour des comptes sans parent
        for numero, nom in SYSCOHADA_REVISE_ACCOUNTS:
            numero_formate = original_to_formatted[numero]
            existing = PlanComptable.objects.filter(societe=societe, numero_compte=numero_formate).first()
            classe = int(numero[0]) if numero else 0
            type_compte = TYPE_BY_CLASS.get(numero[0], 'Resultat')

            payload = {
                'societe': societe,
                'nom_compte': nom,
                'type_compte': type_compte,
                'classe': classe,
                'actif': True,
            }

            if existing:
                changed = False
                for key, value in payload.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed = True
                if changed and not dry_run:
                    existing.save()
                if changed:
                    updated_count += 1
            else:
                if not dry_run:
                    PlanComptable.objects.create(numero_compte=numero_formate, **payload)
                created_count += 1

        # 2) Liaison des parents (plus long prefixe existant)
        comptes = {c.numero_compte: c for c in PlanComptable.objects.filter(societe=societe)}
        for numero, _ in SYSCOHADA_REVISE_ACCOUNTS:
            numero_formate = original_to_formatted[numero]
            compte = comptes.get(numero_formate)
            if not compte:
                continue

            parent_original = None
            parent = None
            for i in range(len(numero) - 1, 0, -1):
                prefix = numero[:i]
                if prefix in original_to_formatted:
                    parent_original = prefix
                    break
            if parent_original:
                parent = comptes.get(original_to_formatted[parent_original])
            if compte.compte_parent_id != (parent.id if parent else None):
                if not dry_run:
                    compte.compte_parent = parent
                    compte.save(update_fields=['compte_parent'])

        if dry_run:
            transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f'SYSCOHADA revise charge pour {societe.raison_sociale} (id={societe.id}) - '
            f'crees={created_count}, maj={updated_count}, dry_run={dry_run}'
        ))
