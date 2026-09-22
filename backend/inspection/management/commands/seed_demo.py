from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from inspection.models import Inspection
from inspection.rules import judge


class Command(BaseCommand):
    help = "seed two inspections and two accounts"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="inspector")
        keeper, created = User.objects.get_or_create(username="keeper")
        if created or not keeper.check_password("light123456"):
            keeper.set_password("light123456")
            keeper.save()
        keeper.groups.add(group)
        watch, created = User.objects.get_or_create(username="watch")
        if created or not watch.check_password("watch123456"):
            watch.set_password("watch123456")
            watch.save()
        watch.groups.remove(group)
        if Inspection.objects.exists():
            self.stdout.write("already seeded")
            return
        # 编号, 实测光强, 要求光强, 方位偏差, 每分钟闪次, 周期秒
        samples = [
            ("LH-01", 1400, 1200, 0.4, 20, 6),
            ("LH-09", 800, 1200, 0.2, 20, 6),
        ]
        for code, measured, required, bearing, flash, period in samples:
            verdict, note, _ = judge(measured, required, bearing, period)
            Inspection.objects.create(
                aid_code=code,
                measured_cd=measured,
                required_cd=required,
                bearing_error_deg=bearing,
                flash_per_min=flash,
                period_sec=period,
                verdict=verdict,
                note=note,
                created_by="keeper",
            )
        self.stdout.write("seeded")
