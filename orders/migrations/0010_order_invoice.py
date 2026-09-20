# Migration لتجاوز العلاقة القديمة مع management.Recipe

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_rename_oredritem_orderitem'),
    ]

    operations = [
    ]