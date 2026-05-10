# Generated manually for linking order items to their parent order.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oredritem',
            name='order',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='orders.order',
                verbose_name='الطلب',
            ),
            preserve_default=False,
        ),
    ]
