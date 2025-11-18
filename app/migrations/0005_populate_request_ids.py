# Generated manually

from django.db import migrations


def populate_request_ids(apps, schema_editor):
    Request = apps.get_model('app', 'Request')
    requests = Request.objects.all().order_by('id')
    
    for index, request in enumerate(requests, start=1):
        request.request_id = f"{index:05d}"
        request.save(update_fields=['request_id'])


def reverse_populate_request_ids(apps, schema_editor):
    Request = apps.get_model('app', 'Request')
    Request.objects.all().update(request_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_request_cost_benefit_request_ease_of_implementation_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_request_ids, reverse_populate_request_ids),
    ]

