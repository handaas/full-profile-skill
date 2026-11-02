---
name: full-profile-report
description: Use for generating a 企业综合画像报告 (企业全维度画像, 全面体检, 360度报告, 综合分析, 全维度评估). Directly connects to 8 MCP servers, confirms the subject, and produces an evidence-bound factual profile without unvalidated custom scores.
---

# 企业综合画像报告

## 定位

企业全面体检 skill。**直接连接 8 个 MCP server**（工商 / 风险 / 经营 / 专利 / 商标 / 标讯 / 舆情 / 招聘），获取全维度原始数据，运行**8 维交叉分析**。

### 执行路径边界

- 默认 direct-mcp 路径仅发布可追溯事实和上游原始评分口径；不发布未经验证的自定义综合分、专项分或由数量直接推导的强弱结论。
- `--reports-dir`、`--skills-dir`、`--no-direct-mcp` 会进入兼容保留的旧 `fusion_engine` 路径。该路径可能包含历史自定义评分，未完成本轮证据门禁验证，**不得用于企业评级、投资或低风险决策**。
- 两条路径不可混同；本说明中的主体确认、去自定义评分和司法冲突门禁仅保证默认 direct-mcp 最终出口。
- 默认 HTML / Markdown / JSON 为 facts-only 输出，不生成雷达图、评分仪表盘或综合画像分；空明细时连同“核心分析”标题和目录项一起跳过。
- 企业风险 MCP 返回的原始风险分只作为明确标注来源的事实字段，不是本报告综合评级；存在司法暴露时不展示正向风险等级。

- MCP 返回的嵌套 JSON 字符串（如金额 `{"coinType":"人民币","value":430000000.0}`、地址 `{"city":"杭州市",...}`）必须解析为可读文本（如"4.30 亿 人民币"、"浙江省杭州市"），绝不在报告正文、表格或指标中输出原始 JSON 字符串。
- 报告所有章节标题、指标卡标签必须用中文；`core_analysis.sections` 的 `title` 字段必须中文，不可显示英文 key（如 `holders`、`investments`）。
- 指标值必须可读化：金额格式为"X 亿/万 + 币种"，地址拼接省市区，比率显示百分号。详见 `references/report-output.md` 的「数据格式约束」。

## 查询成本与分页纪律（必读）

1. **每次调用、每一页都计费。** 想算总页数/总数不是拉全量的授权；没有明确预算时绝不自动翻到 total。
2. **先规划后调用。** 动手前先明确：报告需要哪些结论、每个结论需要哪些数据维度、要调哪些工具和参数、每接口必要页数、最大调用预算。总数未知时，第一页明细既是数据也是 total 发现，**同一页绝不付第二次费**。
3. **优先统计/画像/聚合接口。** 能由统计口径回答的不用明细接口；只取结论、图表、代表性记录或明确"全量/计数"需求所需的明细。只有用户真要求综合报告才跑全管线，绝不"因为工具存在就全调"。
4. **用 schema 允许且合理的大 pageSize，够了就停。** 在明确预算内取到所需证据/样本即停止；追加调用必须来自"缺结论"，而不是"想填满所有章节"。不得用样本分布冒充全量结论来省调用。
5. **同一任务内复用相同请求。** 相同 tool+参数只调一次（含第一页规划数据，一律复用）；渲染只用已落盘 JSON，不重跑 compose/MCP；不自动重试、不重复取统计/明细、不并行取相同数据。补充查询必须先列出具体缺口并复用已有记录。
6. **total_pages/remaining_pages 是按请求 pageSize 的估算。** 预算内短页但上游仍有剩余记录时继续翻页；只有稳定有效的 total 与实际扫描条数相等才算"完整"。错误、提前空页、重复页、total 漂移/缺失、超量都算"不完整"。预算或样本截停是部分采集，**绝不宣称全量**。禁止无关工具/维度调用。

预算不足以支撑关键结论时：先在报告中说明证据缺口与预计需要的额外页数，再请求扩大授权；不得悄悄降级结论，也不得擅自扩大计费范围。

### 分页实现口径

- `compose_fusion_report.py` 新增 `--max-pages N`（正整数，默认 1 页）；每接口的分页明细页数预算，非法值在任何真实调用前被拒绝。
- 直连模式下，分页明细接口走统一的 total 驱动采集：第 1 页同时用于分析与上游 total 发现，不重复计费；后续页仅在预算内按 total 规划翻页。
  - `risk_insight_court_hearings`、`risk_insight_consumption_restrictions`、`bid_bigdata_bidding_info`：schema 单页上限 ≤50 条；`operation_insight_enterprise_rankings`：schema 单页上限 ≤10 条。
