

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profileID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('noAccount', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('accountID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account_name', models.TextField()),
                ('available_bal', models.FloatField(default=0)),
                ('has_trans', models.BooleanField(null=True)),
                ('last_trans', models.DateField(null=True)),
                ('no_transac', models.IntegerField(default=0)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.Profile')),

            ],
        ),
    ]
