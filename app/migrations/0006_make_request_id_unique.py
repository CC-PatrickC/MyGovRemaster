# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_populate_request_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='request_id',
            field=models.CharField(blank=True, editable=False, max_length=5, unique=True),
        ),
    ]

