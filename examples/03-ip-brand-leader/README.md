# 创新品牌企业画像

- 用户需求：分析华为技术有限公司的专利、商标、经营、市场和人才协同情况。
- 决策用途：评估创新与品牌资产的结构匹配。
- 本轮结果：**本轮检查通过**
- 实际工具调用：23；失败 0
- 章节覆盖率：90%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 专利和商标证据分别展示
- 创新品牌协同使用可见数据
- 风险健康度不等于无风险
- 各章节空值处理一致

## 本轮自动检查发现


## 使用局限

- 知识产权数量不等于权利质量
- 集团关联主体数据可能不完全归集

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 full-profile-skill/scripts/compose_fusion_report.py --enterprise '华为技术有限公司' --keyword-type name --output full-profile-skill/output/03-ip-brand-leader/report.json --report-output full-profile-skill/output/03-ip-brand-leader/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 专利和商标证据分别展示：指标分别列专利133237、商标22694；创新章节分别列专利分型、商标总数和类别。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483360107000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=华为技术有限公司，resolved=True；metrics[上游风险评分=99；对外投资=54；专利数量=133237；商标数量=22694；招投标参与=1000；舆情总数=8612；注册资本=人民币 411.41亿；在招岗位=6258；开庭公告=4401；股东数量=1]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=3；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/18)；operation:operation_insight_business_scale=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_financing_info=empty；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(32/32)；enterprise:enterprise_get_enterprise_invest_info=data(50/54)；risk:enterprise_risk_insight_score=data；risk:risk_insight_penalties=empty；risk:risk_insight_court_hearings=data(20/4401)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 创新品牌协同使用可见数据：交叉洞察引用专利133237、商标22694、45类别，并明确仅为公开记录并存，未外推竞争优势。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483360107000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=华为技术有限公司，resolved=True；metrics[上游风险评分=99；对外投资=54；专利数量=133237；商标数量=22694；招投标参与=1000；舆情总数=8612；注册资本=人民币 411.41亿；在招岗位=6258；开庭公告=4401；股东数量=1]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=3；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/18)；operation:operation_insight_business_scale=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_financing_info=empty；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(32/32)；enterprise:enterprise_get_enterprise_invest_info=data(50/54)；risk:enterprise_risk_insight_score=data；risk:risk_insight_penalties=empty；risk:risk_insight_court_hearings=data(20/4401)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 风险健康度不等于无风险：开庭4401触发人工核验与不予评级，上游99分标注与司法记录冲突且不作低风险背书。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483360107000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=华为技术有限公司，resolved=True；metrics[上游风险评分=99；对外投资=54；专利数量=133237；商标数量=22694；招投标参与=1000；舆情总数=8612；注册资本=人民币 411.41亿；在招岗位=6258；开庭公告=4401；股东数量=1]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=3；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/18)；operation:operation_insight_business_scale=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_financing_info=empty；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(32/32)；enterprise:enterprise_get_enterprise_invest_info=data(50/54)；risk:enterprise_risk_insight_score=data；risk:risk_insight_penalties=empty；risk:risk_insight_court_hearings=data(20/4401)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]
- **pass** 各章节空值处理一致：融资调用empty后经营章节不造融资值；司法缺案号/主体/日期统一显示“-”，并披露无法逐案去重。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011483360107000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=18；subject.enterprise=华为技术有限公司，resolved=True；metrics[上游风险评分=99；对外投资=54；专利数量=133237；商标数量=22694；招投标参与=1000；舆情总数=8612；注册资本=人民币 411.41亿；在招岗位=6258；开庭公告=4401；股东数量=1]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=3；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/1000)；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/18)；operation:operation_insight_business_scale=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_financing_info=empty；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(32/32)；enterprise:enterprise_get_enterprise_invest_info=data(50/54)；risk:enterprise_risk_insight_score=data；risk:risk_insight_penalties=empty；risk:risk_insight_court_hearings=data(20/4401)；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=empty]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)