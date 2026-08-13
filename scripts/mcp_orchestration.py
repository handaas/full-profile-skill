#!/usr/bin/env python3
"""Full-profile MCP orchestration: tool plan + multi-source collection + normalization.

Selects high-value tools across 8 MCP servers, tuned for full-profile comprehensive analysis:

  enterprise  : base_info / holders / investments / key persons
  risk        : score / litigation / hearings / penalties / anomalies /
                consumption-restrictions / chattel-mortgage
  operation   : business-scale / financing / company-trends / rankings
  patent      : patent_stats (专利统计)
  trademark   : profile / stats (商标概况/统计)
  bidding     : win_stats / bidding_info (中标统计/招投标参与)
  news        : news_stats (舆情统计)
  recruitment : trend / employer-profile (扩张活力)

Two collection modes:
  * live  — connect to the 8 MCP servers via MultiMcpClient (richest data)
  * cache — read pre-existing atomic report JSONs (reports_探迹/) for dry-run

Both normalize into the SAME unified structure consumed by cross_analysis.
"""
from __future__ import annotations

import asyncio
import json
import pathlib
from typing import Any, Dict, List, Mapping, Optional

from multi_mcp_client import MultiMcpClient, MultiMcpError

# --------------------------------------------------------------------------- #
# Generic extractors
# --------------------------------------------------------------------------- #

def _is_api_error(value: Any) -> bool:
    """Detect MCP API error responses (not empty data, but actual failures like 405)."""
    if value is None:
        return False
    if isinstance(value, str):
        return any(s in value for s in ("接口调用失败", "查询失败", "状态码：4", "状态码：5"))
    if isinstance(value, dict):
        # Check all string values for error indicators
        for v in value.values():
            if isinstance(v, str) and any(s in v for s in ("接口调用失败", "查询失败", "状态码：4", "状态码：5")):
                return True
    return False

def _first_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        if _is_api_error(value):
            return []
        for key in ("resultList", "list", "items", "data", "holderList", "stockHolderList",
                    "fpFinancingList", "tpQualificationList", "punishmentList", "anomalyList",
                    "tmTypeList", "tmStatusList", "winbidStatList", "winbidAreaStat", "tenderStatList",
                    "sentimentLabelList"):
            if isinstance(value.get(key), list):
                return value[key]
    if value in (None, "", {}):
        return []
    return [value]


def _safe_total(value: Any) -> Optional[int]:
    if isinstance(value, dict):
        if _is_api_error(value):
            return None
        t = value.get("total")
        try:
            return int(t) if t is not None else None
        except (TypeError, ValueError):
            return None
    return None


def _text(value: Any, limit: int = 0) -> str:
    if value is None:
        return ""
    t = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    t = " ".join(t.split())
    return (t[: limit - 1].rstrip() + "…") if (limit and len(t) > limit) else t


def _int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float(value: Any) -> Optional[float]:
    try:
        return float(str(value).replace(",", "").replace("万", "").replace("亿", ""))
    except (TypeError, ValueError):
        return None


def _amount(value: Any) -> str:
    """Parse a HandaaS amount field into readable text.

    Accepts: {"coinType":"人民币","value":2e9} | 20000 | "100万" | "人民币 100万"
    """
    if value in (None, "", "-"):
        return "-"
    if isinstance(value, dict):
        val = value.get("value")
        coin = value.get("coinType") or value.get("currency") or ""
        if val is None:
            return "-"
        try:
            fv = float(val)
        except (TypeError, ValueError):
            return f"{coin} {val}".strip()
        if fv >= 1e8:
            return f"{coin} {fv / 1e8:.2f}亿".strip()
        if fv >= 1e4:
            return f"{coin} {fv / 1e4:.0f}万".strip()
        return f"{coin} {fv:.0f}".strip()
    return str(value)


