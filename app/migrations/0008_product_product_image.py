# Generated by Django 4.0 on 2022-01-07 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_product_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_image',
            field=models.ImageField(null=True, upload_to='producting'),
        ),
    ]
