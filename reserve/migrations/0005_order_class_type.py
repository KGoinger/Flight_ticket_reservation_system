# Generated by Django 4.2.7 on 2023-12-14 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve', '0004_rename_book_sum_flight_economy_class_book_sum_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='class_type',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