def _industry_text(value: Any) -> str:
    """Flatten a nested industry dict into '一级/二级/三级' text."""
    if not isinstance(value, dict):
        return str(value) if value else "-"
    parts = []
    for k in ("firstIndustry", "secondIndustry", "thirdIndustry", "fourthIndustry"):
        v = value.get(k)
        if v and str(v) not in parts:
            parts.append(str(v))
    return " / ".join(parts) if parts else "-"


def _amount_num(value: Any) -> Optional[float]:
    """Extract the numeric value from a HandaaS amount field."""
    if isinstance(value, dict):
        return _float(value.get("value"))
    return _float(value)


def _kv_addr(value: Any) -> str:
    """Extract address string from a nested addressValue dict."""
    if isinstance(value, dict):
        return str(value.get("value") or value.get("address") or "-")
    return str(value) if value else ""


# --------------------------------------------------------------------------- #
# Live collection: MCP tool plan
# --------------------------------------------------------------------------- #
def build_mcp_calls(enterprise: str, keyword_type: str) -> List[tuple[str, str, str, Dict[str, Any]]]:
    """Return [(key, domain, tool, args), ...] for all full-profile tools."""
    ent_kw: Dict[str, Any] = {"keyword": enterprise}
    mk_kw: Dict[str, Any] = {"matchKeyword": enterprise, "keywordType": keyword_type}
    return [
        # --- enterprise (工商) ---
        ("ent_base", "enterprise", "enterprise_get_enterprise_base_info", ent_kw),
        ("ent_holder", "enterprise", "enterprise_get_enterprise_holder_info", ent_kw),
        ("ent_invest", "enterprise", "enterprise_get_enterprise_invest_info", ent_kw),
        ("ent_person", "enterprise", "enterprise_get_enterprise_main_person_info", ent_kw),
        # --- risk (风险) ---
        ("risk_score", "risk", "enterprise_risk_insight_score", mk_kw),
        ("risk_litigation", "risk", "risk_insight_litigation_risk_profile", mk_kw),
        ("risk_hearings", "risk", "risk_insight_court_hearings", {**mk_kw, "pageSize": 20}),
        ("risk_penalties", "risk", "risk_insight_penalties", mk_kw),
        ("risk_anomalies", "risk", "risk_insight_business_anomalies", mk_kw),
        ("risk_restrictions", "risk", "risk_insight_consumption_restrictions", {**mk_kw, "pageSize": 20}),
        ("risk_mortgage", "risk", "risk_insight_chattel_mortgage", mk_kw),
        # --- operation (经营) ---
        ("op_scale", "operation", "operation_insight_business_scale", mk_kw),
        ("op_financing", "operation", "operation_insight_financing_info", mk_kw),
        ("op_trends", "operation", "operation_insight_company_trends", mk_kw),
        ("op_rankings", "operation", "operation_insight_enterprise_rankings", {**mk_kw, "pageSize": 10}),
        # --- patent (专利) ---
        ("patent_stats", "patent", "patent_bigdata_patent_stats", mk_kw),
        # --- trademark (商标) ---
        ("tm_profile", "trademark", "trademark_bigdata_trademark_profile", mk_kw),
        ("tm_stats", "trademark", "trademark_bigdata_trademark_stats", mk_kw),
        # --- bidding (招投标) ---
        ("bid_win_stats", "bidding", "bid_bigdata_bid_win_stats", mk_kw),
        ("bid_info", "bidding", "bid_bigdata_bidding_info", {**mk_kw, "pageSize": 20}),
        # --- news (舆情) ---
        ("news_stats", "news", "news_bigdata_news_stats", mk_kw),
        # --- recruitment (招聘/扩张活跃度) ---
        ("rec_trend", "recruitment", "recruitment_trend", mk_kw),
        ("rec_profile", "recruitment", "recruitment_employer_profile", mk_kw),
    ]


_ENTERPRISE_SUFFIXES = ("公司", "集团", "有限", "院", "厂", "中心", "事务所", "合作社", "合伙")


