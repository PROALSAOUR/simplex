from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0002_alter_city_active_alter_city_name_and_more'),
        ('accounts', '0016_alter_store_location_alter_store_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='location',
        ),
        migrations.AddField(
            model_name='store',
            name='location',
            field=models.ForeignKey(
                to='admins.city',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                blank=True,
                verbose_name='الموقع',
                help_text='قم بإدخال موقع المتجر الخاص بك',
            ),
        ),
    ]