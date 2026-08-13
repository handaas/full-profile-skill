---
name: full-profile-report
description: Use for generating a 企业综合画像报告 (企业全维度画像, 全面体检, 360度报告, 综合分析, 全维度评估). Directly connects to 8 MCP servers (enterprise / risk / operation / patent / trademark / bidding / news / recruitment), pulls raw data, and runs cross-domain analysis across all 8 dimensions — innovation × market, risk × scale, brand × innovation, expansion × risk — producing a comprehensive enterprise profile with an 8-axis radar and positioning verdict. Trigger when users ask for "企业全维度画像", "全面体检", "360度报告", "综合分析", "全维度评估", "企业画像". Infer the enterprise name, connect MCPs, cross-analyze, and produce a radar + gauge + verdict report.
---

# 企业综合画像报告

## 定位

企业全面体检 skill。**直接连接 8 个 MCP server**（工商 / 风险 / 经营 / 专利 / 商标 / 标讯 / 舆情 / 招聘），获取全维度原始数据，运行**8 维交叉分析**。

- MCP 返回的嵌套 JSON 字符串（如金额 `{"coinType":"人民币","value":430000000.0}`、地址 `{"city":"杭州市",...}`）必须解析为可读文本（如"4.30 亿 人民币"、"浙江省杭州市"），绝不在报告正文、表格或指标中输出原始 JSON 字符串。
- 报告所有章节标题、指标卡标签必须用中文；`core_analysis.sections` 的 `title` 字段必须中文，不可显示英文 key（如 `holders`、`investments`）。
- 指标值必须可读化：金额格式为"X 亿/万 + 币种"，地址拼接省市区，比率显示百分号。详见 `references/report-output.md` 的「数据格式约束」。

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
| 8 维专项评分 | 创新实力 / 风险健康度 / 工商基础 / 市场活跃度 / 经营状况 / 数字化程度 / 品牌商标 / 人才储备 |
| 综合定位 | 全面领先型 / 均衡发展型 / 偏科型 / 需关注 |
| 跨维度洞察 | 创新×市场 / 风险×规模 / 品牌×创新 / 扩张×风险 |

## 脚本速查

```bash
# 默认：直连多 MCP（8 个 server，串行建连避免并发崩溃）
python scripts/compose_fusion_report.py --enterprise "某公司" --output output/全维度.json --report-output output/全维度.html
# dry-run
python scripts/compose_fusion_report.py --enterprise "某公司" --dry-run --output output/全维度.json --report-output output/全维度.html
```
