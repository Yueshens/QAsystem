

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QAManagement', '0005_auto'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='questioncount',
            table='QAManagement_questioncount',
        ),
        migrations.AlterModelTable(
            name='user',
            table='QAManagement_user',
        ),
        migrations.AlterModelTable(
            name='usermining',
            table='QAManagement_usermining',
        ),
    ]
