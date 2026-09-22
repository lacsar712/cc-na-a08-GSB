from django.db import models


class Inspection(models.Model):
    aid_code = models.CharField("航标编号", max_length=40)
    measured_cd = models.FloatField("实测光强")
    required_cd = models.FloatField("要求光强")
    bearing_error_deg = models.FloatField("方位偏差")
    flash_rate_fpm = models.FloatField("每分钟闪次", default=0)
    period_sec = models.FloatField("周期秒", default=0)
    verdict = models.CharField("结论", max_length=20)
    note = models.CharField("说明", max_length=200)
    created_by = models.CharField("登记人", max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class PeriodGateLog(models.Model):
    """周期门禁册：每次因周期触雷的登记留一行快照，改正实测不回改旧行。"""

    inspection = models.ForeignKey(
        Inspection, on_delete=models.CASCADE, related_name="gate_logs"
    )
    aid_code = models.CharField("航标编号", max_length=40)
    flash_rate_fpm = models.FloatField("每分钟闪次")
    period_sec = models.FloatField("周期秒")
    verdict = models.CharField("当时判词", max_length=20)
    note = models.CharField("说明原文", max_length=200)
    created_by = models.CharField("登记人", max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
