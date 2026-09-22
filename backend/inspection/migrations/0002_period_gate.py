import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspection",
            name="flash_rate_fpm",
            field=models.FloatField(default=0, verbose_name="每分钟闪次"),
        ),
        migrations.AddField(
            model_name="inspection",
            name="period_sec",
            field=models.FloatField(default=0, verbose_name="周期秒"),
        ),
        migrations.CreateModel(
            name="PeriodGateLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("aid_code", models.CharField(max_length=40, verbose_name="航标编号")),
                ("flash_rate_fpm", models.FloatField(verbose_name="每分钟闪次")),
                ("period_sec", models.FloatField(verbose_name="周期秒")),
                ("verdict", models.CharField(max_length=20, verbose_name="当时判词")),
                ("note", models.CharField(max_length=200, verbose_name="说明原文")),
                ("created_by", models.CharField(max_length=64, verbose_name="登记人")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "inspection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gate_logs",
                        to="inspection.inspection",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
    ]
