# Generated by Django 2.0.3 on 2018-04-03 13:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='дата создания')),
                ('unlisted', models.BooleanField(db_index=True, default=False, verbose_name='скрыта')),
                ('date_deleted', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата удаления')),
                ('title', models.TextField(verbose_name='название')),
                ('latitude', models.FloatField(db_index=True)),
                ('longitude', models.FloatField(db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'точка',
                'verbose_name_plural': 'точки',
            },
        ),
    ]