# Generated manually to preserve existing Projet data while aligning schema.

import datetime

import django.db.models.deletion
from django.db import migrations, models


def fill_missing_project_start_dates(apps, schema_editor):
    Projet = apps.get_model('core', 'Projet')
    Projet.objects.filter(date_debut__isnull=True).update(date_debut=datetime.date.today())


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_achat_projet_achat_type_achat_facture_projet_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projet',
            old_name='code',
            new_name='reference_projet',
        ),
        migrations.RenameField(
            model_name='projet',
            old_name='nom',
            new_name='libelle_projet',
        ),
        migrations.RenameField(
            model_name='projet',
            old_name='date_fin',
            new_name='date_fin_prevue',
        ),
        migrations.RenameField(
            model_name='projet',
            old_name='budget',
            new_name='budget_previsionnel',
        ),
        migrations.AddField(
            model_name='projet',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.client', verbose_name='Client'),
        ),
        migrations.AddField(
            model_name='projet',
            name='date_fin_reelle',
            field=models.DateField(blank=True, null=True, verbose_name='Date de fin réelle'),
        ),
        migrations.AddField(
            model_name='projet',
            name='montant_ht',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Montant HT'),
        ),
        migrations.AddField(
            model_name='projet',
            name='montant_ttc',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Montant TTC'),
        ),
        migrations.AddField(
            model_name='projet',
            name='montant_tva',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Montant TVA'),
        ),
        migrations.AddField(
            model_name='projet',
            name='responsable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.utilisateurprofile', verbose_name='Responsable'),
        ),
        migrations.AddField(
            model_name='projet',
            name='statut_projet',
            field=models.CharField(choices=[('EnCours', 'EnCours'), ('Termine', 'Termine'), ('Suspendu', 'Suspendu'), ('Annule', 'Annule')], default='EnCours', max_length=20, verbose_name='Statut projet'),
        ),
        migrations.AddField(
            model_name='projet',
            name='type_projet',
            field=models.CharField(choices=[('Interne', 'Interne'), ('Externe', 'Externe'), ('Vente', 'Vente'), ('Service', 'Service')], default='Externe', max_length=20, verbose_name='Type projet'),
        ),
        migrations.RunPython(fill_missing_project_start_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='projet',
            name='date_debut',
            field=models.DateField(verbose_name='Date de début'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='type_vente',
            field=models.CharField(choices=[('Produit', 'Produit'), ('Service', 'Service'), ('Travaux', 'Travaux')], default='Produit', max_length=20, verbose_name='Type vente'),
        ),
        migrations.AlterModelOptions(
            name='projet',
            options={'ordering': ['libelle_projet'], 'verbose_name': 'Projet', 'verbose_name_plural': 'Projets'},
        ),
        migrations.AddIndex(
            model_name='projet',
            index=models.Index(fields=['societe'], name='core_projet_soc_idx'),
        ),
        migrations.AddIndex(
            model_name='projet',
            index=models.Index(fields=['client'], name='core_projet_cli_idx'),
        ),
        migrations.AddIndex(
            model_name='projet',
            index=models.Index(fields=['statut_projet'], name='core_projet_sta_idx'),
        ),
    ]
