PERIOD_MIN_SEC = 2
PERIOD_MAX_SEC = 10


def _fmt_sec(value: float):
    """1.0 -> '1'，非整数保留原值。"""
    return str(int(value)) if float(value).is_integer() else str(value)


def judge(
    measured_cd: float,
    required_cd: float,
    bearing_error_deg: float,
    period_sec: float,
) -> tuple[str, str, bool]:
    """返回（结论, 说明, 周期是否触雷）。

    周期秒须在 2~10 之间才放行。周期单独触雷时结论写作“周期不合”；
    与光强不足或方位越限同时出现时，结论为“不合格”，说明中两件事都保留。
    """
    problems = []
    if measured_cd < required_cd:
        problems.append("光强不足")
    if abs(bearing_error_deg) > 2:
        problems.append("方位偏差过大")
    period_bad = not (PERIOD_MIN_SEC <= period_sec <= PERIOD_MAX_SEC)
    if period_bad:
        problems.append(
            f"周期{_fmt_sec(period_sec)}秒不合（允许{PERIOD_MIN_SEC}至{PERIOD_MAX_SEC}秒）"
        )
    if not problems:
        return "合格", "光强、方位与周期均在限内", False
    if len(problems) == 1 and period_bad:
        return "周期不合", problems[0], True
    return "不合格", "；".join(problems), period_bad
