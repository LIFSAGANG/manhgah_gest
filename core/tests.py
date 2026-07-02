from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Client, Fournisseur, Societe


class ClientFournisseurModelTests(TestCase):
    def setUp(self):
        self.societe = Societe.objects.create(
            code_societe='SOC-TEST',
            raison_sociale='Société test',
        )

    def test_client_uses_new_default_fields(self):
        client = Client.objects.create(
            societe=self.societe,
            code_client='CLI-001',
            raison_sociale='Entreprise Test',
            nom='Durand',
            prenom='Jean',
        )

        self.assertEqual(client.type_client, 'Particulier')
        self.assertEqual(client.limite_credit, 0)
        self.assertTrue(client.actif)
        self.assertEqual(client.code, 'CLI-001')

    def test_fournisseur_requires_raison_sociale(self):
        fournisseur = Fournisseur(
            societe=self.societe,
            code_fournisseur='FRS-001',
        )

        with self.assertRaises(ValidationError):
            fournisseur.full_clean()
