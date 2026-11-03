# 平台企业综合画像

- 用户需求：分析京东科技信息技术有限公司的经营、创新、品牌、舆情和招聘信号。
- 决策用途：为平台型企业合作评估建立基线。
- 本轮结果：**本轮检查通过**
- 实际工具调用：23；失败 0
- 章节覆盖率：90%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 企业主体解析准确
- 品牌与关联集团不无依据混同
- 舆情与风险维度分别展示
- 证据不足维度降低置信度

## 本轮自动检查发现


## 使用局限

- 关联集团数据可能无法完整归属
- 平台业务细分表现不在统一报告中拆分

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 full-profile-skill/scripts/compose_fusion_report.py --enterprise '京东科技信息技术有限公司' --keyword-type name --output full-profile-skill/output/07-platform-company/report.json --report-output full-profile-skill/output/07-platform-company/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 企业主体解析准确：subject、match_raw、工商企业名均为京东科技信息技术有限公司，并有统一信用代码91110108MA00G9F39B。 当前第五轮result.started_at=2026-10-26T18:45:14+08:00，invocation_id=1793011514748258000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=京东科技信息技术有限公司，resolved=True；metrics[上游风险评分=100；对外投资=9；专利数量=4213；商标数量=16；招投标参与=804；舆情总数=393；注册资本=人民币 3.00亿；融资轮次=1；在招岗位=31；开庭公告=33]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[patent:patent_bigdata_patent_stats=data；news:news_bigdata_news_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bidding_info=data(20/804)；bidding:bid_bigdata_bid_win_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=empty；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(9/9)；enterprise:enterprise_get_enterprise_main_person_info=data(3/3)；risk:enterprise_risk_insight_score=data；risk:risk_insight_court_hearings=data(20/33)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 品牌与关联集团不无依据混同：商标/专利只按目标法人具名检索，洞察明确权利人与目标法人关系未逐项核验；股东京东云计算另列。 当前第五轮result.started_at=2026-10-26T18:45:14+08:00，invocation_id=1793011514748258000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=京东科技信息技术有限公司，resolved=True；metrics[上游风险评分=100；对外投资=9；专利数量=4213；商标数量=16；招投标参与=804；舆情总数=393；注册资本=人民币 3.00亿；融资轮次=1；在招岗位=31；开庭公告=33]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[patent:patent_bigdata_patent_stats=data；news:news_bigdata_news_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bidding_info=data(20/804)；bidding:bid_bigdata_bid_win_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=empty；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(9/9)；enterprise:enterprise_get_enterprise_main_person_info=data(3/3)；risk:enterprise_risk_insight_score=data；risk:risk_insight_court_hearings=data(20/33)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 舆情与风险维度分别展示：舆情总数393/正面58%为独立指标；风险另列开庭32及样本，不以舆情替代风险。 当前第五轮result.started_at=2026-10-26T18:45:14+08:00，invocation_id=1793011514748258000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=京东科技信息技术有限公司，resolved=True；metrics[上游风险评分=100；对外投资=9；专利数量=4213；商标数量=16；招投标参与=804；舆情总数=393；注册资本=人民币 3.00亿；融资轮次=1；在招岗位=31；开庭公告=33]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[patent:patent_bigdata_patent_stats=data；news:news_bigdata_news_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bidding_info=data(20/804)；bidding:bid_bigdata_bid_win_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=empty；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(9/9)；enterprise:enterprise_get_enterprise_main_person_info=data(3/3)；risk:enterprise_risk_insight_score=data；risk:risk_insight_court_hearings=data(20/33)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 证据不足维度降低置信度：verdict为“事实观察（不评分）/逐项人工核验”，caliber披露权属、行业和财务审计限制。 当前第五轮result.started_at=2026-10-26T18:45:14+08:00，invocation_id=1793011514748258000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=京东科技信息技术有限公司，resolved=True；metrics[上游风险评分=100；对外投资=9；专利数量=4213；商标数量=16；招投标参与=804；舆情总数=393；注册资本=人民币 3.00亿；融资轮次=1；在招岗位=31；开庭公告=33]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[patent:patent_bigdata_patent_stats=data；news:news_bigdata_news_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bidding_info=data(20/804)；bidding:bid_bigdata_bid_win_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=empty；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(9/9)；enterprise:enterprise_get_enterprise_main_person_info=data(3/3)；risk:enterprise_risk_insight_score=data；risk:risk_insight_court_hearings=data(20/33)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)