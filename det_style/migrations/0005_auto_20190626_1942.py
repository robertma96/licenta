# Generated by Django 2.2 on 2019-06-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('det_style', '0004_auto_20190626_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paintings',
            name='author',
            field=models.CharField(default='Author', max_length=50),
        ),
        migrations.AlterField(
            model_name='paintings',
            name='name',
            field=models.CharField(max_length=45),
        ),
    ]
