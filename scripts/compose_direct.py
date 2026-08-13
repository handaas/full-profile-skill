#!/usr/bin/env python3
"""Direct multi-MCP composition for the full-profile report.

Connects to 8 MCP servers (or reads cached reports for dry-run), runs
cross-domain analysis across all 8 dimensions, and assembles a comprehensive
enterprise profile with cross-dimensional insights, an 8-axis specialty score
matrix, and a structured positioning verdict.

Output payload follows the unified JSON skeleton so render_report.py renders it
unchanged.
"""
from __future__ import annotations

import datetime as dt
import sys
from typing import Any, Dict, List, Mapping

import mcp_orchestration as orch
import cross_analysis as xa
from cross_analysis import _pick, _i, _base, _risk, _operation, _patent, _trademark, _bidding, _news, _recruitment, _holders, _investments

REPORT_TYPE = "full_profile_direct"
BANNER = "企业综合画像报告"

# --------------------------------------------------------------------------- #
# Per-domain detail extractors
# --------------------------------------------------------------------------- #
_BASE_FIELDS = [
    ("企业名称", ("企业名称", "name", "名称")),
    ("统一社会信用代码", ("统一社会信用代码", "socialCreditCode", "scCode", "信用代码")),
    ("法定代表人", ("法定代表人", "legalRepresentative", "法人代表")),
    ("企业类型", ("企业类型", "enterpriseType")),
    ("行业", ("行业", "industry", "industryName")),
    ("注册资本", ("注册资本", "regCapital", "regCapitalValue")),
    ("实缴资本", ("实缴资本", "realCapital", "paidInCapital")),
    ("成立日期", ("成立日期", "foundTime", "成立时间")),
    ("经营状态", ("经营状态", "operStatus")),
    ("注册地址", ("注册地址", "address", "addressValue")),
    ("经营范围", ("经营范围", "businessScope", "business")),
]


def _base_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    base = _base(data)
    out: Dict[str, str] = {}
    for label, keys in _BASE_FIELDS:
        v = _pick(base, *keys)
        if v not in (None, "", "-"):
            out[label] = str(v)
    rate = _pick(base, "资本实缴率", "实缴率")
    if rate:
        out["资本实缴率"] = str(rate)
    return out


_RISK_DIMS = [
    ("行政处罚", "penalties"), ("经营异常", "anomalies"), ("限制高消费", "restrictions"),
    ("开庭公告", "court_hearings"), ("动产抵押", "mortgages"), ("严重违法", "serious_violations"),
]


def _risk_dim_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    risk = _risk(data)
    rows = []
    for label, key in _RISK_DIMS:
        val = risk.get(key)
        if val:
            total_key = key + "_total"
            count = risk.get(total_key) or len(val) if isinstance(val, list) else 1
            rows.append({"风险维度": label, "记录数": str(count)})
    return rows


