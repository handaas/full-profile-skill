# full-profile-skill：已验收示例

本目录只展示 **5 个完全通过的真实正向场景**（最低要求4例）。

每例均为真实、非空、非缓存调用；技术检查、独立业务检查和离线浏览器检查全部通过。不把空数据、报错处理或仅生成页面计作通过。历史验收记录保留在本地 test-records/；本目录的 HTML/Markdown 由原 JSON 重渲染，不代表重新查询或重新验收。

| 场景 | 真实使用需求 | 报告 |
|---|---|---|
| [上市科技企业综合画像](01-investment-profile/README.md) | 为宁德时代新能源科技股份有限公司生成工商、风险、经营、创新、品牌、市场、舆情和人才八维画像。 | [HTML](01-investment-profile/report.html) / [MD](01-investment-profile/report.md) / [JSON](01-investment-profile/report.json) |
| [高风险地产企业全面体检](02-high-risk-profile/README.md) | 对恒大地产集团有限公司做全面体检，重点观察风险、经营和市场活动之间的关系。 | [HTML](02-high-risk-profile/report.html) / [MD](02-high-risk-profile/report.md) / [JSON](02-high-risk-profile/report.json) |
| [创新品牌企业画像](03-ip-brand-leader/README.md) | 分析华为技术有限公司的专利、商标、经营、市场和人才协同情况。 | [HTML](03-ip-brand-leader/report.html) / [MD](03-ip-brand-leader/report.md) / [JSON](03-ip-brand-leader/report.json) |
| [人才扩张型企业画像](05-hiring-expansion/README.md) | 对比亚迪股份有限公司做八维画像，重点检查招聘扩张与经营、风险和创新是否匹配。 | [HTML](05-hiring-expansion/report.html) / [MD](05-hiring-expansion/report.md) / [JSON](05-hiring-expansion/report.json) |
| [平台企业综合画像](07-platform-company/README.md) | 分析京东科技信息技术有限公司的经营、创新、品牌、舆情和招聘信号。 | [HTML](07-platform-company/report.html) / [MD](07-platform-company/report.md) / [JSON](07-platform-company/report.json) |

- [逐例验收结果](results.json) · [业务复核](review.json) · [证据摘要](evidence-index.json)
- 完整测试记录仅存于本地 test-records/live-replaced-20261027/（仅本地审计用，不随本目录发布），不属于可展示示例。
- 当前数据与结论限于原查询时点及公开样本；覆盖率不代表准确率或低风险。