def is_full_name(raw: str) -> bool:
    return any(s in (raw or "") for s in _ENTERPRISE_SUFFIXES)


async def resolve_enterprise(client: MultiMcpClient, keyword: str) -> Dict[str, Any]:
    """Resolve a keyword to a canonical enterprise name via enterprise MCP fuzzy search."""
    keyword = (keyword or "").strip()
    if not keyword:
        return {"keyword": "", "enterprise": "", "resolved": False}
    if is_full_name(keyword):
        return {"keyword": keyword, "enterprise": keyword, "resolved": True, "reason": "视为企业全称"}
    fuzzy = await client.call(
        "enterprise", "enterprise_get_keyword_search", {"matchKeyword": keyword, "pageSize": 1}
    )
    for rec in _first_list(fuzzy):
        if isinstance(rec, dict):
            name = str(rec.get("name") or "").strip()
            if name:
                return {"keyword": keyword, "enterprise": name, "resolved": True, "reason": "关键词模糊查询补全"}
    return {"keyword": keyword, "enterprise": keyword, "resolved": False, "reason": "模糊查询未命中，按关键词直查"}


async def _collect_live(enterprise: str, keyword_type: str) -> Dict[str, Any]:
    """Connect to 8 MCP servers, resolve name, fan out all tool calls."""
    async with MultiMcpClient() as client:
        resolved = await resolve_enterprise(client, enterprise)
        canon = resolved["enterprise"] or enterprise
        calls = build_mcp_calls(canon, keyword_type)
        raw = await client.call_many(calls)
    raw["_resolved"] = resolved
    return normalize_mcp(raw)


# --------------------------------------------------------------------------- #
# Cache collection: read pre-existing atomic report JSONs (dry-run)
# --------------------------------------------------------------------------- #
def _metric_value(report: Mapping[str, Any], label: str) -> Optional[str]:
    for m in report.get("metrics", []):
        if isinstance(m, dict) and label in str(m.get("label", "")):
            return str(m.get("value", ""))
    return None


def _metric_int(report: Mapping[str, Any], label: str) -> Optional[int]:
    v = _metric_value(report, label)
    return _int(v.replace(",", "").replace("万", "").replace("%", "")) if v else None


