# 人才扩张型企业画像

- 用户需求：对比亚迪股份有限公司做八维画像，重点检查招聘扩张与经营、风险和创新是否匹配。
- 决策用途：支持快速扩张企业的综合评估。
- 本轮结果：**本轮检查通过**
- 实际工具调用：23；失败 0
- 章节覆盖率：90%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 招聘趋势与经营趋势时间口径清楚
- 扩张风险判断引用多个域
- 专利数量不直接等于研发效率
- 综合结论区分事实和推断

## 本轮自动检查发现


## 使用局限

- 招聘岗位不等于实际员工净增长
- 产能和现金流不在本报告直接验证

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 full-profile-skill/scripts/compose_fusion_report.py --enterprise '比亚迪股份有限公司' --keyword-type name --output full-profile-skill/output/05-hiring-expansion/report.json --report-output full-profile-skill/output/05-hiring-expansion/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 招聘趋势与经营趋势时间口径清楚：招聘标为“当前/近三月”并声明无精确起止日期；经营章节仅列规模/融资/上榜，不伪造同周期趋势。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483907439000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=19；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=109；专利数量=46035；商标数量=3907；招投标参与=1000；舆情总数=5131；注册资本=人民币 91.17亿；融资轮次=7；在招岗位=126960；开庭公告=298]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/76)；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/109)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/298)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 扩张风险判断引用多个域：洞察同时引用招聘125052、融资7、开庭298与限高0，并由司法暴露触发人工核验。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483907439000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=19；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=109；专利数量=46035；商标数量=3907；招投标参与=1000；舆情总数=5131；注册资本=人民币 91.17亿；融资轮次=7；在招岗位=126960；开庭公告=298]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/76)；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/109)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/298)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 专利数量不直接等于研发效率：专利46035仅作为公开数量；章节和洞察均声明缺权属、有效性、质量、投入与转化，不能推断技术竞争优势。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483907439000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=19；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=109；专利数量=46035；商标数量=3907；招投标参与=1000；舆情总数=5131；注册资本=人民币 91.17亿；融资轮次=7；在招岗位=126960；开庭公告=298]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/76)；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/109)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/298)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 综合结论区分事实和推断：insights明确分evidence与interpretation，verdict只作司法核验而非扩张/健康评级。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483907439000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=19；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=109；专利数量=46035；商标数量=3907；招投标参与=1000；舆情总数=5131；注册资本=人民币 91.17亿；融资轮次=7；在招岗位=126960；开庭公告=298]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/76)；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/109)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/298)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)