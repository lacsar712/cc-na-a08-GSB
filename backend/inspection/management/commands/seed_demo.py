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
        samples = [
            ("LH-01", 1400, 1200, 0.4, 30, 3),
            ("LH-09", 800, 1200, 0.2, 20, 4),
        ]
        for code, measured, required, bearing, flash_rate, period in samples:
            verdict, note = judge(measured, required, bearing, period)
            Inspection.objects.create(
                aid_code=code,
                measured_cd=measured,
                required_cd=required,
                bearing_error_deg=bearing,
                flash_rate_fpm=flash_rate,
                period_sec=period,
                verdict=verdict,
                note=note,
                created_by="keeper",
            )
        self.stdout.write("seeded")