def _collect_cache(skills_root: str, enterprise: str) -> Dict[str, Any]:
    """Load atomic report JSONs from reports_探迹/ and normalize."""
    root = pathlib.Path(skills_root)
    reports_dir = root / "reports_探迹"
    if not reports_dir.exists():
        # fall back to each atomic skill's output/ sample
        return normalize_reports({}, enterprise, resolved=False)
    reports: Dict[str, Any] = {}
    for p in sorted(reports_dir.glob("*.json")):
        try:
            reports[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return normalize_reports(reports, enterprise)


# --------------------------------------------------------------------------- #
# Normalization — both modes produce THIS structure
# --------------------------------------------------------------------------- #
def normalize_mcp(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize live MCP results into the unified cross-analysis structure."""
    resolved = raw.get("_resolved") or {}
    errors = {k: v["_error"] for k, v in raw.items() if isinstance(v, dict) and "_error" in v}

    # --- enterprise ---
    base_raw = raw.get("ent_base") or {}
    bi = base_raw.get("base_info") if isinstance(base_raw, dict) else {}
    if not isinstance(bi, dict):
        bi = {}
    base = {
        "企业名称": bi.get("name") or "-",
        "统一社会信用代码": bi.get("socialCreditCode") or bi.get("orgCode") or "-",
        "法定代表人": bi.get("legalRepresentative") or "-",
        "企业类型": bi.get("enterpriseType") or "-",
        "行业": _industry_text(bi.get("industry")),
        "注册资本": _amount(bi.get("regCapital")),
        "实缴资本": _amount(bi.get("realCapital") or bi.get("payAmountCount")),
        "成立日期": str(bi.get("foundTime") or "-"),
        "经营状态": bi.get("operStatus") or "-",
        "注册地址": bi.get("address") or _kv_addr(bi.get("addressValue")) or "-",
        "经营范围": _text(bi.get("business") or bi.get("businessScope"), limit=400) or "-",
    }
    # 实缴率：若实缴与注册资本都可量化则计算
    reg_v = _amount_num(bi.get("regCapital"))
    paid_v = _amount_num(bi.get("realCapital") or bi.get("payAmountCount"))
    if reg_v and paid_v is not None and reg_v > 0:
        base["资本实缴率"] = f"{paid_v / reg_v * 100:.1f}%"
    holders = _first_list(raw.get("ent_holder"))
    investments = _first_list(raw.get("ent_invest"))
    investments_total = _safe_total(raw.get("ent_invest")) or len(investments)
    persons = _first_list(raw.get("ent_person"))

    # --- risk ---
    rs = raw.get("risk_score") or {}
    rl = raw.get("risk_litigation") or {}
    rl = rl if isinstance(rl, dict) else {}
    # litigation: live MCP returns caKaitingList/caLiAnList etc. + summary fields
    ca_kaiting = _first_list(rl.get("caKaitingList") or rl.get("caseCount"))
    hearings_list = _first_list(raw.get("risk_hearings"))
    hearings_total = _safe_total(raw.get("risk_hearings")) or len(hearings_list)
    # penalties: MCP wraps records in {punishmentCount, punishmentList:[...]}
    penalties_raw = raw.get("risk_penalties") or {}
    if isinstance(penalties_raw, dict) and isinstance(penalties_raw.get("punishmentList"), list):
        penalties_count = _int(penalties_raw.get("punishmentCount"))
        penalties_list = [r for r in penalties_raw["punishmentList"] if isinstance(r, dict) and r.get("text") != "查询数据为空"]
        penalties_total = penalties_count or len(penalties_list)
    else:
        penalties_list = [r for r in _first_list(penalties_raw) if isinstance(r, dict) and r.get("text") != "查询数据为空"]
        penalties_total = _safe_total(penalties_raw) or len(penalties_list)
    # anomalies: MCP may nest {anomalyList:[...], anomalyCount} OR return {text:"查询数据为空"}
    anomalies_raw_raw = raw.get("risk_anomalies") or {}
    if isinstance(anomalies_raw_raw, dict) and anomalies_raw_raw.get("text") == "查询数据为空":
        anomalies_list = []
        anomalies_total = 0
    elif isinstance(anomalies_raw_raw, dict) and isinstance(anomalies_raw_raw.get("anomalyList"), list):
        anomalies_list = [a for a in anomalies_raw_raw["anomalyList"] if isinstance(a, dict)]
        anomalies_total = _int(anomalies_raw_raw.get("anomalyCount")) or len(anomalies_list)
    else:
        anomalies_list = [a for a in _first_list(anomalies_raw_raw) if isinstance(a, dict) and a.get("text") != "查询数据为空"]
        anomalies_total = _safe_total(anomalies_raw_raw) or len(anomalies_list)
    # restrictions: filter "查询数据为空"
    restrictions_raw = raw.get("risk_restrictions") or {}
    if isinstance(restrictions_raw, dict) and restrictions_raw.get("text") == "查询数据为空":
        restrictions_list = []
        restrictions_total = 0
    else:
        restrictions_list = [r for r in _first_list(restrictions_raw) if isinstance(r, dict) and r.get("text") != "查询数据为空"]
        restrictions_total = _safe_total(restrictions_raw) or len(restrictions_list)
    # mortgages: filter "查询数据为空"
    mortgages_raw = raw.get("risk_mortgage") or {}
    if isinstance(mortgages_raw, dict) and mortgages_raw.get("text") == "查询数据为空":
        mortgages_list = []
        mortgages_total = 0
    else:
        mortgages_list = [r for r in _first_list(mortgages_raw) if isinstance(r, dict) and r.get("text") != "查询数据为空"]
        mortgages_total = _safe_total(mortgages_raw) or len(mortgages_list)
    # litigation summary: prefer MCP total over list length
    hearings_n = hearings_total
    litigation = {
        "case_count": hearings_n or None,
        "as_defendant": _int(rl.get("asDefendantCount")),
        "as_plaintiff": _int(rl.get("asPlaintiffCount")),
        "recent_count": _int(rl.get("recentCaseCount")),
        "total_amount": _float(rl.get("totalAmount")),
        "hearings_count": hearings_n or None,
        "开庭公告数": hearings_n,
        "被执行人记录数": restrictions_total,
        "失信被执行人数": 0,
    }
    risk = {
        "score": _int(rs["risk_score"]) if isinstance(rs, dict) and rs.get("risk_score") is not None else (_int(rs.get("riskScore")) if isinstance(rs, dict) else None),
        "level": (rs["risk_level"] if isinstance(rs, dict) and rs.get("risk_level") else (rs.get("riskLevel") if isinstance(rs, dict) else None)),
        "credit_level": None,
        "oper_level": None,
        "litigation_level": None,
        "litigation": litigation,
        "court_hearings": hearings_list,
        "court_hearings_total": hearings_total,
        "penalties": penalties_list,
        "penalties_total": penalties_total,
        "anomalies": anomalies_list,
        "anomalies_total": len(anomalies_list),
        "restrictions": restrictions_list,
        "restrictions_total": restrictions_total,
        "mortgages": mortgages_list,
        "mortgages_total": mortgages_total,
        "investments_total": investments_total,
    }

    # --- operation ---
    os_ = raw.get("op_scale") or {}
    of = raw.get("op_financing") or {}
    ot = raw.get("op_trends") or {}
    operation = {
        "scale": {
            "staff": os_.get("enterpriseScale") if isinstance(os_, dict) else None,
            "turnover": os_.get("annualTurnover") if isinstance(os_, dict) else None,
        },
        "financing_count": _int(of.get("fpFinancingCount")) if isinstance(of, dict) else None,
        "financing_list": _first_list(of.get("fpFinancingList")) if isinstance(of, dict) else [],
        "trends": ot if isinstance(ot, dict) else {},
        "rankings": _first_list(raw.get("op_rankings")),
    }

    # --- patent (专利统计) ---
    patent_raw = raw.get("patent_stats") or {}
    if isinstance(patent_raw, dict) and patent_raw.get("text") == "查询数据为空":
        patent = {}
    else:
        patent_raw = patent_raw if isinstance(patent_raw, dict) else {}
        patent = {
            "patentCount": _int(patent_raw.get("patentCount")),
            "inventionAppPatentCount": _int(patent_raw.get("inventionAppPatentCount")),
            "inventionLicPatentCount": _int(patent_raw.get("inventionLicPatentCount")),
            "utilityModelPatentCount": _int(patent_raw.get("utilityModelPatentCount")),
            "appearanceDesignPatentCount": _int(patent_raw.get("appearanceDesignPatentCount")),
            "patentTypeAppTimeStat": _first_list(patent_raw.get("patentTypeAppTimeStat")),
            "patentTypePubTimeStat": _first_list(patent_raw.get("patentTypePubTimeStat")),
            "patentDivAppLegalStat": _first_list(patent_raw.get("patentDivAppLegalStat")),
            "patentTypeStat": patent_raw.get("patentTypeStat") or {},
        }

    # --- trademark (商标概况/统计) ---
    tm_profile_raw = raw.get("tm_profile") or {}
    tm_stats_raw = raw.get("tm_stats") or {}
    if isinstance(tm_profile_raw, dict) and tm_profile_raw.get("text") == "查询数据为空":
        trademark = {}
    else:
        tm_profile_raw = tm_profile_raw if isinstance(tm_profile_raw, dict) else {}
        tm_stats_raw = tm_stats_raw if isinstance(tm_stats_raw, dict) else {}
        trademark = {
            "tmCount": _int(tm_profile_raw.get("tmCount")),
            "tmValidNumber": _int(tm_profile_raw.get("tmValidNumber")),
            "tmInvalidNumber": _int(tm_profile_raw.get("tmInvalidNumber")),
            "tmNumberThisYear": _int(tm_profile_raw.get("tmNumberThisYear")),
            "tmTypeList": _first_list(tm_profile_raw.get("tmTypeList")),
            "tmStatusList": _first_list(tm_profile_raw.get("tmStatusList")),
            "tmStatusStat": tm_profile_raw.get("tmStatusStat") or {},
            "tmAppTimeStat": _first_list(tm_stats_raw.get("tmAppTimeStat")),
            "tmRegTimeStat": _first_list(tm_stats_raw.get("tmRegTimeStat")),
            "tmTypeStats": _first_list(tm_stats_raw.get("tmTypeStats")),
        }

    # --- bidding (招投标) ---
    bid_stats_raw = raw.get("bid_win_stats") or {}
    bid_info_raw = raw.get("bid_info") or {}
    if isinstance(bid_stats_raw, dict) and bid_stats_raw.get("text") == "查询数据为空":
        bidding = {}
    else:
        bid_stats_raw = bid_stats_raw if isinstance(bid_stats_raw, dict) else {}
        bidding_info_list = _first_list(bid_info_raw)
        bidding_info_list = [b for b in bidding_info_list if isinstance(b, dict) and b.get("text") != "查询数据为空"]
        bidding = {
            "winbidAmountStatList": _first_list(bid_stats_raw.get("winbidAmountStatList")),
            "winbidAreaStat": _first_list(bid_stats_raw.get("winbidAreaStat")),
            "winbidStatList": _first_list(bid_stats_raw.get("winbidStatList")),
            "winbidTrend": _first_list(bid_stats_raw.get("winbidTrend")),
            "bidding_info": bidding_info_list,
            "bidding_total": _safe_total(bid_info_raw) or len(bidding_info_list),
        }

    # --- news (舆情) ---
    news_raw = raw.get("news_stats") or {}
    if isinstance(news_raw, dict) and news_raw.get("text") == "查询数据为空":
        news = {}
    else:
        news_raw = news_raw if isinstance(news_raw, dict) else {}
        news = {
            "newsSentimentStats": news_raw.get("newsSentimentStats") or {},
            "sentimentLabelList": _first_list(news_raw.get("sentimentLabelList")),
            "newsSentimentTrend": _first_list(news_raw.get("newsSentimentTrend")),
        }

    # --- recruitment ---
    rt = raw.get("rec_trend") or {}
    rp = raw.get("rec_profile") or {}
    recruitment = {
        "current": _int(rt.get("recruitingCurrentCount")) if isinstance(rt, dict) else None,
        "last_3m": _int(rt.get("recruitingLastThreeMonthCount")) if isinstance(rt, dict) else None,
        "avg_salary": rt.get("recruitingAvgWorkingSalary") if isinstance(rt, dict) else None,
        "welfare": _first_list(rp.get("recruitingWelfareList") or rp.get("welfareList")) if isinstance(rp, dict) else [],
    }

    return _wrap(resolved, errors, "live", enterprise=resolved.get("enterprise", ""),
                 base=base, holders=holders, investments=investments, persons=persons,
                 risk=risk, operation=operation, patent=patent, trademark=trademark,
                 bidding=bidding, news=news, recruitment=recruitment)


def normalize_reports(reports: Mapping[str, Any], enterprise: str, *, resolved: bool = True) -> Dict[str, Any]:
    """Normalize cached atomic report JSONs into the unified structure (dry-run)."""
    er = reports.get("enterprise-report", {}) if isinstance(reports, dict) else {}
    rr = reports.get("enterprise-risk-report", {}) if isinstance(reports, dict) else {}
    opr = reports.get("enterprise-operation-report", {}) if isinstance(reports, dict) else {}
    pr = reports.get("patent-report", {}) if isinstance(reports, dict) else {}
    tr = reports.get("trademark-report", {}) if isinstance(reports, dict) else {}
    br = reports.get("bidding-report", {}) if isinstance(reports, dict) else {}
    nr = reports.get("news-report", {}) if isinstance(reports, dict) else {}
    recr = reports.get("recruitment-report", {}) if isinstance(reports, dict) else {}

    def _ca(report: Mapping[str, Any]) -> Mapping[str, Any]:
        return report.get("core_analysis", {}) if isinstance(report, dict) else {}

    # enterprise
    ec = _ca(er)
    base = _kv_to_dict(ec.get("enterprise_base")) if isinstance(ec.get("enterprise_base"), list) else (ec.get("enterprise_base") or {})
    for mlabel, bkey in [("资本实缴率", "资本实缴率"), ("注册资本", "注册资本"), ("实缴资本", "实缴资本")]:
        mv = _metric_value(er, mlabel)
        if mv and not base.get(bkey):
            base[bkey] = mv
    holders = ec.get("holders") or []
    investments = ec.get("investments") or []
    persons = ec.get("key_persons") or []

    # risk
    rc = _ca(rr)
    risk = {
        "score": _metric_int(rr, "风险评分"),
        "level": _metric_value(rr, "风险等级"),
        "credit_level": None,
        "oper_level": None,
        "litigation_level": None,
        "litigation": _kv_to_dict(rc.get("litigation_overview")),
        "court_hearings": rc.get("court_hearings") or [],
        "penalties": rc.get("penalties") or [],
        "anomalies": rc.get("business_anomalies") or [],
        "restrictions": rc.get("consumption_restrictions") or [],
        "mortgages": rc.get("chattel_mortgage") or [],
        "investments_total": len(investments),
    }

    # operation
    opc = _ca(opr)
    operation = {
        "scale": _kv_to_dict(opc.get("business_scale")),
        "financing_count": _metric_int(opr, "融资次数"),
        "financing_list": opc.get("financing_info") or [],
        "trends": _kv_to_dict(opc.get("company_trends")),
        "rankings": opc.get("enterprise_rankings") or [],
    }

    # patent
    pc = _ca(pr)
    patent = {
        "patentCount": _metric_int(pr, "专利数量"),
        "inventionAppPatentCount": None,
        "inventionLicPatentCount": None,
        "utilityModelPatentCount": None,
        "appearanceDesignPatentCount": None,
        "patentTypeAppTimeStat": _first_list(pc.get("patentTypeAppTimeStat")),
        "patentTypePubTimeStat": _first_list(pc.get("patentTypePubTimeStat")),
        "patentDivAppLegalStat": _first_list(pc.get("patentDivAppLegalStat")),
        "patentTypeStat": pc.get("patentTypeStat") or {},
    }

    # trademark
    tc = _ca(tr)
    trademark = {
        "tmCount": _metric_int(tr, "商标数量"),
        "tmValidNumber": _metric_int(tr, "有效商标数"),
        "tmInvalidNumber": None,
        "tmNumberThisYear": None,
        "tmTypeList": _first_list(tc.get("tmTypeList")),
        "tmStatusList": _first_list(tc.get("tmStatusList")),
        "tmStatusStat": _kv_to_dict(tc.get("tmStatusStat")),
        "tmAppTimeStat": _first_list(tc.get("tmAppTimeStat")),
        "tmRegTimeStat": _first_list(tc.get("tmRegTimeStat")),
        "tmTypeStats": _first_list(tc.get("tmTypeStats")),
    }

    # bidding
    bc = _ca(br)
    bidding = {
        "winbidAmountStatList": _first_list(bc.get("winbidAmountStatList")),
        "winbidAreaStat": _first_list(bc.get("winbidAreaStat")),
        "winbidStatList": _first_list(bc.get("winbidStatList")),
        "winbidTrend": _first_list(bc.get("winbidTrend")),
        "bidding_info": bc.get("bidding_info") or [],
        "bidding_total": _metric_int(br, "招投标参与数"),
    }

    # news
    nc = _ca(nr)
    news = {
        "newsSentimentStats": _kv_to_dict(nc.get("newsSentimentStats")),
        "sentimentLabelList": _first_list(nc.get("sentimentLabelList")),
        "newsSentimentTrend": _first_list(nc.get("newsSentimentTrend")),
    }

    # recruitment
    recc = _ca(recr)
    recruitment = {
        "current": _metric_int(recr, "当前招聘人数"),
        "last_3m": _metric_int(recr, "近三月招聘人数"),
        "avg_salary": _metric_value(recr, "平均薪酬"),
        "welfare": recc.get("benefit_tags") or [],
    }

    resolved_meta = {"keyword": enterprise, "enterprise": enterprise, "resolved": resolved,
                     "reason": "缓存报告（dry-run）" if not resolved else "已有报告"}
    return _wrap(resolved_meta, {}, "cache", enterprise=enterprise,
                 base=base, holders=holders, investments=investments, persons=persons,
                 risk=risk, operation=operation, patent=patent, trademark=trademark,
                 bidding=bidding, news=news, recruitment=recruitment)


def _kv_to_dict(value: Any) -> Dict[str, Any]:
    """Convert a [{字段/名称, 内容/值}] KV list (report style) to a plain dict."""
    out: Dict[str, Any] = {}
    if isinstance(value, list):
        for row in value:
            if isinstance(row, dict):
                k = row.get("字段") or row.get("名称") or row.get("指标") or row.get("维度") or ""
                v = row.get("内容") or row.get("值") or row.get("数量") or row.get("占比") or row.get("值/说明") or ""
                if k:
                    out[str(k)] = v
    elif isinstance(value, dict):
        out = dict(value)
    return out


def _pick(d: Any, *keys: str) -> Any:
    """Tolerant field extractor."""
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if v not in (None, "", "-", []):
            return v
    return None


def _wrap(resolved: Mapping[str, Any], errors: Mapping[str, Any], source: str, **domain: Any) -> Dict[str, Any]:
    enterprise = domain.pop("enterprise", resolved.get("enterprise", ""))
    return {
        "_meta": {
            "enterprise": enterprise,
            "resolved": dict(resolved),
            "source": source,  # "live" | "cache"
            "errors": dict(errors),
        },
        "enterprise": {
            "base": domain.get("base", {}),
            "holders": domain.get("holders", []),
            "investments": domain.get("investments", []),
            "persons": domain.get("persons", []),
        },
        "risk": domain.get("risk", {}),
        "operation": domain.get("operation", {}),
        "patent": domain.get("patent", {}),
        "trademark": domain.get("trademark", {}),
        "bidding": domain.get("bidding", {}),
        "news": domain.get("news", {}),
        "recruitment": domain.get("recruitment", {}),
    }


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def collect_direct(enterprise: str, keyword_type: str, *, dry_run: bool, skills_root: str) -> Dict[str, Any]:
    """Collect multi-source data: live MCP (default) or cached reports (dry-run)."""
    if dry_run:
        return _collect_cache(skills_root, enterprise)
    try:
        return asyncio.run(_collect_live(enterprise, keyword_type))
    except MultiMcpError as exc:
        # No MCP connection available — gracefully degrade to cached reports.
        print(f"⚠️  MCP 连接不可用 ({exc})，回退到缓存报告模式", file=__import__("sys").stderr)
        return _collect_cache(skills_root, enterprise)
