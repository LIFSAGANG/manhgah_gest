from django.db import connection, migrations


def add_missing_fields(apps, schema_editor):
    with connection.cursor() as cursor:
        def has_column(table_name, column_name):
            cursor.execute(f'PRAGMA table_info({table_name})')
            return any(row[1] == column_name for row in cursor.fetchall())

        columns_by_table = {
            'core_client': {
                'societe_id': 'bigint',
                'code_client': 'varchar(50)',
                'type_client': 'varchar(20)',
                'raison_sociale': 'varchar(200)',
                'prenom': 'varchar(100)',
                'code_postal': 'varchar(20)',
                'numero_fiscal': 'varchar(50)',
                'condition_paiement': 'varchar(50)',
                'limite_credit': 'decimal(12,2)',
                'date_creation': 'datetime',
                'date_modification': 'datetime',
            },
            'core_fournisseur': {
                'societe_id': 'bigint',
                'code_fournisseur': 'varchar(50)',
                'raison_sociale': 'varchar(200)',
                'code_postal': 'varchar(20)',
                'numero_fiscal': 'varchar(50)',
                'condition_paiement': 'varchar(50)',
                'date_creation': 'datetime',
                'date_modification': 'datetime',
            },
        }

        for table_name, columns in columns_by_table.items():
            for column_name, sql_definition in columns.items():
                if not has_column(table_name, column_name):
                    schema_editor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}')

    Client = apps.get_model('core', 'Client')
    Fournisseur = apps.get_model('core', 'Fournisseur')

    for client in Client.objects.all():
        if not client.code_client and client.code:
            client.code_client = client.code
        if not client.raison_sociale and client.nom:
            client.raison_sociale = client.nom
        client.save(update_fields=['code_client', 'raison_sociale'])

    for fournisseur in Fournisseur.objects.all():
        if not fournisseur.code_fournisseur and fournisseur.code:
            fournisseur.code_fournisseur = fournisseur.code
        if not fournisseur.raison_sociale and fournisseur.nom:
            fournisseur.raison_sociale = fournisseur.nom
        fournisseur.save(update_fields=['code_fournisseur', 'raison_sociale'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_add_module_permissions'),
    ]

    operations = [
        migrations.RunPython(add_missing_fields, migrations.RunPython.noop),
    ]
