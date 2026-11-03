#!/usr/bin/env python3
"""Cross-domain analysis engine for full-profile reports.

Consumes the unified NormalizedData from mcp_orchestration and produces
cross-dimensional insights that NO single atomic skill can generate on its own:

  1. 创新实力       — 专利 + 商标（数量与质量）
  2. 风险健康度     — 处罚/异常/限高/违法 倒扣
  3. 工商基础       — 实缴率 + 规模 + 成立年限
  4. 市场活跃度     — 招投标参与 + 中标统计
  5. 经营状况       — 融资 + 规模 + 趋势
  6. 舆情可见度     — 舆情声量 + 情感分布
  7. 品牌商标       — 商标覆盖 + 类别分布
  8. 人才储备       — 招聘活跃度 + 薪酬 + 福利

All evidence is grounded in actual data; missing dimensions are skipped (never
fabricated).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Mapping, Optional


# --------------------------------------------------------------------------- #
# Tolerant field extraction (handles both live MCP and cached report shapes)
# --------------------------------------------------------------------------- #
def source_ratio_percent(value: Any) -> Optional[Decimal]:
    """Return a percentage as Decimal without rounding; None when unavailable.

    Accepts a 0-1 fraction, an already-percent number, a '12.3456%' string,
    or a dict. Zero is a real value; only missing/invalid input returns None.
    """
    if isinstance(value, dict):
        value = value.get("value", value.get("ratio", value.get("percent")))
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text or text in {"-", "—"}:
        return None
    if "%" in text:
        text = text.replace("%", "").strip()
    try:
        number = Decimal(text)
    except InvalidOperation:
        return None
    if number != 0 and abs(number) <= 1:
        number *= 100
    return number


def format_source_ratio(value: Any) -> str:
    """Render an upstream ratio without rounding, zero-padding, or unit guessing.

    A percent string such as '12.3400%' is returned verbatim. Numeric 0-1
    fractions keep their original significant digits (0.123456 -> 12.3456%).
    Zero renders as '0%'; missing or invalid values render as '-'.
    """
    if isinstance(value, dict):
        value = value.get("value", value.get("ratio", value.get("percent")))
    if value is None:
        return "-"
    text = str(value).strip()
    if not text or text in {"-", "—"}:
        return "-"
    if "%" in text:
        return text
    number = source_ratio_percent(value)
    if number is None:
        return text
    return f"{format(number.normalize(), 'f')}%"


def _pick(d: Any, *keys: str) -> Any:
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if v not in (None, "", "-", []):
            return v
    return None


def _f(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(
            str(value)
            .replace(",", "")
            .replace("万", "")
            .replace("%", "")
            .replace("亿", "")
        )
    except (TypeError, ValueError):
        return None


def _i(value: Any) -> Optional[int]:
    f = _f(value)
    return int(f) if f is not None else None


def _ratio_pct(value: Any) -> Optional[float]:
    """Parse '67%' / '0.67' / 67 into a 0-100 percentage."""
    if value is None:
        return None
    s = str(value).strip()
    if "%" in s:
        try:
            return float(s.replace("%", "").strip())
        except ValueError:
            return None
    f = _f(value)
    if f is None:
        return None
    return f * 100 if f <= 1 else f


# --------------------------------------------------------------------------- #
# Data accessors
# --------------------------------------------------------------------------- #
def _holders(data: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    return list(data.get("enterprise", {}).get("holders") or [])


def _investments(data: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    return list(data.get("enterprise", {}).get("investments") or [])


def _base(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("enterprise", {}).get("base") or {})


def _risk(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("risk") or {})


def _litigation(data: Mapping[str, Any]) -> Dict[str, Any]:
    lit = _risk(data).get("litigation") or {}
    return lit if isinstance(lit, dict) else {}


def _litigation_summary(data: Mapping[str, Any]) -> Dict[str, Any]:
    risk = _risk(data)
    lit = _litigation(data)
    hearings = _i(risk.get("court_hearings_total"))
    executed = _i(risk.get("restrictions_total"))
    case_count = _i(lit.get("case_count") or lit.get("caseCount"))
    defendant = _i(lit.get("as_defendant") or lit.get("asDefendant"))
    plaintiff = _i(lit.get("as_plaintiff") or lit.get("asPlaintiff"))
    announcements = _i(lit.get("法院公告数"))
    judgments = _i(lit.get("裁判文书数"))
    dishonest = _i(lit.get("失信被执行人数"))
    known = any(
        v is not None and v > 0
        for v in (
            hearings,
            executed,
            case_count,
            defendant,
            plaintiff,
            announcements,
            judgments,
            dishonest,
        )
    ) or bool(risk.get("level"))
    if not known:
        return {
            "case_count": None,
            "as_defendant": None,
            "as_plaintiff": None,
            "hearings": None,
            "announcements": None,
            "judgments": None,
            "executed": None,
            "dishonest": None,
            "has_role_detail": False,
        }
    if case_count is None:
        case_count = hearings
    return {
        "case_count": case_count,
        "as_defendant": defendant,
        "as_plaintiff": plaintiff,
        "hearings": hearings,
        "announcements": announcements,
        "judgments": judgments,
        "executed": executed,
        "dishonest": dishonest,
        "has_role_detail": defendant is not None or plaintiff is not None,
    }


def _operation(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("operation") or {})


def _patent(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("patent") or {})


def _trademark(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("trademark") or {})


def _bidding(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("bidding") or {})


def _news(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("news") or {})


def _recruitment(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data.get("recruitment") or {})


def _risk_evidence_known(data: Mapping[str, Any]) -> bool:
    """Distinguish an explicitly queried risk result from an empty/failed domain."""
    risk = _risk(data)
    marker = risk.get("_evidence_known")
    if marker is not None:
        return marker is True
    if risk.get("score") is not None or risk.get("level") not in (None, "", "-"):
        return True
    return any(
        risk.get(key) is not None
        for key in (
            "court_hearings_total",
            "restrictions_total",
            "penalties_total",
            "anomalies_total",
        )
    )


# --------------------------------------------------------------------------- #
# Specialty scores (each 0-100, or None if data unavailable)
# --------------------------------------------------------------------------- #
def score_innovation_strength(data: Mapping[str, Any]) -> Optional[float]:
    """创新实力: 仅在有专利证据时评估，商标由独立维度承载."""
    patent = _patent(data)
    patent_count = _i(patent.get("patentCount"))
    invention_app = _i(patent.get("inventionAppPatentCount")) or 0
    invention_lic = _i(patent.get("inventionLicPatentCount")) or 0

    if patent_count is None:
        return None

    s = 0.0
    # 专利评分（最高 60 分）
    if invention_lic:
        s += min(30, invention_lic * 6)
    if invention_app:
        s += min(20, invention_app * 4)
    other_patent = patent_count - invention_app - invention_lic
    if other_patent:
        s += min(10, other_patent * 2)

    return round(max(0, min(100, s)), 1)


def score_risk_health(data: Mapping[str, Any]) -> Optional[float]:
    if not _risk_evidence_known(data):
        return None
    risk = _risk(data)
    hearings = _i(risk.get("court_hearings_total"))
    restrictions = _i(risk.get("restrictions_total"))
    penalties = _i(risk.get("penalties_total"))
    anomalies = _i(risk.get("anomalies_total"))
    if all(v is None for v in (hearings, restrictions, penalties, anomalies)):
        return None
    exposure = (
        min(60, (hearings or 0) / 5)
        + min(50, (restrictions or 0) * 10)
        + min(30, (penalties or 0) * 10)
        + min(20, (anomalies or 0) * 5)
    )
    return round(max(0, 100 - exposure), 1)


def score_business_foundation(data: Mapping[str, Any]) -> Optional[float]:
    """工商基础: 实缴率 + 规模 + 成立年限."""
    base = _base(data)

    paid_rate = _ratio_pct(_pick(base, "资本实缴率", "实缴率", "paidRate"))
    if paid_rate is None:
        reg = _f(_pick(base, "注册资本", "regCapital", "regCapitalValue"))
        paid = _f(_pick(base, "实缴资本", "realCapital", "paidInCapital"))
        if reg and paid is not None and reg > 0:
            paid_rate = paid / reg * 100

    found_year = _pick(base, "成立日期", "foundTime", "成立时间")
    if found_year:
        try:
            year_int = int(str(found_year)[:4])
            import datetime as _dt

            age = _dt.datetime.now().year - year_int
        except (ValueError, TypeError):
            age = None
    else:
        age = None

    if paid_rate is None and age is None:
        return None

    s = 0.0
    # 实缴率评分（最高 50 分）
    if paid_rate is not None:
        if paid_rate >= 80:
            s += 50
        elif paid_rate >= 50:
            s += 30 + (paid_rate - 50) * 0.67
        elif paid_rate >= 20:
            s += 15 + (paid_rate - 20) * 0.5
        else:
            s += paid_rate * 0.75

    # 成立年限评分（最高 50 分）
    if age is not None:
        if age >= 10:
            s += 50
        elif age >= 5:
            s += 30 + (age - 5) * 4
        elif age >= 3:
            s += 15 + (age - 3) * 7.5
        else:
            s += age * 5

    return round(max(0, min(100, s)), 1)


def score_market_activity(data: Mapping[str, Any]) -> Optional[float]:
    """市场活跃度: 招投标参与 + 中标统计."""
    bidding = _bidding(data)

    bid_total = _i(bidding.get("bidding_total")) or 0
    win_stats = _first_list(bidding.get("winbidStatList"))
    win_count = sum(
        _i(item.get("count")) or 0 for item in win_stats if isinstance(item, dict)
    )

    if bid_total == 0 and win_count == 0:
        return None

    s = 0.0
    # 招投标参与评分（最高 50 分）
    if bid_total:
        s += min(50, bid_total * 5)

    # 中标评分（最高 50 分）
    if win_count:
        s += min(50, win_count * 5)

    return round(max(0, min(100, s)), 1)


def score_operation_status(data: Mapping[str, Any]) -> Optional[float]:
    """经营状况: 融资 + 规模 + 趋势."""
    operation = _operation(data)

    fin_n = _i(operation.get("financing_count")) or 0
    scale = operation.get("scale") or {}
    has_scale = bool(
        _pick(scale, "staff", "人员规模", "enterpriseScale")
        or _pick(scale, "turnover", "年营业额", "annualTurnover")
    )
    trends = operation.get("trends") or {}

    # 趋势信号
    trend_signals = 0
    for k in (
        "isNewFinancingIn3Month",
        "isStaffExpandIn3Month",
        "isFoundSubsidiaryIn3Month",
        "isExpandNewCityIn3Month",
        "isAuthorityListIn6Month",
    ):
        if isinstance(trends, dict) and trends.get(k) == 1:
            trend_signals += 1

    if fin_n == 0 and not has_scale and trend_signals == 0:
        return None

    s = 0
    # 融资评分（最高 40 分）
    s += min(40, fin_n * 10)

    # 规模评分（最高 40 分）
    if has_scale:
        s += 40

    # 趋势评分（最高 20 分）
    s += min(20, trend_signals * 7)

    return round(max(0, min(100, s)), 1)


def score_digital_presence(data: Mapping[str, Any]) -> Optional[float]:
    """舆情可见度: 舆情声量 + 情感分布."""
    news = _news(data)

    sentiment_stats = news.get("newsSentimentStats") or {}
    if not isinstance(sentiment_stats, dict):
        sentiment_stats = {}

    total_news = sum(
        _i(sentiment_stats.get(k)) or 0
        for k in ("neutral", "negative", "positive", "unknown")
    )
    positive_ratio = 0.0
    if total_news > 0:
        pos = _i(sentiment_stats.get("positive")) or 0
        positive_ratio = pos / total_news * 100

    if total_news == 0:
        return None

    s = 0.0
    # 舆情声量评分（最高 60 分）
    if total_news >= 100:
        s += 60
    elif total_news >= 50:
        s += 40 + (total_news - 50) * 0.4
    elif total_news >= 10:
        s += 20 + (total_news - 10) * 0.5
    else:
        s += total_news * 2

    # 正面舆情占比评分（最高 40 分）
    if positive_ratio >= 60:
        s += 40
    elif positive_ratio >= 40:
        s += 25 + (positive_ratio - 40) * 0.75
    elif positive_ratio >= 20:
        s += 10 + (positive_ratio - 20) * 0.75
    else:
        s += positive_ratio * 0.5

    return round(max(0, min(100, s)), 1)


def score_brand_trademark(data: Mapping[str, Any]) -> Optional[float]:
    """品牌商标: 商标覆盖 + 类别分布."""
    trademark = _trademark(data)

    tm_count = _i(trademark.get("tmCount")) or 0
    tm_valid = _i(trademark.get("tmValidNumber")) or 0
    tm_types = _first_list(trademark.get("tmTypeList"))
    type_count = len(tm_types)

    if tm_count == 0:
        return None

    s = 0
    # 商标数量评分（最高 50 分）
    if tm_valid:
        s += min(50, tm_valid * 5)

    # 类别覆盖评分（最高 50 分）
    if type_count:
        s += min(50, type_count * 10)

    return round(max(0, min(100, s)), 1)


def score_talent_reserve(data: Mapping[str, Any]) -> Optional[float]:
    """人才储备: 招聘活跃度 + 薪酬 + 福利."""
    recruitment = _recruitment(data)

    current = _i(recruitment.get("current")) or 0
    last_3m = _i(recruitment.get("last_3m")) or 0
    welfare = recruitment.get("welfare") or []

    if current == 0 and last_3m == 0 and not welfare:
        return None

    s = 0
    # 招聘活跃度评分（最高 60 分）
    if current:
        s += min(35, current * 7)
    if last_3m:
        s += min(25, last_3m * 5)

    # 福利项评分（最高 40 分）
    welfare_count = len(welfare) if isinstance(welfare, list) else 0
    s += min(40, welfare_count * 5)

    return round(max(0, min(100, s)), 1)


def specialty_scores(data: Mapping[str, Any]) -> Dict[str, Any]:
    items = [
        ("innovation_strength", "创新实力", score_innovation_strength(data)),
        ("risk_health", "司法与合规健康度", score_risk_health(data)),
        ("business_foundation", "工商基础", score_business_foundation(data)),
        ("market_activity", "市场活动", score_market_activity(data)),
        ("operation_status", "经营公开线索", score_operation_status(data)),
        ("digital_presence", "舆情可见度", score_digital_presence(data)),
        ("brand_trademark", "品牌商标", score_brand_trademark(data)),
        ("talent_reserve", "人才公开线索", score_talent_reserve(data)),
    ]
    valid = [(key, label, value) for key, label, value in items if value is not None]
    meta = data.get("_meta") or {}
    resolved_meta = meta.get("resolved") or {}
    canon = str(resolved_meta.get("enterprise") or "").strip()
    base = _base(data)
    base_name = str(_pick(base, "企业名称", "name", "名称") or "").strip()
    code = str(
        _pick(base, "统一社会信用代码", "socialCreditCode", "信用代码") or ""
    ).strip()
    subject_ok = (
        base_name not in ("", "-")
        and code not in ("", "-")
        and (not canon or base_name == canon)
    )
    risk = _risk(data)
    hearings = _i(risk.get("court_hearings_total"))
    restrictions = _i(risk.get("restrictions_total"))
    level = str(risk.get("level") or "")
    risk_known = (hearings is not None or restrictions is not None) and bool(
        level or (hearings or 0) > 0 or (restrictions or 0) > 0
    )
    judicial_clear = (
        hearings is not None and hearings < 100 and (restrictions or 0) == 0
    )
    supply_ok = True
    eligible = (
        subject_ok
        and not meta.get("errors")
        and risk_known
        and judicial_clear
        and supply_ok
        and len(valid) >= 5
    )
    avg = (
        round(sum(value for _, _, value in valid) / len(valid), 1) if eligible else None
    )
    return {
        "items": items,
        "valid": valid,
        "average": avg,
        "rating_eligible": eligible,
        "minimum_domains": 5,
        "gate_reason": None if eligible else "主体、关键域或司法风险门禁未满足",
    }


def insight_innovation_market(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """专利与中标公开数量并列，不推断转化或优势."""
    patent = _patent(data)
    bidding = _bidding(data)

    patent_count = _i(patent.get("patentCount"))
    win_stats = _first_list(bidding.get("winbidStatList"))
    win_count = sum(
        _i(item.get("count")) or 0 for item in win_stats if isinstance(item, dict)
    )

    if patent_count is None and win_count == 0:
        return None

    parts = []
    if patent_count is not None:
        parts.append(f"专利 {patent_count} 件")
    if win_count:
        parts.append(f"中标 {win_count} 次")

    evidence = "、".join(parts) + "。"

    interp = "专利与中标数量仅表明两类公开记录并存；缺少专利权属/有效性、中标金额与履约结果、收入转化和同行分母，不能推断技术转化、市场强弱或竞争优势；需逐项核验。"

    return {
        "feature": "专利与中标公开记录并存",
        "evidence": evidence,
        "interpretation": interp,
    }


def insight_risk_scale(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    if not _risk_evidence_known(data):
        return None
    risk = _risk(data)
    inv_total = _i(risk.get("investments_total"))
    shown = len(_investments(data))
    hearings = _i(risk.get("court_hearings_total"))
    restrictions = _i(risk.get("restrictions_total"))
    level = str(risk.get("level") or "")
    if all(v is None for v in (inv_total, hearings, restrictions)) and not level:
        return None
    parts = []
    if level:
        parts.append(f"上游风险等级「{level}」")
    if inv_total is not None:
        parts.append(f"对外投资总量 {inv_total} 家（展示 {shown} 家）")
    if hearings is not None:
        parts.append(f"开庭 {hearings} 条")
    if restrictions is not None:
        parts.append(f"限高 {restrictions} 条")
    severe = (hearings or 0) >= 100 or (restrictions or 0) > 0
    interp = (
        "司法暴露触发人工核验门禁；上游等级与事件数量分别展示，不以数值方向互相推翻。"
        if severe
        else "仅作公开风险线索，不能据投资展示样本或上游分值直接评价总体风险。"
    )
    return {
        "feature": "风险等级、司法事件与投资暴露",
        "evidence": "、".join(parts) + "。",
        "interpretation": interp,
    }


def insight_brand_innovation(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """商标与专利公开数量并列，不推断护城河或优势."""
    patent = _patent(data)
    trademark = _trademark(data)

    patent_count = _i(patent.get("patentCount"))
    tm_count = _i(trademark.get("tmCount"))
    tm_types = _first_list(trademark.get("tmTypeList"))
    type_count = len(tm_types)

    if patent_count is None and tm_count is None:
        return None

    parts = []
    if patent_count is not None:
        parts.append(f"专利 {patent_count} 件")
    if tm_count is not None:
        parts.append(f"商标 {tm_count} 件")
    if type_count:
        parts.append(f"覆盖 {type_count} 个类别")

    evidence = "、".join(parts) + "。"

    interp = "专利、商标及类别数量仅为公开记录；未逐项核验权利人与目标法人关系、有效状态、权利范围、质量和同行分母，不能推断品牌/技术保护强度或竞争优势；需逐项核验。"

    return {
        "feature": "专利与商标公开记录并存",
        "evidence": evidence,
        "interpretation": interp,
    }


def insight_expansion_risk(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    rec = _recruitment(data)
    op = _operation(data)
    risk = _risk(data)
    current = _i(rec.get("current"))
    last3 = _i(rec.get("last_3m"))
    fin = _i(op.get("financing_count"))
    risk_known = _risk_evidence_known(data)
    hearings = _i(risk.get("court_hearings_total")) if risk_known else None
    restrictions = _i(risk.get("restrictions_total")) if risk_known else None
    if all(v is None for v in (current, last3, fin, hearings, restrictions)):
        return None
    evidence = f"当前招聘 {current if current is not None else '未知'}、近三月招聘 {last3 if last3 is not None else '未知'}、融资 {fin if fin is not None else '未知'}、开庭 {hearings if hearings is not None else '未知'}、限高 {restrictions if restrictions is not None else '未知'}。"
    activities = []
    if (current or 0) > 0 or (last3 or 0) > 0:
        activities.append("招聘活动存在")
    if (fin or 0) > 0:
        activities.append("融资活动存在")
    activity_fact = "、".join(activities) if activities else "未见正值招聘或融资活动"
    if (hearings or 0) >= 100 or (restrictions or 0) > 0:
        interp = f"{activity_fact}；司法暴露触发人工核验门禁，不能评价为健康扩张。"
    else:
        interp = f"{activity_fact}；相关指标缺少统一时点、现金流和负债数据，仅作公开事实线索。"
    return {
        "feature": "扩张活动与司法暴露",
        "evidence": evidence,
        "interpretation": interp,
    }


def _first_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in (
            "resultList",
            "list",
            "items",
            "data",
            "holderList",
            "stockHolderList",
            "fpFinancingList",
            "tpQualificationList",
            "punishmentList",
            "anomalyList",
            "tmTypeList",
            "tmStatusList",
            "winbidStatList",
            "winbidAreaStat",
            "sentimentLabelList",
            "patentTypeAppTimeStat",
            "patentTypePubTimeStat",
        ):
            if isinstance(value.get(key), list):
                return value[key]
    if value in (None, "", {}):
        return []
    return [value]


def _holder_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for h in _holders(data)[:15]:
        ratio = _pick(h, "持股比例", "ratio", "占比")
        sub = _pick(h, "认缴金额", "subscriptionDetail", "认缴", "认缴/实缴")
        if isinstance(sub, dict):
            sub = sub.get("amount") or sub.get("value")
        paid = _pick(h, "实缴金额", "payAmount", "实缴", "paidAmount", "认缴/实缴")
        rows.append(
            {
                "股东名称": str(
                    _pick(h, "股东名称", "name", "名称", "holderName") or "-"
                ),
                "持股比例": format_source_ratio(ratio),
                "认缴金额": _amount_text(sub),
                "实缴金额": _amount_text(paid),
                "股东类型": str(
                    _pick(h, "股东类型", "holderType", "entityType") or "-"
                ),
            }
        )
    return rows


def _amount_text(value: Any) -> str:
    """Readable amount for holder/investment tables."""
    if value in (None, "", "-"):
        return "-"
    if isinstance(value, dict):
        val = value.get("value") or value.get("amount")
        coin = value.get("coinType") or ""
        if val is None:
            return "-"
        try:
            fv = float(val)
            if fv >= 1e8:
                return f"{coin} {fv / 1e8:.2f}亿".strip()
            if fv >= 1e4:
                return f"{coin} {fv / 1e4:.0f}万".strip()
            return f"{coin} {fv:.0f}".strip()
        except (TypeError, ValueError):
            return f"{coin} {val}".strip()
    try:
        fv = float(str(value).replace(",", ""))
        if fv >= 1e8:
            return f"人民币 {fv / 1e8:.2f}亿"
        if fv >= 1e4:
            return f"人民币 {fv / 1e4:.0f}万"
        return f"人民币 {fv:.0f}"
    except (TypeError, ValueError):
        return str(value)


def _investment_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for inv in _investments(data)[:15]:
        iratio = _pick(inv, "ratio", "持股比例", "占股比例", "投资比例")
        rows.append(
            {
                "被投资企业": str(
                    _pick(inv, "name", "企业名称", "对外投资企业", "被投资企业") or "-"
                ),
                "持股比例": format_source_ratio(iratio),
                "经营状态": str(_pick(inv, "operStatus", "经营状态", "状态") or "-"),
                "成立日期": str(_pick(inv, "foundTime", "成立日期", "成立时间") or "-"),
                "注册资本": _amount_text(
                    _pick(
                        inv, "subscriptionAmount", "投资金额", "regCapital", "注册资本"
                    )
                ),
            }
        )
    return rows


def _litigation_summary_text(data: Mapping[str, Any]) -> str:
    s = _litigation_summary(data)
    parts = []
    if s["hearings"]:
        parts.append(f"开庭公告 {s['hearings']} 条")
    if s["executed"]:
        parts.append(f"被执行 {s['executed']} 条")
    if s["case_count"]:
        parts.append(f"涉诉 {s['case_count']} 起")
    return "、".join(parts) if parts else "诉讼数据未返回，无法评估"


def _specialty_score_rows(scores: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for _key, label, v in scores.get("items", []):
        if v is not None:
            grade = (
                "优" if v >= 75 else ("良" if v >= 55 else ("中" if v >= 35 else "弱"))
            )
            rows.append({"评估维度": label, "评分": str(v), "等级": grade})
    return rows


# --------------------------------------------------------------------------- #
# Verdict
# --------------------------------------------------------------------------- #
def build_verdict(data: Mapping[str, Any], scores: Mapping[str, Any]) -> Dict[str, Any]:
    """全维度综合画像结论: 综合判定 + 关键关注点."""
    risk = _risk(data)
    concerns: List[str] = []
    blockers: List[str] = []

    n_vio = len(risk.get("serious_violations") or [])
    n_res = (
        risk.get("restrictions_total")
        if risk.get("restrictions_total") is not None
        else len(risk.get("restrictions") or [])
    )
    n_pen = _i(risk.get("penalties_total"))
    if n_pen is None:
        n_pen = len(risk.get("penalties") or [])
    n_ano = (
        risk.get("anomalies_total")
        if risk.get("anomalies_total") is not None
        else len(risk.get("anomalies") or [])
    )
    risk_level_text = str(risk.get("level") or "")

    if n_vio:
        blockers.append(f"严重违法记录 {n_vio} 条")
    if n_res:
        blockers.append(f"限制高消费记录 {n_res} 条")
    if n_pen >= 3:
        concerns.append(f"行政处罚 {n_pen} 条")
    if n_ano:
        concerns.append(f"经营异常 {n_ano} 条")
    hearings = _i(risk.get("court_hearings_total"))
    if hearings is not None and hearings >= 100:
        blockers.append(f"开庭公告 {hearings} 条，需人工司法核验")
    elif hearings:
        concerns.append(f"开庭公告 {hearings} 条")
    if risk_level_text:
        if "高" in risk_level_text or "严重" in risk_level_text:
            blockers.append(f"风险等级「{risk_level_text}」")
        elif "中" in risk_level_text:
            concerns.append(f"风险等级「{risk_level_text}」")

    # 创新实力关注
    innovation = score_innovation_strength(data)
    if innovation is not None and innovation < 30:
        concerns.append("创新实力偏弱")

    avg = scores.get("average")
    if avg is None:
        level = "不予综合评级" if blockers else "数据不足"
        recommendation = "人工司法核验" if blockers else "需补充数据"
        evidence_note = (
            "、".join((blockers + concerns)[:4]) or "主体确认、关键域或工具调用证据不足"
        )
        summary = f"评级门禁未满足，不予综合评级。需核验：{evidence_note}。"
    elif blockers:
        level = "需重点关注"
        recommendation = "需重点关注"
        summary = f"发现 {len(blockers)} 项重大风险阻断项（{'、'.join(blockers)}），综合评分偏低，建议审慎决策。"
    elif avg is not None and avg >= 72 and not concerns:
        level = "多维观察可用"
        recommendation = "多维观察可用"
        summary = f"已满足主体、司法与最低有效域门禁，多维观察均值 {avg}；本报告不包含同行对比，不作领先性结论。"
    elif avg is not None and avg >= 55:
        level = "部分维度可用"
        recommendation = "需核验关注项"
        summary = f"多维观察均值 {avg}，存在 {len(concerns)} 项需关注事项（{'、'.join(concerns[:3])}）；不据此推断全面经营表现。"
    elif avg is not None:
        level = "偏科型"
        recommendation = "偏科型"
        summary = f"全维度综合评分 {avg} 偏低，部分维度存在短板，建议针对性提升。"
    else:
        level = "数据不足"
        recommendation = "需补充数据"
        summary = "多维数据覆盖不足，无法形成充分评估结论，建议补充更多维度数据。"

    return {
        "recommendation": recommendation,
        "level": level,
        "summary": summary,
        "blockers": blockers,
        "key_concerns": concerns[:6],
        "specialty_average": avg,
    }


# --------------------------------------------------------------------------- #
# Main entry
# --------------------------------------------------------------------------- #
def analyze(data: Mapping[str, Any]) -> Dict[str, Any]:
    """Run full cross-domain analysis, returning all artifacts for the report."""
    scores = specialty_scores(data)
    insight_fns = [
        insight_innovation_market,
        insight_risk_scale,
        insight_brand_innovation,
        insight_expansion_risk,
    ]
    cross_insights: List[Dict[str, Any]] = []
    for fn in insight_fns:
        ins = fn(data)
        if ins:
            cross_insights.append(ins)

    verdict = build_verdict(data, scores)
    base = _base(data)

    # Cross metrics (top-level indicator cards)
    metrics: List[Dict[str, Any]] = []
    risk_score = _i(_risk(data).get("score"))
    if risk_score is not None:
        metrics.append(
            {
                "label": "上游风险评分",
                "value": str(risk_score),
                "hint": "上游评分；方向以同次返回等级为准",
                "delta": _risk(data).get("level") or "",
            }
        )
    inv_n = _risk(data).get("investments_total") or len(_investments(data))
    if inv_n:
        metrics.append(
            {
                "label": "对外投资",
                "value": str(inv_n),
                "hint": "关联方数量（风险传导面）",
            }
        )
    if scores.get("average") is not None:
        metrics.append(
            {
                "label": "综合评分",
                "value": str(scores["average"]),
                "hint": f"{len(scores['valid'])} 项有效专项观察均值",
                "delta": verdict["level"],
            }
        )
    # 专利指标
    patent_count = _i(_patent(data).get("patentCount"))
    if patent_count:
        metrics.append(
            {"label": "专利数量", "value": str(patent_count), "hint": "知识产权储备"}
        )
    # 商标指标
    tm_count = _i(_trademark(data).get("tmCount"))
    if tm_count:
        metrics.append(
            {"label": "商标数量", "value": str(tm_count), "hint": "品牌保护覆盖"}
        )
    # 招投标指标
    bidding_total = _i(_bidding(data).get("bidding_total"))
    if bidding_total:
        metrics.append(
            {
                "label": "招投标参与",
                "value": str(bidding_total),
                "hint": "市场活跃度信号",
            }
        )
    # 舆情指标
    news = _news(data)
    sentiment_stats = news.get("newsSentimentStats") or {}
    total_news = sum(
        _i(sentiment_stats.get(k)) or 0
        for k in ("neutral", "negative", "positive", "unknown")
    )
    if total_news:
        pos = _i(sentiment_stats.get("positive")) or 0
        pos_pct = round(pos / total_news * 100) if total_news > 0 else 0
        metrics.append(
            {
                "label": "舆情总数",
                "value": str(total_news),
                "hint": f"正面占比 {pos_pct}%",
            }
        )
    # 风险计数指标
    n_pen = len(_risk(data).get("penalties") or [])
    if n_pen:
        metrics.append(
            {"label": "行政处罚", "value": str(n_pen), "hint": "行政处罚记录数"}
        )
    # 财务指标
    reg = _pick(base, "注册资本", "regCapital", "regCapitalValue")
    if reg:
        metrics.append(
            {"label": "注册资本", "value": str(reg), "hint": "工商登记注册资本"}
        )
    paid_rate = _ratio_pct(_pick(base, "资本实缴率", "实缴率"))
    if paid_rate is not None:
        metrics.append(
            {
                "label": "资本实缴率",
                "value": f"{paid_rate:.0f}%",
                "hint": "实缴资本/注册资本比例",
            }
        )
    fin_n = _i(_operation(data).get("financing_count"))
    if fin_n:
        metrics.append(
            {"label": "融资轮次", "value": str(fin_n), "hint": "历史融资轮次"}
        )
    # 招聘指标
    cur_hire = _i(_recruitment(data).get("current"))
    if cur_hire is not None:
        metrics.append(
            {"label": "在招岗位", "value": str(cur_hire), "hint": "招聘活跃度信号"}
        )
    # 风险计数指标
    res_n = _risk(data).get("restrictions_total") or len(
        _risk(data).get("restrictions") or []
    )
    if res_n:
        metrics.append(
            {"label": "限制高消费", "value": str(res_n), "hint": "被执行限高记录数"}
        )
    hearing_n = _risk(data).get("court_hearings_total")
    if hearing_n:
        metrics.append(
            {"label": "开庭公告", "value": str(hearing_n), "hint": "诉讼开庭记录总数"}
        )
    ano_n = _risk(data).get("anomalies_total") or len(
        _risk(data).get("anomalies") or []
    )
    if ano_n:
        metrics.append(
            {"label": "经营异常", "value": str(ano_n), "hint": "经营异常名录记录"}
        )
    holder_n = len(_holders(data))
    if holder_n:
        metrics.append(
            {"label": "股东数量", "value": str(holder_n), "hint": "工商公示股东数"}
        )
    for _key, label, v in scores["valid"]:
        metrics.append({"label": label, "value": str(v), "hint": "全维度专项评分"})

    # Detail sections
    section_specs: List[Dict[str, Any]] = []
    section_data: Dict[str, Any] = {}

    holder_rows = _holder_rows(data)
    if holder_rows:
        section_specs.append(
            {
                "key": "fp_holders",
                "title": "股东出资结构",
                "kind": "table",
                "note": "股东持股比例与实缴情况（资本充实性核查基础）",
                "columns": [
                    ("股东名称", "股东名称"),
                    ("持股比例", "持股比例"),
                    ("认缴金额", "认缴金额"),
                    ("实缴金额", "实缴金额"),
                    ("股东类型", "股东类型"),
                ],
            }
        )
        section_data["fp_holders"] = holder_rows

    invest_rows = _investment_rows(data)
    if invest_rows:
        section_specs.append(
            {
                "key": "fp_investments",
                "title": "对外投资清单（关联方敞口）",
                "kind": "table",
                "note": f"报告总量 {_risk(data).get('investments_total') or len(_investments(data))} 家，当前列表展示 {min(len(_investments(data)), 15)} 家；仅表示关联暴露面，未核验关联方风险传导",
                "columns": [
                    ("被投资企业", "被投资企业"),
                    ("持股比例", "持股比例"),
                    ("经营状态", "经营状态"),
                    ("成立日期", "成立日期"),
                    ("注册资本", "注册资本"),
                ],
            }
        )
        section_data["fp_investments"] = invest_rows

    score_rows = _specialty_score_rows(scores)
    if score_rows:
        section_specs.append(
            {
                "key": "fp_specialty",
                "title": "全维度专项评分矩阵",
                "kind": "table",
                "note": "跨维度交叉评分（创新实力 / 风险健康度 / 工商基础 / 市场活跃度 / 经营状况 / 舆情可见度 / 品牌商标 / 人才储备）",
                "columns": [
                    ("评估维度", "评估维度"),
                    ("评分", "评分"),
                    ("等级", "等级"),
                ],
            }
        )
        section_data["fp_specialty"] = score_rows

    return {
        "metrics": metrics,
        "insights": cross_insights,
        "specialty_scores": {
            "items": [
                {"key": key, "label": label, "score": value}
                for key, label, value in scores["items"]
            ],
            "average": scores["average"],
        },
        "verdict": verdict,
        "section_specs": section_specs,
        "section_data": section_data,
    }
