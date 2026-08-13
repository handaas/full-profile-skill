#!/usr/bin/env python3
"""Cross-domain analysis engine for full-profile reports.

Consumes the unified NormalizedData from mcp_orchestration and produces
cross-dimensional insights that NO single atomic skill can generate on its own:

  1. 创新实力       — 专利 + 商标（数量与质量）
  2. 风险健康度     — 处罚/异常/限高/违法 倒扣
  3. 工商基础       — 实缴率 + 规模 + 成立年限
  4. 市场活跃度     — 招投标参与 + 中标统计
  5. 经营状况       — 融资 + 规模 + 趋势
  6. 数字化程度     — 舆情声量 + 情感分布
  7. 品牌商标       — 商标覆盖 + 类别分布
  8. 人才储备       — 招聘活跃度 + 薪酬 + 福利

All evidence is grounded in actual data; missing dimensions are skipped (never
fabricated).
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

# --------------------------------------------------------------------------- #
# Tolerant field extraction (handles both live MCP and cached report shapes)
# --------------------------------------------------------------------------- #
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
        return float(str(value).replace(",", "").replace("万", "").replace("%", "").replace("亿", ""))
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
    """Unified litigation info across live MCP (English keys) and cached reports (Chinese keys)."""
    risk = _risk(data)
    lit = _litigation(data)
    case_count = _i(lit.get("case_count") or lit.get("caseCount"))
    defendant = _i(lit.get("as_defendant") or lit.get("asDefendant"))
    plaintiff = _i(lit.get("as_plaintiff") or lit.get("asPlaintiff"))
    hearings = risk.get("court_hearings_total") or _i(lit.get("开庭公告数"))
    announcements = _i(lit.get("法院公告数"))
    judgments = _i(lit.get("裁判文书数"))
    executed = risk.get("restrictions_total") or _i(lit.get("被执行人记录数"))
    dishonest = _i(lit.get("失信被执行人数"))
    if case_count is None:
        parts = [v for v in (hearings, announcements, judgments) if v is not None]
        if parts:
            case_count = sum(parts)
    return {
        "case_count": case_count, "as_defendant": defendant, "as_plaintiff": plaintiff,
        "hearings": hearings, "announcements": announcements, "judgments": judgments,
        "executed": executed, "dishonest": dishonest,
        "has_role_detail": defendant is not None,
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


# --------------------------------------------------------------------------- #
# Specialty scores (each 0-100, or None if data unavailable)
# --------------------------------------------------------------------------- #
def score_innovation_strength(data: Mapping[str, Any]) -> Optional[float]:
    """创新实力: 专利 + 商标（数量与质量）."""
    patent = _patent(data)
    trademark = _trademark(data)

    patent_count = _i(patent.get("patentCount")) or 0
    invention_app = _i(patent.get("inventionAppPatentCount")) or 0
    invention_lic = _i(patent.get("inventionLicPatentCount")) or 0
    tm_count = _i(trademark.get("tmCount")) or 0
    tm_valid = _i(trademark.get("tmValidNumber")) or 0

    if patent_count == 0 and tm_count == 0:
        return None

    s = 0
    # 专利评分（最高 60 分）
    if invention_lic:
        s += min(30, invention_lic * 6)
    if invention_app:
        s += min(20, invention_app * 4)
    other_patent = patent_count - invention_app - invention_lic
    if other_patent:
        s += min(10, other_patent * 2)

    # 商标评分（最高 40 分）
    if tm_valid:
        s += min(30, tm_valid * 3)
    other_tm = tm_count - tm_valid
    if other_tm:
        s += min(10, other_tm)

    return round(max(0, min(100, s)), 1)


def score_risk_health(data: Mapping[str, Any]) -> Optional[float]:
    """风险健康度: deduct for penalties / anomalies / restrictions / violations."""
    risk = _risk(data)
    n_pen = len(risk.get("penalties") or [])
    n_ano = len(risk.get("anomalies") or [])
    n_res = len(risk.get("restrictions") or [])
    n_vio = len(risk.get("serious_violations") or []) if risk.get("serious_violations") else 0
    total_hits = n_pen + n_ano + n_res + n_vio
    if total_hits == 0 and risk.get("score") is None:
        return None
    health = 100 - (n_pen * 12 + n_ano * 8 + n_res * 15 + n_vio * 20)
    return round(max(0, min(100, health)), 1)


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

    s = 0
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
    win_count = sum(_i(item.get("count")) or 0 for item in win_stats if isinstance(item, dict))

    if bid_total == 0 and win_count == 0:
        return None

    s = 0
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
    has_scale = bool(_pick(scale, "staff", "人员规模", "enterpriseScale") or _pick(scale, "turnover", "年营业额", "annualTurnover"))
    trends = operation.get("trends") or {}

    # 趋势信号
    trend_signals = 0
    for k in ("isNewFinancingIn3Month", "isStaffExpandIn3Month", "isFoundSubsidiaryIn3Month",
              "isExpandNewCityIn3Month", "isAuthorityListIn6Month"):
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
    """数字化程度: 舆情声量 + 情感分布."""
    news = _news(data)

    sentiment_stats = news.get("newsSentimentStats") or {}
    if not isinstance(sentiment_stats, dict):
        sentiment_stats = {}

    total_news = sum(_i(sentiment_stats.get(k)) or 0 for k in ("neutral", "negative", "positive", "unknown"))
    positive_ratio = 0
    if total_news > 0:
        pos = _i(sentiment_stats.get("positive")) or 0
        positive_ratio = pos / total_news * 100

    if total_news == 0:
        return None

    s = 0
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
        ("risk_health", "风险健康度", score_risk_health(data)),
        ("business_foundation", "工商基础", score_business_foundation(data)),
        ("market_activity", "市场活跃度", score_market_activity(data)),
        ("operation_status", "经营状况", score_operation_status(data)),
        ("digital_presence", "数字化程度", score_digital_presence(data)),
        ("brand_trademark", "品牌商标", score_brand_trademark(data)),
        ("talent_reserve", "人才储备", score_talent_reserve(data)),
    ]
    valid = [(key, label, v) for key, label, v in items if v is not None]
    avg = round(sum(v for _, _, v in valid) / len(valid), 1) if valid else None
    return {"items": items, "valid": valid, "average": avg}


# --------------------------------------------------------------------------- #
# Cross-domain insights
# --------------------------------------------------------------------------- #
def insight_innovation_market(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """创新×市场: 专利×中标 → 技术变现."""
    patent = _patent(data)
    bidding = _bidding(data)

    patent_count = _i(patent.get("patentCount")) or 0
    win_stats = _first_list(bidding.get("winbidStatList"))
    win_count = sum(_i(item.get("count")) or 0 for item in win_stats if isinstance(item, dict))

    if patent_count == 0 and win_count == 0:
        return None

    parts = []
    if patent_count:
        parts.append(f"专利 {patent_count} 件")
    if win_count:
        parts.append(f"中标 {win_count} 次")

    evidence = "、".join(parts) + "。"

    if patent_count >= 10 and win_count >= 5:
        interp = f"技术创新与市场变现双强。专利储备 {patent_count} 件，中标 {win_count} 次，技术转化与市场开拓能力突出，具备持续竞争优势。"
    elif patent_count >= 10:
        interp = f"技术创新能力强（专利 {patent_count} 件）但市场变现相对有限，建议关注技术转化路径与商业化落地。"
    elif win_count >= 5:
        interp = f"市场活跃度高（中标 {win_count} 次）但专利储备有限，建议加强技术积累与知识产权保护。"
    else:
        interp = "创新与市场数据有限，建议补充更多维度以评估技术变现能力。"

    return {"feature": "创新实力与市场活跃度匹配", "evidence": evidence, "interpretation": interp}


def insight_risk_scale(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """风险×规模: 风险×投资 → 风险敞口."""
    risk = _risk(data)
    risk_score = _i(risk.get("score"))
    risk_level = str(risk.get("level") or "")

    invest_n = len(_investments(data))
    hearings = risk.get("court_hearings_total") or 0

    if risk_score is None and not risk_level and invest_n == 0 and hearings == 0:
        return None

    parts = []
    if risk_score is not None:
        parts.append(f"风险评分 {risk_score}")
    if risk_level:
        parts.append(f"风险等级「{risk_level}」")
    if invest_n:
        parts.append(f"对外投资 {invest_n} 家")
    if hearings:
        parts.append(f"开庭公告 {hearings} 条")

    evidence = "、".join(parts) + "。" if parts else "风险与规模数据有限。"

    if (risk_score or 0) >= 60 or "高" in risk_level:
        if invest_n >= 5:
            interp = f"综合风险偏高（{risk_level or risk_score}）且对外投资 {invest_n} 家，风险敞口较大。建议核查关联方风险传导，加强风险隔离机制。"
        else:
            interp = f"综合风险偏高（{risk_level or risk_score}），建议关注核心风险案件并建立缓释措施。"
    elif invest_n >= 10:
        interp = f"对外投资 {invest_n} 家，关联方网络较广。虽风险相对可控，仍建议定期监控关联方经营与法律风险。"
    else:
        interp = "风险与投资规模数据有限，建议补充更多维度以评估风险敞口。"

    return {"feature": "风险敞口与投资规模匹配度", "evidence": evidence, "interpretation": interp}


def insight_brand_innovation(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """品牌×创新: 商标×专利 → IP护城河."""
    patent = _patent(data)
    trademark = _trademark(data)

    patent_count = _i(patent.get("patentCount")) or 0
    tm_count = _i(trademark.get("tmCount")) or 0
    tm_types = _first_list(trademark.get("tmTypeList"))
    type_count = len(tm_types)

    if patent_count == 0 and tm_count == 0:
        return None

    parts = []
    if patent_count:
        parts.append(f"专利 {patent_count} 件")
    if tm_count:
        parts.append(f"商标 {tm_count} 件")
    if type_count:
        parts.append(f"覆盖 {type_count} 个类别")

    evidence = "、".join(parts) + "。"

    if patent_count >= 20 and tm_count >= 10 and type_count >= 5:
        interp = "专利与商标布局完善，形成较强的 IP 护城河。技术保护与品牌覆盖并重，竞争优势显著。"
    elif patent_count >= 10 or tm_count >= 5:
        interp = "具备一定的 IP 储备，建议继续完善专利与商标布局，构建更全面的知识产权保护体系。"
    else:
        interp = "IP 储备相对有限，建议加强技术创新与品牌注册，提升知识产权保护水平。"

    return {"feature": "知识产权护城河（专利+商标）", "evidence": evidence, "interpretation": interp}


def insight_expansion_risk(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """扩张×风险: 招聘融资扩张×诉讼."""
    recruitment = _recruitment(data)
    operation = _operation(data)
    risk = _risk(data)

    current = _i(recruitment.get("current")) or 0
    last_3m = _i(recruitment.get("last_3m")) or 0
    fin_n = _i(operation.get("financing_count")) or 0
    hearings = risk.get("court_hearings_total") or 0
    restrictions = risk.get("restrictions_total") or 0

    if current == 0 and last_3m == 0 and fin_n == 0 and hearings == 0 and restrictions == 0:
        return None

    parts = []
    if current:
        parts.append(f"当前在招 {current} 人")
    if last_3m:
        parts.append(f"近三月招聘 {last_3m} 人")
    if fin_n:
        parts.append(f"融资 {fin_n} 轮")
    if hearings:
        parts.append(f"开庭公告 {hearings} 条")
    if restrictions:
        parts.append(f"限高 {restrictions} 条")

    evidence = "、".join(parts) + "。" if parts else "扩张与风险数据有限。"

    hiring_active = (current or 0) >= 10 or (last_3m or 0) >= 20
    risk_high = hearings >= 3 or restrictions >= 1

    if hiring_active and fin_n >= 2:
        if risk_high:
            interp = "扩张活跃（招聘+融资）但伴随较高风险，需平衡扩张节奏与风险管控，避免过度扩张引发经营风险。"
        else:
            interp = "扩张活跃且风险可控，业务发展动能充足，建议关注扩张效率与质量。"
    elif risk_high:
        interp = "存在较多法律风险，建议优先处理风险案件，避免影响业务稳定性。"
    else:
        interp = "扩张与风险数据有限，建议补充更多维度以评估扩张风险匹配度。"

    return {"feature": "扩张活力与风险匹配度", "evidence": evidence, "interpretation": interp}


# --------------------------------------------------------------------------- #
# Detail sections (tables fed to the renderer)
# --------------------------------------------------------------------------- #
def _first_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("resultList", "list", "items", "data", "holderList", "stockHolderList",
                    "fpFinancingList", "tpQualificationList", "punishmentList", "anomalyList",
                    "tmTypeList", "tmStatusList", "winbidStatList", "winbidAreaStat",
                    "sentimentLabelList", "patentTypeAppTimeStat", "patentTypePubTimeStat"):
            if isinstance(value.get(key), list):
                return value[key]
    if value in (None, "", {}):
        return []
    return [value]


def _holder_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for h in _holders(data)[:15]:
        ratio = _pick(h, "持股比例", "ratio", "占比")
        if ratio is not None:
            try:
                rf = float(ratio)
                ratio = f"{rf * 100:.1f}%" if rf <= 1 else f"{rf:.1f}%"
            except (TypeError, ValueError):
                pass
        sub = _pick(h, "认缴金额", "subscriptionDetail", "认缴", "认缴/实缴")
        if isinstance(sub, dict):
            sub = sub.get("amount") or sub.get("value")
        paid = _pick(h, "实缴金额", "payAmount", "实缴", "paidAmount", "认缴/实缴")
        rows.append({
            "股东名称": str(_pick(h, "股东名称", "name", "名称", "holderName") or "-"),
            "持股比例": str(ratio or "-"),
            "认缴金额": _amount_text(sub),
            "实缴金额": _amount_text(paid),
            "股东类型": str(_pick(h, "股东类型", "holderType", "entityType") or "-"),
        })
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
                return f"{coin} {fv/1e8:.2f}亿".strip()
            if fv >= 1e4:
                return f"{coin} {fv/1e4:.0f}万".strip()
            return f"{coin} {fv:.0f}".strip()
        except (TypeError, ValueError):
            return f"{coin} {val}".strip()
    try:
        fv = float(str(value).replace(",", ""))
        if fv >= 1e8:
            return f"人民币 {fv/1e8:.2f}亿"
        if fv >= 1e4:
            return f"人民币 {fv/1e4:.0f}万"
        return f"人民币 {fv:.0f}"
    except (TypeError, ValueError):
        return str(value)


def _investment_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for inv in _investments(data)[:15]:
        iratio = _pick(inv, "ratio", "持股比例", "占股比例", "投资比例")
        if iratio is not None:
            try:
                rf = float(iratio)
                iratio = f"{rf * 100:.0f}%" if rf <= 1 else f"{rf:.0f}%"
            except (TypeError, ValueError):
                pass
        rows.append({
            "被投资企业": str(_pick(inv, "name", "企业名称", "对外投资企业", "被投资企业") or "-"),
            "持股比例": str(iratio or "-"),
            "经营状态": str(_pick(inv, "operStatus", "经营状态", "状态") or "-"),
            "成立日期": str(_pick(inv, "foundTime", "成立日期", "成立时间") or "-"),
            "注册资本": _amount_text(_pick(inv, "subscriptionAmount", "投资金额", "regCapital", "注册资本")),
        })
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
    return "、".join(parts) if parts else "无显著诉讼风险"


def _specialty_score_rows(scores: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for _key, label, v in scores.get("items", []):
        if v is not None:
            grade = "优" if v >= 75 else ("良" if v >= 55 else ("中" if v >= 35 else "弱"))
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
    n_res = len(risk.get("restrictions") or [])
    n_pen = len(risk.get("penalties") or [])
    n_ano = len(risk.get("anomalies") or [])
    risk_score = _i(risk.get("score"))
    risk_level_text = str(risk.get("level") or "")

    if n_vio:
        blockers.append(f"严重违法记录 {n_vio} 条")
    if n_res:
        blockers.append(f"限制高消费记录 {n_res} 条")
    if n_pen >= 3:
        concerns.append(f"行政处罚 {n_pen} 条")
    if n_ano:
        concerns.append(f"经营异常 {n_ano} 条")
    if risk_level_text:
        if "高" in risk_level_text or "严重" in risk_level_text:
            blockers.append(f"风险等级「{risk_level_text}」")
        elif "中" in risk_level_text:
            concerns.append(f"风险等级「{risk_level_text}」")
    elif risk_score is not None and risk_score >= 70:
        blockers.append(f"综合风险评分 {risk_score}（偏高）")
    elif risk_score is not None and risk_score >= 50:
        concerns.append(f"综合风险评分 {risk_score}（中等）")

    # 创新实力关注
    innovation = score_innovation_strength(data)
    if innovation is not None and innovation < 30:
        concerns.append("创新实力偏弱")

    avg = scores.get("average")
    if blockers:
        level = "需重点关注"
        recommendation = "需重点关注"
        summary = f"发现 {len(blockers)} 项重大风险阻断项（{'、'.join(blockers)}），综合评分偏低，建议审慎决策。"
    elif avg is not None and avg >= 72 and not concerns:
        level = "全面领先型"
        recommendation = "全面领先型"
        summary = f"全维度综合评分 {avg}，各维度表现稳健，无明显短板，综合竞争力突出。"
    elif avg is not None and avg >= 55:
        level = "均衡发展型"
        recommendation = "均衡发展型"
        summary = f"全维度综合评分 {avg}，存在 {len(concerns)} 项需关注事项（{'、'.join(concerns[:3])}），整体发展均衡。"
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
        metrics.append({"label": "综合风险评分", "value": str(risk_score), "hint": "风险洞察评分（越低越好）", "delta": _risk(data).get("level") or ""})
    inv_n = len(_investments(data))
    if inv_n:
        metrics.append({"label": "对外投资", "value": str(inv_n), "hint": "关联方数量（风险传导面）"})
    if scores.get("average") is not None:
        metrics.append({"label": "综合评分", "value": str(scores["average"]), "hint": "8 项专项评分均值", "delta": verdict["level"]})
    # 专利指标
    patent_count = _i(_patent(data).get("patentCount"))
    if patent_count:
        metrics.append({"label": "专利数量", "value": str(patent_count), "hint": "知识产权储备"})
    # 商标指标
    tm_count = _i(_trademark(data).get("tmCount"))
    if tm_count:
        metrics.append({"label": "商标数量", "value": str(tm_count), "hint": "品牌保护覆盖"})
    # 招投标指标
    bidding_total = _i(_bidding(data).get("bidding_total"))
    if bidding_total:
        metrics.append({"label": "招投标参与", "value": str(bidding_total), "hint": "市场活跃度信号"})
    # 舆情指标
    news = _news(data)
    sentiment_stats = news.get("newsSentimentStats") or {}
    total_news = sum(_i(sentiment_stats.get(k)) or 0 for k in ("neutral", "negative", "positive", "unknown"))
    if total_news:
        pos = _i(sentiment_stats.get("positive")) or 0
        pos_pct = round(pos / total_news * 100) if total_news > 0 else 0
        metrics.append({"label": "舆情总数", "value": str(total_news), "hint": f"正面占比 {pos_pct}%"})
    # 风险计数指标
    n_pen = len(_risk(data).get("penalties") or [])
    if n_pen:
        metrics.append({"label": "行政处罚", "value": str(n_pen), "hint": "行政处罚记录数"})
    # 财务指标
    reg = _pick(base, "注册资本", "regCapital", "regCapitalValue")
    if reg:
        metrics.append({"label": "注册资本", "value": str(reg), "hint": "工商登记注册资本"})
    paid_rate = _ratio_pct(_pick(base, "资本实缴率", "实缴率"))
    if paid_rate is not None:
        metrics.append({"label": "资本实缴率", "value": f"{paid_rate:.0f}%", "hint": "实缴资本/注册资本比例"})
    fin_n = _i(_operation(data).get("financing_count"))
    if fin_n:
        metrics.append({"label": "融资轮次", "value": str(fin_n), "hint": "历史融资轮次"})
    # 招聘指标
    cur_hire = _i(_recruitment(data).get("current"))
    if cur_hire is not None:
        metrics.append({"label": "在招岗位", "value": str(cur_hire), "hint": "招聘活跃度信号"})
    # 风险计数指标
    res_n = _risk(data).get("restrictions_total") or len(_risk(data).get("restrictions") or [])
    if res_n:
        metrics.append({"label": "限制高消费", "value": str(res_n), "hint": "被执行限高记录数"})
    hearing_n = _risk(data).get("court_hearings_total")
    if hearing_n:
        metrics.append({"label": "开庭公告", "value": str(hearing_n), "hint": "诉讼开庭记录总数"})
    ano_n = _risk(data).get("anomalies_total") or len(_risk(data).get("anomalies") or [])
    if ano_n:
        metrics.append({"label": "经营异常", "value": str(ano_n), "hint": "经营异常名录记录"})
    holder_n = len(_holders(data))
    if holder_n:
        metrics.append({"label": "股东数量", "value": str(holder_n), "hint": "工商公示股东数"})
    for _key, label, v in scores["valid"]:
        metrics.append({"label": label, "value": str(v), "hint": "全维度专项评分"})

    # Detail sections
    section_specs: List[Dict[str, Any]] = []
    section_data: Dict[str, Any] = {}

    holder_rows = _holder_rows(data)
    if holder_rows:
        section_specs.append({"key": "fp_holders", "title": "股东出资结构", "kind": "table",
                              "note": "股东持股比例与实缴情况（资本充实性核查基础）",
                              "columns": [("股东名称", "股东名称"), ("持股比例", "持股比例"), ("认缴金额", "认缴金额"), ("实缴金额", "实缴金额"), ("股东类型", "股东类型")]})
        section_data["fp_holders"] = holder_rows

    invest_rows = _investment_rows(data)
    if invest_rows:
        section_specs.append({"key": "fp_investments", "title": "对外投资清单（关联方敞口）", "kind": "table",
                              "note": f"共 {len(_investments(data))} 家对外投资（展示前 {min(len(_investments(data)), 15)} 家），风险可能经关联方传导",
                              "columns": [("被投资企业", "被投资企业"), ("持股比例", "持股比例"), ("经营状态", "经营状态"), ("成立日期", "成立日期"), ("注册资本", "注册资本")]})
        section_data["fp_investments"] = invest_rows

    score_rows = _specialty_score_rows(scores)
    if score_rows:
        section_specs.append({"key": "fp_specialty", "title": "全维度专项评分矩阵", "kind": "table",
                              "note": "跨维度交叉评分（创新实力 / 风险健康度 / 工商基础 / 市场活跃度 / 经营状况 / 数字化程度 / 品牌商标 / 人才储备）",
                              "columns": [("评估维度", "评估维度"), ("评分", "评分"), ("等级", "等级")]})
        section_data["fp_specialty"] = score_rows

    return {
        "metrics": metrics,
        "insights": cross_insights,
        "specialty_scores": {"items": [{"key": k, "label": l, "score": v} for k, l, v in scores["items"]],
                             "average": scores["average"]},
        "verdict": verdict,
        "section_specs": section_specs,
        "section_data": section_data,
    }
