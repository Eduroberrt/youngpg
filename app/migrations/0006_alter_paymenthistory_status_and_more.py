# Generated by Django 5.1.4 on 2025-07-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_product_description_paymentpointtransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthistory',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], default='Pending', max_length=20),
        ),
        migrations.DeleteModel(
            name='PaymentPointTransaction',
        ),
    ]
