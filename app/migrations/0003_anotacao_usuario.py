import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_metadiaria_options_metadiaria_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='anotacao',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.usuario', verbose_name='Usuário'),
        ),
    ]
