PERIOD_MIN_SEC = 2
PERIOD_MAX_SEC = 10


def judge(
    measured_cd: float,
    required_cd: float,
    bearing_error_deg: float,
    period_sec: float,
) -> tuple[str, str]:
    """返回（结论, 说明）。周期秒不在 2~10 之间时参与放行判定。"""
    other_faults = []
    if measured_cd < required_cd:
        other_faults.append("光强不足")
    if abs(bearing_error_deg) > 2:
        other_faults.append("方位偏差过大")

    period_bad = not (PERIOD_MIN_SEC <= period_sec <= PERIOD_MAX_SEC)

    if not other_faults and not period_bad:
        return "合格", "光强、方位与周期均在限内"

    if period_bad:
        period_reason = f"周期不合（周期{sec_label(period_sec)}秒，应在2至10秒之间）"
        # 只有周期问题时结论写作“周期不合”；光强或方位同时触雷时两类原因都留下
        if not other_faults:
            return "周期不合", period_reason
        return "不合格", "；".join(other_faults + [period_reason])

    return "不合格", "；".join(other_faults)


def sec_label(value: float) -> str:
    """整数秒不带小数点，如 1.0 -> '1'。"""
    return str(int(value)) if float(value).is_integer() else str(value)