def _hearing_rows(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for h in (_risk(data).get("court_hearings") or [])[:20]:
        if not isinstance(h, dict):
            continue
        rows.append({
            "案由": str(_pick(h, "case_reason", "caseReason", "案由") or "-"),
            "法院": str(_pick(h, "publishUnit", "court", "法院") or "-"),
            "公告类型": str(_pick(h, "caseType", "公告类型") or "开庭公告"),
        })
    return rows


def _patent_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    pat = _patent(data)
    out: Dict[str, str] = {}
    for label, key in [("专利总数", "patentCount"), ("发明申请", "inventionAppPatentCount"),
                       ("发明授权", "inventionLicPatentCount"), ("实用新型", "utilityModelPatentCount"),
                       ("外观设计", "appearanceDesignPatentCount")]:
        v = _i(pat.get(key))
        if v is not None:
            out[label] = str(v)
    return out


def _trademark_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    tm = _trademark(data)
    out: Dict[str, str] = {}
    for label, key in [("商标总数", "tmCount"), ("类别数", "tmTypeCount"), ("有效商标", "validTmCount")]:
        v = _i(tm.get(key)) or _pick(tm, key)
        if v not in (None, "", "-"):
            out[label] = str(v)
    tm_types = tm.get("tmTypeList") or []
    if tm_types:
        out["覆盖类别"] = "、".join(str(t) for t in tm_types[:8])
    return out


def _bidding_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    bid = _bidding(data)
    out: Dict[str, str] = {}
    for label, key in [("招投标参与", "bidding_total"), ("中标次数", "winbidCount"), ("招标次数", "tenderCount")]:
        v = _i(bid.get(key))
        if v:
            out[label] = str(v)
    return out


def _news_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    news = _news(data)
    out: Dict[str, str] = {}
    stats = news.get("sentiment_stats") or {}
    for label, key in [("正面舆情", "positive"), ("负面舆情", "negative"), ("中立舆情", "neutral")]:
        v = _i(stats.get(key))
        if v is not None:
            out[label] = str(v)
    return out


def _operation_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    op = _operation(data)
    scale = op.get("scale") or {}
    out: Dict[str, str] = {}
    for label, keys in [("人员规模", ("staff", "人员规模", "enterpriseScale")), ("年营业额", ("turnover", "年营业额", "annualTurnover"))]:
        v = _pick(scale, *keys)
        if v not in (None, "", "-"):
            out[label] = str(v)
    fin_n = _i(op.get("financing_count"))
    if fin_n is not None:
        out["融资轮次"] = str(fin_n)
    rankings = op.get("rankings") or []
    if rankings:
        out["上榜记录"] = str(len(rankings))
    return out


def _recruitment_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    rec = _recruitment(data)
    out: Dict[str, str] = {}
    for label, key in [("当前在招", "current"), ("近三月招聘", "last_3m")]:
        v = _i(rec.get(key))
        if v is not None:
            out[label] = str(v)
    sal = rec.get("avg_salary")
    if sal not in (None, "", "-"):
        try:
            out["平均薪酬"] = f"{float(str(sal).replace(',', '')):.0f} 元/月"
        except (TypeError, ValueError):
            out["平均薪酬"] = str(sal)
    welfare = rec.get("welfare") or []
    if welfare:
        out["福利项数"] = str(len(welfare))
    return out


# --------------------------------------------------------------------------- #
# Payload assembly
# --------------------------------------------------------------------------- #
def build_direct_payload(enterprise: str, keyword_type: str, *, dry_run: bool, skills_root: str) -> Dict[str, Any]:
    data = orch.collect_direct(enterprise, keyword_type, dry_run=dry_run, skills_root=skills_root)
    meta = data.get("_meta") or {}
    resolved = meta.get("resolved") or {}
    canon = resolved.get("enterprise") or enterprise
    errors = meta.get("errors") or {}
    source_mode = "live_mcp" if meta.get("source") == "live" else "cached_reports"

    if errors:
        for k, msg in list(errors.items())[:5]:
            print(f"⚠️  工具调用失败 [{k}]: {msg[:120]}", file=sys.stderr)

    cross = xa.analyze(data)
    verdict = cross["verdict"]
    scores = cross["specialty_scores"]

    sections: List[Dict[str, Any]] = []
    core: Dict[str, Any] = {}

    def _add(spec: Dict[str, Any], body: Any) -> None:
        key = spec["key"]
        if spec.get("kind") == "radar":
            sections.append(spec)
            if body:
                core[key] = body
            return
        if body not in (None, "", [], {}):
            sections.append(spec)
            core[key] = body

    # verdict gauge — paired with radar
    if scores.get("average") is not None:
        _add({"key": "fp_verdict_gauge", "title": "综合画像评分", "kind": "gauge",
              "chart": {"value_key": "综合评分", "level_key": "综合定位", "max": 100},
              "note": f"综合定位：{verdict['recommendation']}",
              "pair_with": "fp_radar"},
             {"综合评分": scores["average"], "综合定位": verdict["level"]})

    # specialty radar — paired with gauge
    valid_scores = [(s["label"], s["score"]) for s in scores["items"] if s["score"] is not None]
    if len(valid_scores) >= 3:
        dim_names = " / ".join(l for l, _ in valid_scores)
        _add({"key": "fp_radar", "title": "全维度专项评分雷达", "kind": "radar",
              "chart": {"indicators": [{"name": l, "max": 100} for l, _ in valid_scores],
                        "series": [{"name": "专项评分", "value": [v for _, v in valid_scores]}]},
              "note": f"跨维度交叉评分（{len(valid_scores)} 维）：{dim_names}"},
             {})

    # 工商基础
    _add({"key": "fp_base", "title": "工商基础信息", "kind": "kv", "note": "工商登记 + 经营范围"}, _base_kv(data))

    # cross-analysis sections (shareholders, investments, specialty matrix)
    for spec in cross["section_specs"]:
        _add(spec, cross["section_data"].get(spec["key"]))

    # 创新储备（专利 + 商标）
    pat_kv = _patent_kv(data)
    tm_kv = _trademark_kv(data)
    innovation_kv = {**pat_kv, **tm_kv}
    _add({"key": "fp_innovation", "title": "创新与知识产权", "kind": "kv",
          "note": "专利储备 + 商标布局，反映技术壁垒与品牌保护"}, innovation_kv)

    # 招投标表现
    _add({"key": "fp_bidding", "title": "招投标市场表现", "kind": "kv",
          "note": "中标/招标/采购参与，反映市场活跃度"}, _bidding_kv(data))

    # 舆情健康
    _add({"key": "fp_news", "title": "舆情健康度", "kind": "kv",
          "note": "正面/负面/中立情感分布"}, _news_kv(data))

    # 风险评分 gauge + 风险维度统计 — paired
    risk_score = _i(_risk(data).get("score"))
    if risk_score is not None:
        _add({"key": "fp_risk_gauge", "title": "综合风险评分", "kind": "gauge",
              "chart": {"value_key": "风险评分", "level_key": "风险等级", "max": 100},
              "note": "风险洞察综合评分（越低越好）",
              "pair_with": "fp_risk_dims"},
             {"风险评分": risk_score, "风险等级": _risk(data).get("level") or "-"})
    _add({"key": "fp_risk_dims", "title": "风险维度统计", "kind": "table",
          "note": "各风险维度记录数",
          "columns": [("风险维度", "风险维度"), ("记录数", "记录数")]}, _risk_dim_rows(data))

    # 风险明细
    _add({"key": "fp_hearings", "title": "开庭公告明细", "kind": "table",
          "note": f"共 {_risk(data).get('court_hearings_total') or len(_risk(data).get('court_hearings') or [])} 条（展示前 20 条）",
          "columns": [("案由", "案由"), ("法院", "法院"), ("公告类型", "公告类型")]}, _hearing_rows(data))

    # 经营
    _add({"key": "fp_operation", "title": "经营规模与资本运作", "kind": "kv",
          "note": "人员规模 / 营业额 / 融资 / 上榜"}, _operation_kv(data))

    # 招聘
    _add({"key": "fp_recruitment", "title": "招聘与扩张活跃度", "kind": "kv",
          "note": "招聘活跃度反映企业经营动能"}, _recruitment_kv(data))

    # Metrics
    metrics: List[Dict[str, Any]] = list(cross["metrics"])
    while len(metrics) % 4 != 0:
        metrics.append({"label": "-", "value": "-", "hint": ""})

    # Insights
    insights: List[Dict[str, Any]] = list(cross["insights"])

    # Representative records
    rep_records: List[Dict[str, str]] = []
    inv_total = _risk(data).get("investments_total") or len(_investments(data))
    if inv_total:
        rep_records.append({"维度": "对外投资", "关键记录": f"{inv_total} 家关联企业"})
    ls = xa._litigation_summary(data)
    if ls["executed"]:
        rep_records.append({"维度": "执行风险", "关键记录": f"被执行记录 {ls['executed']} 条"})
    if risk_score is not None:
        rep_records.append({"维度": "风险评级", "关键记录": f"风险评分 {risk_score}（{_risk(data).get('level') or '-'}）"})
    patent_count = _i(_patent(data).get("patentCount"))
    if patent_count:
        rep_records.append({"维度": "创新储备", "关键记录": f"专利 {patent_count} 件"})
    fin_n = _i(_operation(data).get("financing_count"))
    if fin_n:
        rep_records.append({"维度": "资本运作", "关键记录": f"已完成 {fin_n} 轮融资"})
    if not rep_records:
        rep_records.append({"维度": "数据状态", "关键记录": "多维数据覆盖，详见各章节"})

    n_sources = sum(1 for d in (data.get("enterprise"), data.get("risk"), data.get("operation"),
                                data.get("patent"), data.get("trademark"), data.get("bidding"),
                                data.get("news"), data.get("recruitment")) if d)
    abstract_parts = [
        f"本报告以「{canon}」为分析对象，直接聚合工商、风险、经营、创新、商标、招投标、舆情、招聘 {n_sources} 大维度数据源，",
    ]
    if scores.get("average") is not None:
        abstract_parts.append(f"综合评分 {scores['average']}（{verdict['level']}）。")
    if verdict["blockers"]:
        abstract_parts.append(f"阻断项：{'、'.join(verdict['blockers'])}。")
    abstract_parts.append(verdict["summary"])
    abstract = "".join(abstract_parts)

    populated = sum(1 for s in sections if core.get(s["key"]) not in (None, "", [], {}))
    quality = {
        "total_sections": len(sections),
        "populated_sections": populated,
        "empty_sections": len(sections) - populated,
        "coverage_pct": round(populated / max(1, len(sections)) * 100),
        "data_sources": n_sources,
        "cross_insights": len(insights),
    }

    return {
        "report_type": REPORT_TYPE,
        "title": f"{canon} 企业综合画像报告",
        "banner": BANNER,
        "subject": {"enterprise": canon, "match_raw": enterprise, "resolved": resolved.get("resolved", False),
                    "resolve_reason": resolved.get("reason", "")},
        "abstract": abstract,
        "summary": abstract,
        "executive_summary": [verdict["summary"]] + [i["interpretation"] for i in insights[:4]],
        "verdict": verdict,
        "specialty_scores": scores,
        "metrics": metrics,
        "caliber": {
            "match_target": canon,
            "match_type": f"全维度综合画像（直接聚合 {n_sources} 个 MCP）",
            "data_scope": f"覆盖 {n_sources}/8 大数据源，{len(sections)} 个明细章节，{len(insights)} 条跨维度洞察",
            "products": ["企业大数据", "企业风险洞察", "企业经营分析", "专利大数据", "商标大数据", "标讯大数据", "舆情大数据", "招聘大数据"],
            "limit": "综合画像基于多维公开数据交叉分析；建议结合行业调研与财务审计综合判断。",
        },
        "core_analysis": {**core, "sections": sections},
        "representative_records": rep_records,
        "insights": insights,
        "data_source": {
            "mcp_server": f"{n_sources} MCP（工商/风险/经营/创新/商标/招投标/舆情/招聘）",
            "mcp_servers": list(__import__("multi_mcp_client").SERVER_REGISTRY.values()),
            "mode": source_mode,
            "dry_run": dry_run,
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "quality_report": quality,
            "tool_errors": list(errors.keys()) if errors else [],
        },
    }
