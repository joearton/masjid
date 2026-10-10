from django.db import migrations

APPS_MODELS = [('display', 'displaysettings'), ('display', 'displayslide')]


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    group, _ = Group.objects.get_or_create(name='Operator Display')
    for app_label, model in APPS_MODELS:
        ct, _ = ContentType.objects.get_or_create(app_label=app_label, model=model)
        for action in ('add', 'change', 'delete', 'view'):
            perm, _ = Permission.objects.get_or_create(
                content_type=ct, codename=f'{action}_{model}', defaults={'name': f'Can {action} {model}'})
            group.permissions.add(perm)


def remove_group(apps, schema_editor):
    apps.get_model('auth', 'Group').objects.filter(name='Operator Display').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_create_sitesetting'),
        ('display', '0007_suara_lembut'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    operations = [migrations.RunPython(create_group, remove_group)]
