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
from typing import Any, Dict, List, Mapping, Optional

import mcp_orchestration as orch
import cross_analysis as xa
from cross_analysis import (
    _pick,
    _i,
    _base,
    _risk,
    _operation,
    _patent,
    _trademark,
    _bidding,
    _news,
    _recruitment,
    _investments,
)

REPORT_TYPE = "full_profile_direct"
BANNER = "企业综合画像报告"

# --------------------------------------------------------------------------- #
# Per-domain detail extractors
# --------------------------------------------------------------------------- #
_BASE_FIELDS = [
    ("企业名称", ("企业名称", "name", "名称")),
    (
        "统一社会信用代码",
        ("统一社会信用代码", "socialCreditCode", "scCode", "信用代码"),
    ),
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
    ("行政处罚", "penalties"),
    ("经营异常", "anomalies"),
    ("限制高消费", "restrictions"),
    ("开庭公告", "court_hearings"),
    ("动产抵押", "mortgages"),
    ("严重违法", "serious_violations"),
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
        case_no = _pick(h, "caseNo", "caseNumber", "caCaseNo", "案号")
        hearing_date = _pick(
            h,
            "hearingDate",
            "courtTime",
            "startDate",
            "publishDate",
            "noticeDate",
            "开庭日期",
            "发布日期",
        )
        rows.append(
            {
                "案号": str(case_no or "-"),
                "案由": str(_pick(h, "case_reason", "caseReason", "案由") or "-"),
                "法院": str(_pick(h, "publishUnit", "court", "法院") or "-"),
                "相关主体": str(
                    _pick(
                        h,
                        "enterpriseName",
                        "partyName",
                        "relatedEntity",
                        "当事人",
                        "相关主体",
                    )
                    or "-"
                ),
                "开庭/发布日期": str(hearing_date or "-"),
                "公告类型": str(_pick(h, "caseType", "公告类型") or "开庭公告"),
                "去重键状态": (
                    "案号+日期可用"
                    if case_no and hearing_date
                    else "缺少案号或日期，无法逐案去重"
                ),
            }
        )
    return rows


def _patent_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    pat = _patent(data)
    out: Dict[str, str] = {}
    for label, key in [
        ("专利总数", "patentCount"),
        ("发明申请", "inventionAppPatentCount"),
        ("发明授权", "inventionLicPatentCount"),
        ("实用新型", "utilityModelPatentCount"),
        ("外观设计", "appearanceDesignPatentCount"),
    ]:
        v = _i(pat.get(key))
        if v is not None:
            out[label] = str(v)
    return out


def _trademark_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    tm = _trademark(data)
    out: Dict[str, str] = {}
    for label, key in [
        ("商标总数", "tmCount"),
        ("类别数", "tmTypeCount"),
        ("有效商标", "validTmCount"),
    ]:
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
    for label, key in [
        ("招投标参与", "bidding_total"),
        ("中标次数", "winbidCount"),
        ("招标次数", "tenderCount"),
    ]:
        v = _i(bid.get(key))
        if v:
            out[label] = str(v)
    return out


def _news_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    news = _news(data)
    out: Dict[str, str] = {}
    stats = news.get("sentiment_stats") or {}
    for label, key in [
        ("正面舆情", "positive"),
        ("负面舆情", "negative"),
        ("中立舆情", "neutral"),
    ]:
        v = _i(stats.get(key))
        if v is not None:
            out[label] = str(v)
    return out


def _operation_kv(data: Mapping[str, Any]) -> Dict[str, str]:
    op = _operation(data)
    scale = op.get("scale") or {}
    out: Dict[str, str] = {}
    for label, keys in [
        ("人员规模", ("staff", "人员规模", "enterpriseScale")),
        ("年营业额", ("turnover", "年营业额", "annualTurnover")),
    ]:
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
def build_direct_payload(
    enterprise: str, keyword_type: str, *, dry_run: bool, skills_root: str,
    max_pages: Optional[int] = None,
) -> Dict[str, Any]:
    data = orch.collect_direct(
        enterprise, keyword_type, dry_run=dry_run, skills_root=skills_root,
        detail_max_pages=max_pages,
    )
    meta = data.get("_meta") or {}
    resolved = meta.get("resolved") or {}
    canon = resolved.get("enterprise") or enterprise
    errors = meta.get("errors") or {}
    source_mode = "live_mcp" if meta.get("source") == "live" else "cached_reports"
    identity_base = _base(data)
    identity_name = str(_pick(identity_base, "企业名称", "name", "名称") or "").strip()
    identity_code = str(
        _pick(identity_base, "统一社会信用代码", "socialCreditCode", "信用代码") or ""
    ).strip()
    subject_confirmed = (
        identity_name not in ("", "-")
        and identity_code not in ("", "-")
        and identity_name == canon
    )
    subject_reason = (
        "工商基础信息中的企业名称和统一社会信用代码已返回"
        if subject_confirmed
        else "工商基础信息未返回可核验企业名称及统一社会信用代码"
    )

    if errors:
        for k, msg in list(errors.items())[:5]:
            print(f"⚠️  工具调用失败 [{k}]: {msg[:120]}", file=sys.stderr)

    cross = xa.analyze(data)
    verdict = dict(cross["verdict"])
    scores: Dict[str, Any] = {"items": [], "average": None}
    factual_metric_labels = {
        "上游风险评分",
        "对外投资",
        "专利数量",
        "商标数量",
        "招投标参与",
        "舆情总数",
        "行政处罚",
        "注册资本",
        "资本实缴率",
        "融资轮次",
        "在招岗位",
        "限制高消费",
        "开庭公告",
        "经营异常",
        "股东数量",
    }
    cross["metrics"] = [
        dict(item)
        for item in cross["metrics"]
        if item.get("label") in factual_metric_labels
    ]
    cross["section_specs"] = [
        spec for spec in cross["section_specs"] if spec.get("key") != "fp_specialty"
    ]
    cross["section_data"].pop("fp_specialty", None)
    judicial_exposure = bool(
        (_i(_risk(data).get("court_hearings_total")) or 0)
        or (_i(_risk(data).get("restrictions_total")) or 0)
    )
    cross["insights"] = [
        item
        for item in cross["insights"]
        if "评分" not in str(item)
        and "观察值" not in str(item)
        and not (judicial_exposure and "上游风险等级" in str(item))
    ]
    verdict["specialty_average"] = None
    risk_level_display = (
        "上游原等级与司法记录冲突待核验"
        if judicial_exposure
        else (_risk(data).get("level") or "-")
    )
    verdict["key_concerns"] = [
        concern
        for concern in verdict.get("key_concerns", [])
        if concern != "创新实力偏弱"
    ]
    if not subject_confirmed:
        verdict.update(
            level="主体未确认",
            recommendation="仅作具名检索线索",
            summary="工商名称与统一社会信用代码未同时确认；返回内容不得归属于目标主体，不作综合画像评级。",
            blockers=[],
            key_concerns=["主体身份未确认"],
        )
    elif verdict.get("blockers"):
        verdict.update(
            level="不予综合评级",
            recommendation="人工司法核验",
            summary=f"发现需人工核验的司法或合规线索：{'、'.join(verdict['blockers'])}；不生成自定义综合或专项评分。",
        )
    else:
        verdict.update(
            level="事实观察（不评分）",
            recommendation="逐项人工核验",
            summary="报告仅整理公开事实和上游原始口径；缺少经验证模型与同行分母，不生成自定义综合或专项评分。",
        )
    risk_errors = any(str(key).startswith("risk_") for key in errors)
    evidence_gate = (
        subject_confirmed and xa._risk_evidence_known(data) and not risk_errors
    )
    if not evidence_gate:
        cross["insights"] = (
            []
            if not subject_confirmed
            else [
                item
                for item in cross["insights"]
                if not any(
                    word in str(item.get("feature") or "")
                    for word in ("风险", "司法", "诉讼")
                )
            ]
        )

    sections: List[Dict[str, Any]] = []
    core: Dict[str, Any] = {}
    attempted_sections = 0

    def _effective(value: Any) -> bool:
        if value in (None, "", "-", [], {}):
            return False
        if isinstance(value, dict):
            return any(_effective(v) for v in value.values())
        if isinstance(value, list):
            return any(_effective(v) for v in value)
        return True

    def _add(spec: Dict[str, Any], body: Any) -> None:
        nonlocal attempted_sections
        attempted_sections += 1
        key = spec["key"]
        if spec.get("kind") == "radar":
            sections.append(spec)
            if body:
                core[key] = body
            return
        if _effective(body):
            sections.append(spec)
            core[key] = body

    # 工商基础
    _add(
        {
            "key": "fp_base",
            "title": "工商基础信息",
            "kind": "kv",
            "note": "工商登记 + 经营范围",
        },
        _base_kv(data),
    )

    # cross-analysis sections (shareholders, investments, specialty matrix)
    for spec in cross["section_specs"]:
        _add(spec, cross["section_data"].get(spec["key"]))

    # 创新储备（专利 + 商标）
    pat_kv = _patent_kv(data)
    tm_kv = _trademark_kv(data)
    innovation_kv = {**pat_kv, **tm_kv}
    _add(
        {
            "key": "fp_innovation",
            "title": "专利与商标公开统计",
            "kind": "kv",
            "note": "专利与商标公开字段事实统计；未核验权属、有效性、质量或同行分母，不推断技术壁垒与品牌保护强度",
        },
        innovation_kv,
    )

    # 招投标表现
    _add(
        {
            "key": "fp_bidding",
            "title": "招投标公开统计",
            "kind": "kv",
            "note": "中标、招标与采购公开记录事实统计；未核验金额、履约结果或同行分母，不推断市场强弱",
        },
        _bidding_kv(data),
    )

    # 舆情健康
    _add(
        {
            "key": "fp_news",
            "title": "舆情健康度",
            "kind": "kv",
            "note": "正面/负面/中立情感分布",
        },
        _news_kv(data),
    )

    # 风险评分 gauge + 风险维度统计 — paired
    risk_score = _i(_risk(data).get("score"))
    if risk_score is not None:
        _add(
            {
                "key": "fp_risk_gauge",
                "title": "综合风险评分",
                "kind": "gauge",
                "chart": {"value_key": "风险评分", "level_key": "风险等级", "max": 100},
                "note": "上游风险评分原始口径；若与司法事件数量冲突，不作为低风险背书",
                "pair_with": "fp_risk_dims",
            },
            {"风险评分": risk_score, "风险等级": risk_level_display},
        )
    _add(
        {
            "key": "fp_risk_dims",
            "title": "风险维度统计",
            "kind": "table",
            "note": "各风险维度记录数",
            "columns": [("风险维度", "风险维度"), ("记录数", "记录数")],
        },
        _risk_dim_rows(data),
    )

    # 风险明细
    _add(
        {
            "key": "fp_hearings",
            "title": "开庭公告明细",
            "kind": "table",
            "note": f"报告总量 {_risk(data).get('court_hearings_total') if _risk(data).get('court_hearings_total') is not None else '未知'} 条（当前展示 {len(_hearing_rows(data))} 条）；保留上游案号/日期/主体用于人工去重，缺少案号或日期的记录无法逐案去重",
            "columns": [
                ("案号", "案号"),
                ("案由", "案由"),
                ("法院", "法院"),
                ("相关主体", "相关主体"),
                ("开庭/发布日期", "开庭/发布日期"),
                ("公告类型", "公告类型"),
                ("去重键状态", "去重键状态"),
            ],
        },
        _hearing_rows(data),
    )

    # 经营
    _add(
        {
            "key": "fp_operation",
            "title": "经营规模与资本运作",
            "kind": "kv",
            "note": "人员规模 / 营业额 / 融资 / 上榜",
        },
        _operation_kv(data),
    )

    # 招聘
    _add(
        {
            "key": "fp_recruitment",
            "title": "招聘公开统计",
            "kind": "kv",
            "note": "招聘平台公开字段事实统计；“当前/近三月”为上游窗口标签，未返回精确观察起止日期，不能单独证明经营动能、扩张结果或履约能力",
        },
        _recruitment_kv(data),
    )

    # Metrics
    metrics: List[Dict[str, Any]] = [
        item
        for item in cross["metrics"]
        if item.get("label") not in (None, "", "-")
        and item.get("value") not in (None, "", "-")
    ]
    for item in metrics:
        if item.get("label") == "上游风险评分":
            item["hint"] = "上游原始口径；若与司法事件数量冲突，不作为低风险背书"
            if judicial_exposure:
                item.pop("delta", None)
        elif item.get("label") == "专利数量":
            item["hint"] = "专利公开数量；归属、有效性和质量待核验"
        elif item.get("label") == "商标数量":
            item["hint"] = "商标公开数量；归属、状态和类别适用性待核验"
        elif item.get("label") == "招投标参与":
            item["hint"] = "公开记录数量；不代表市场强弱或履约结果"
        elif item.get("label") == "在招岗位":
            item["hint"] = "招聘平台公开数量；不代表经营动能或扩张结果"

    # Insights
    insights: List[Dict[str, Any]] = list(cross["insights"])

    # Representative records
    rep_records: List[Dict[str, str]] = []
    inv_total = _risk(data).get("investments_total") or len(_investments(data))
    if inv_total:
        rep_records.append({"维度": "对外投资", "关键记录": f"{inv_total} 家关联企业"})
    ls = xa._litigation_summary(data)
    if ls["executed"]:
        rep_records.append(
            {"维度": "执行风险", "关键记录": f"被执行记录 {ls['executed']} 条"}
        )
    if risk_score is not None:
        rep_records.append(
            {
                "维度": "风险评级",
                "关键记录": f"上游风险评分 {risk_score}（{risk_level_display}）",
            }
        )
    patent_count = _i(_patent(data).get("patentCount"))
    if patent_count:
        rep_records.append({"维度": "创新储备", "关键记录": f"专利 {patent_count} 件"})
    fin_n = _i(_operation(data).get("financing_count"))
    if fin_n:
        rep_records.append({"维度": "资本运作", "关键记录": f"已完成 {fin_n} 轮融资"})
    if not rep_records:
        rep_records.append({"维度": "数据状态", "关键记录": "多维数据覆盖，详见各章节"})

    n_sources = sum(
        1
        for d in (
            data.get("enterprise"),
            data.get("risk"),
            data.get("operation"),
            data.get("patent"),
            data.get("trademark"),
            data.get("bidding"),
            data.get("news"),
            data.get("recruitment"),
        )
        if _effective(d)
    )
    abstract_parts = [
        f"本报告以「{canon}」为分析对象，直接聚合工商、风险、经营、创新、商标、招投标、舆情、招聘 {n_sources} 大维度数据源，",
    ]
    if verdict["blockers"]:
        abstract_parts.append(f"阻断项：{'、'.join(verdict['blockers'])}。")
    abstract_parts.append(verdict["summary"])
    abstract = "".join(abstract_parts)

    if not subject_confirmed:
        sections = []
        core = {}
        metrics = []
        insights = []
        rep_records = [
            {
                "维度": "检索状态",
                "关键记录": "仅形成具名检索线索；工商名称与统一社会信用代码未同时确认，所有返回记录归属待核验",
            }
        ]
        abstract = (
            f"本报告仅记录对关键词「{enterprise}」的具名检索线索。"
            "工商名称与统一社会信用代码未同时确认，返回的风险、投资、专利、经营、商标、标讯、舆情及招聘记录不得归属于目标主体；不作综合画像评级。"
        )

    # Upstream risk scores may remain as explicitly sourced factual metrics,
    # but must never be promoted into this report's own gauge or "综合" chart.
    gauge_keys = {
        str(section.get("key") or "")
        for section in sections
        if section.get("kind") == "gauge"
    }
    if gauge_keys:
        sections = [section for section in sections if section.get("kind") != "gauge"]
        for key in gauge_keys:
            core.pop(key, None)
        attempted_sections = max(0, attempted_sections - len(gauge_keys))

    populated = sum(
        1
        for s in sections
        if s.get("kind") == "radar" or _effective(core.get(s["key"]))
    )
    quality = {
        "total_sections": attempted_sections,
        "populated_sections": populated,
        "empty_sections": attempted_sections - populated,
        "coverage_pct": round(populated / max(1, attempted_sections) * 100),
        "data_sources": n_sources,
        "cross_insights": len(insights),
    }

    report = {
        "report_type": REPORT_TYPE,
        "title": f"{canon} 企业综合画像报告",
        "banner": BANNER,
        "subject": {
            "enterprise": canon,
            "match_raw": enterprise,
            "resolved": subject_confirmed,
            "resolve_reason": subject_reason,
        },
        "abstract": abstract,
        "summary": abstract,
        "executive_summary": [verdict["summary"]]
        + [i["interpretation"] for i in insights[:4]],
        "verdict": verdict,
        "specialty_scores": scores,
        "metrics": metrics,
        "caliber": {
            "match_target": canon,
            "match_type": f"全维度综合画像（直接聚合 {n_sources} 个 MCP）",
            "data_scope": f"覆盖 {n_sources}/8 大数据源，{len(sections)} 个明细章节，{len(insights)} 条跨维度洞察",
            "products": [
                "企业大数据",
                "企业风险洞察",
                "企业经营分析",
                "专利大数据",
                "商标大数据",
                "标讯大数据",
                "舆情大数据",
                "招聘大数据",
            ],
            "limit": "未确认主体时所有返回仅为具名检索线索；已确认主体时也仅整理公开事实，不生成自定义评分，并需结合行业适用性、权属核验与财务审计判断。",
        },
        "core_analysis": {**core, "sections": sections},
        "representative_records": rep_records,
        "insights": insights,
        "data_source": {
            "mcp_server": f"{n_sources} MCP（工商/风险/经营/创新/商标/招投标/舆情/招聘）",
            "mcp_servers": list(
                __import__("multi_mcp_client").SERVER_REGISTRY.values()
            ),
            "mode": source_mode,
            "dry_run": dry_run,
            "generated_at": dt.datetime.now()
            .astimezone()
            .isoformat(timespec="seconds"),
            "quality_report": quality,
            "tool_errors": list(errors.keys()) if errors else [],
        },
    }
    if meta.get("source") == "live":
        from common import attach_pagination

        report = attach_pagination(report, meta.get("pagination_payloads") or {})
        call_usage = meta.get("call_usage")
        if isinstance(call_usage, dict) and call_usage:
            report["data_source"]["call_usage"] = call_usage
        if max_pages is None:
            budget_note = (
                "明细接口默认按单页预算采集（每接口仅请求第 1 页，该页同时用于分析与上游 total 发现，不重复计费）；"
                "如需更多明细页，请先规划所需结论与数据维度，再用 --max-pages N 明确页数预算；"
                "若预算不足以支撑关键结论，必须说明证据缺口与预计所需额外页数，不得悄悄降级结论或扩大计费范围。"
            )
            report["abstract"] += budget_note
            report["summary"] += budget_note
            report["caliber"]["limit"] += budget_note
        for note in (meta.get("schema_limited") or {}).values():
            report["abstract"] += note
            report["summary"] += note
            report["caliber"]["limit"] += note
    return report