- 报告 `data_source.pagination` 与 `data_source.call_usage` 会披露每接口的上游 total、预计页数、实际请求页数、取得/未纳入条数与停止原因；`abstract`/`summary`/`caliber.limit` 同步可见。
- 模糊查询主体确认（`enterprise_get_keyword_search`）不做分页；统计/画像接口（`risk_insight_litigation_risk_profile`、`risk_insight_penalties`、`risk_insight_business_anomalies`、`risk_insight_chattel_mortgage`、`patent_bigdata_patent_stats`、`trademark_bigdata_trademark_profile`/`_stats`、`news_bigdata_news_stats`、`bid_bigdata_bid_win_stats`、`operation_insight_financing_info`、`operation_insight_business_scale`、`operation_insight_company_trends`、`recruitment_trend`、`recruitment_employer_profile` 等）单次调用不翻页；`enterprise_get_enterprise_invest_info` 与 `enterprise_get_enterprise_main_person_info` 返回 resultList+total 但工具参数不含分页，保持单次调用并在报告中披露 total 与未纳入条数。

## 直连的 8 个 MCP

| MCP server | 工具 | 数据用途 |
| --- | --- | --- |
| enterprise-mcp-server | base_info / holders / invest / main_person | 工商基础、股权、关联方 |
| enterprise-risk-mcp-server | score / litigation / hearings / penalties / anomalies / restrictions / mortgage | 风险全景、诉讼结构 |
| enterprise-operation-mcp-server | business_scale / financing / trends / rankings | 经营规模、资本运作 |
| patent-mcp-server | patent_stats | 专利储备、创新实力 |
| trademark-mcp-server | trademark_profile / trademark_stats | 商标布局、品牌保护 |
| bidding-mcp-server | bid_win_stats / bidding_info | 中标能力、市场活跃度 |
| news-mcp-server | news_stats | 舆情健康、情感分布 |
| recruitment-mcp-server | trend / employer_profile | 招聘活跃度、人才储备 |

## 交叉分析产出

| 产出 | 说明 |
| --- | --- |
| 事实指标 | 工商、司法、经营、专利、商标、标讯、舆情和招聘的可追溯公开字段 |
| 综合边界 | 主体确认状态、人工司法核验项、行业适用性和数据缺口；不生成自定义评级 |
| 跨维度洞察 | 创新×市场 / 风险×规模 / 品牌×创新 / 扩张×风险 |

## 脚本速查

```bash
# 默认：直连多 MCP（8 个 server，串行建连避免并发崩溃；明细接口按默认 1 页预算采集并披露 total）
python scripts/compose_fusion_report.py --enterprise "某公司" --output output/全维度.json --report-output output/全维度.html
# 明确扩大明细页数预算（每页计费，先规划结论与维度再定）
python scripts/compose_fusion_report.py --enterprise "某公司" --max-pages 3 --output output/全维度.json --report-output output/全维度.html
# dry-run
python scripts/compose_fusion_report.py --enterprise "某公司" --dry-run --output output/全维度.json --report-output output/全维度.html
```

## 输出字段

- `verdict` — 主体确认、司法人工核验项和数据缺口，不提供自定义综合评级。
- `specialty_scores` — 默认 direct-mcp 路径固定为空。
- `metrics` — 可追溯事实指标；上游原始风险分不等于本报告综合评分。
- `core_analysis.sections` — 按有效数据动态生成，不含 gauge；空时 HTML/Markdown 与目录不显示“核心分析”。
- `data_source` — MCP 来源、调用错误、生成时间与质量覆盖情况。

### 付费主体校验与批次

- 主体模糊查询也是付费请求，计入本任务调用次数并进入同一请求复用范围；存在多个候选或无法确认时立即停止其他维度查询，返回候选名称供选择，不能为不确定主体继续购买数据。显式企业标识不额外做名称模糊查询。
- 可分页标讯、开庭、限高和渠道明细采用接口允许的 50 条批次；企业上榜保持 schema 上限 10 条，减少相同采集范围的分页调用。预算仍为每数据源最多页数，不是全报告总调用次数。
- 招聘画像已包含趋势汇总所需字段，只购买一次同主体统计结果，在本地复用，不再另查招聘趋势工具。
