# Generated by Django 5.0.3 on 2024-11-19 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0005_alter_company_user_alter_customer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default='Cash on Delivery', max_length=50),
        ),
    ]
