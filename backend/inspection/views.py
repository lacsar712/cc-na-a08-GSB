from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from inspection.models import Inspection, PeriodGateLog
from inspection.rules import judge


def _can_write(user) -> bool:
    return user.groups.filter(name="inspector").exists()


def _parse_form(post):
    """从表单解析五项实测值，失败抛 ValueError。"""
    try:
        return {
            "aid_code": post["aid_code"].strip(),
            "measured_cd": float(post["measured_cd"]),
            "required_cd": float(post["required_cd"]),
            "bearing_error_deg": float(post["bearing_error_deg"]),
            "flash_per_min": float(post["flash_per_min"]),
            "period_sec": float(post["period_sec"]),
        }
    except (KeyError, ValueError):
        raise ValueError("bad input")


def _log_period_gate(row, values, verdict, note, username):
    """周期触雷时向门禁册追加一行快照；旧册行不动。"""
    PeriodGateLog.objects.create(
        inspection=row,
        aid_code=values["aid_code"],
        flash_per_min=values["flash_per_min"],
        period_sec=values["period_sec"],
        verdict=verdict,
        note=note,
        logged_by=username,
    )


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
    return render(
        request,
        "detail.html",
        {"row": row, "can_write": _can_write(request.user)},
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_view(request):
    if not _can_write(request.user):
        return HttpResponseForbidden("仅巡检员可登记灯光巡检")
    error = ""
    if request.method == "POST":
        try:
            values = _parse_form(request.POST)
            if not values["aid_code"]:
                raise ValueError("empty")
        except ValueError:
            error = "请填编号和五项数值"
        else:
            verdict, note, period_bad = judge(
                values["measured_cd"],
                values["required_cd"],
                values["bearing_error_deg"],
                values["period_sec"],
            )
            row = Inspection.objects.create(
                aid_code=values["aid_code"],
                measured_cd=values["measured_cd"],
                required_cd=values["required_cd"],
                bearing_error_deg=values["bearing_error_deg"],
                flash_per_min=values["flash_per_min"],
                period_sec=values["period_sec"],
                verdict=verdict,
                note=note,
                created_by=request.user.username,
            )
            if period_bad:
                _log_period_gate(row, values, verdict, note, request.user.username)
            return redirect("detail", pk=row.pk)
    return render(request, "form.html", {"error": error})


@login_required
@require_http_methods(["GET", "POST"])
def edit_view(request, pk):
    """改正实测：覆盖本条记录并重新判定；再次周期触雷则追加新册行，旧册行不动。"""
    if not _can_write(request.user):
        return HttpResponseForbidden("仅巡检员可改正灯光巡检记录")
    row = get_object_or_404(Inspection, pk=pk)
    error = ""
    if request.method == "POST":
        try:
            values = _parse_form(request.POST)
            if not values["aid_code"]:
                raise ValueError("empty")
        except ValueError:
            error = "请填编号和五项数值"
        else:
            verdict, note, period_bad = judge(
                values["measured_cd"],
                values["required_cd"],
                values["bearing_error_deg"],
                values["period_sec"],
            )
            row.aid_code = values["aid_code"]
            row.measured_cd = values["measured_cd"]
            row.required_cd = values["required_cd"]
            row.bearing_error_deg = values["bearing_error_deg"]
            row.flash_per_min = values["flash_per_min"]
            row.period_sec = values["period_sec"]
            row.verdict = verdict
            row.note = note
            row.save()
            if period_bad:
                _log_period_gate(row, values, verdict, note, request.user.username)
            return redirect("detail", pk=row.pk)
    return render(request, "form.html", {"error": error, "row": row})


@login_required
def gate_ledger_view(request):
    """周期门禁册：仅巡检员可查看。"""
    if not _can_write(request.user):
        return HttpResponseForbidden("仅巡检员可查看周期门禁册")
    logs = PeriodGateLog.objects.select_related("inspection").all()
    return render(request, "gate_ledger.html", {"logs": logs})
