

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QAManagement', '0004_auto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questioncount',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='usermining',
            options={'managed': False},
        ),
    ]
