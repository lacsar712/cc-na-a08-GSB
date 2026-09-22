from django.db import models


class Inspection(models.Model):
    aid_code = models.CharField("航标编号", max_length=40)
    measured_cd = models.FloatField("实测光强")
    required_cd = models.FloatField("要求光强")
    bearing_error_deg = models.FloatField("方位偏差")
    flash_per_min = models.FloatField("每分钟闪次", default=0)
    period_sec = models.FloatField("周期秒", default=0)
    verdict = models.CharField("结论", max_length=20)
    note = models.CharField("说明", max_length=200)
    created_by = models.CharField("登记人", max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class PeriodGateLog(models.Model):
    """周期门禁册：每次登记/改正因周期触雷即追加一行，旧册行永不改动。"""

    inspection = models.ForeignKey(
        Inspection, on_delete=models.CASCADE, related_name="period_gate_logs"
    )
    aid_code = models.CharField("航标编号", max_length=40)
    flash_per_min = models.FloatField("每分钟闪次")
    period_sec = models.FloatField("周期秒")
    verdict = models.CharField("当时判词", max_length=20)
    note = models.CharField("说明原文", max_length=200)
    logged_by = models.CharField("登记人", max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
