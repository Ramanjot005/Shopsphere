# Generated by Django 5.2.1 on 2025-05-17 09:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_review_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='store.product'),
        ),
    ]
