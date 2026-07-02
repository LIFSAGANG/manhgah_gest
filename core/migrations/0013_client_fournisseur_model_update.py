from django.db import connection, migrations


def add_missing_fields(apps, schema_editor):
    with connection.cursor() as cursor:
        columns_by_table = {
            'core_client': {col['name'] for col in connection.introspection.get_columns(cursor, 'core_client')},
            'core_fournisseur': {col['name'] for col in connection.introspection.get_columns(cursor, 'core_fournisseur')},
        }

        for table_name, columns in columns_by_table.items():
            if table_name == 'core_client':
                for column_name, sql_definition in {
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
                }.items():
                    if column_name not in columns:
                        schema_editor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}')
            else:
                for column_name, sql_definition in {
                    'code_fournisseur': 'varchar(50)',
                    'raison_sociale': 'varchar(200)',
                    'code_postal': 'varchar(20)',
                    'numero_fiscal': 'varchar(50)',
                    'condition_paiement': 'varchar(50)',
                    'date_creation': 'datetime',
                    'date_modification': 'datetime',
                }.items():
                    if column_name not in columns:
                        schema_editor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_add_module_permissions'),
    ]

    operations = [
        migrations.RunPython(add_missing_fields, migrations.RunPython.noop),
    ]
