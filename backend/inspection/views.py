from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from inspection.models import Inspection, PeriodGateLog
from inspection.rules import PERIOD_MAX_SEC, PERIOD_MIN_SEC, judge


def _can_write(user) -> bool:
    return user.groups.filter(name="inspector").exists()


def health(_request):
    from django.http import JsonResponse

    return JsonResponse({"status": "ok", "service": "nav-aid-inspection"})


@require_http_methods(["GET", "POST"])
def login_view(request):
    from django.contrib.auth import authenticate, login

    error = ""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        if user is None:
            error = "用户名或密码错误"
        else:
            login(request, user)
            return redirect("list")
    return render(request, "login.html", {"error": error})


def logout_view(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect("login")


@login_required
def list_view(request):
    rows = Inspection.objects.all()
    return render(request, "list.html", {"rows": rows, "can_write": _can_write(request.user)})


@login_required
def detail_view(request, pk):
    row = get_object_or_404(Inspection, pk=pk)
    return render(request, "detail.html", {"row": row, "can_write": _can_write(request.user)})


def _parse_form(post):
    code = post.get("aid_code", "").strip()
    if not code:
        raise ValueError("empty")
    return {
        "aid_code": code,
        "measured_cd": float(post["measured_cd"]),
        "required_cd": float(post["required_cd"]),
        "bearing_error_deg": float(post["bearing_error_deg"]),
        "flash_rate_fpm": float(post["flash_rate_fpm"]),
        "period_sec": float(post["period_sec"]),
    }


def _period_out_of_range(period_sec: float) -> bool:
    return not (PERIOD_MIN_SEC <= period_sec <= PERIOD_MAX_SEC)


def _append_gate_log(row, verdict, note, username):
    """周期触雷即留快照行；字段取自当时实测，改正不会回改旧行。"""
    PeriodGateLog.objects.create(
        inspection=row,
        aid_code=row.aid_code,
        flash_rate_fpm=row.flash_rate_fpm,
        period_sec=row.period_sec,
        verdict=verdict,
        note=note,
        created_by=username,
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_view(request):
    if not _can_write(request.user):
        return HttpResponseForbidden("仅巡检员可登记灯光巡检")
    error = ""
    if request.method == "POST":
        try:
            data = _parse_form(request.POST)
        except (KeyError, ValueError):
            error = "请填编号和五项数值"
        else:
            verdict, note = judge(
                data["measured_cd"],
                data["required_cd"],
                data["bearing_error_deg"],
                data["period_sec"],
            )
            row = Inspection.objects.create(
                verdict=verdict,
                note=note,
                created_by=request.user.username,
                **data,
            )
            if _period_out_of_range(data["period_sec"]):
                _append_gate_log(row, verdict, note, request.user.username)
            return redirect("detail", pk=row.pk)
    return render(request, "form.html", {"error": error, "row": None})


@login_required
@require_http_methods(["GET", "POST"])
def edit_view(request, pk):
    if not _can_write(request.user):
        return HttpResponseForbidden("仅巡检员可改正灯光巡检")
    row = get_object_or_404(Inspection, pk=pk)
    error = ""
    if request.method == "POST":
        try:
            data = _parse_form(request.POST)
        except (KeyError, ValueError):
            error = "请填编号和五项数值"
        else:
            verdict, note = judge(
                data["measured_cd"],
                data["required_cd"],
                data["bearing_error_deg"],
                data["period_sec"],
            )
            for key, value in data.items():
                setattr(row, key, value)
            row.verdict = verdict
            row.note = note
            row.save()
            # 改正后仍因周期触雷，再追加一行新册；旧册行保持不动
            if _period_out_of_range(data["period_sec"]):
                _append_gate_log(row, verdict, note, request.user.username)
            return redirect("detail", pk=row.pk)
    return render(request, "form.html", {"error": error, "row": row})


@login_required
def gate_log_view(request):
    logs = PeriodGateLog.objects.all()
    return render(request, "gate_log.html", {"logs": logs})
