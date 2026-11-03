# 高风险地产企业全面体检

- 用户需求：对恒大地产集团有限公司做全面体检，重点观察风险、经营和市场活动之间的关系。
- 决策用途：支持高风险交易的初步筛查。
- 本轮结果：**本轮检查通过**
- 实际工具调用：23；失败 0
- 章节覆盖率：90%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 风险事件分类可追溯
- 风险与经营事实不作无依据因果推断
- 空创新或招聘维度不被补零
- 综合定位体现重大风险

## 本轮自动检查发现


## 使用局限

- 公开事件可能有时间延迟
- 不替代法律和财务专项尽调

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 full-profile-skill/scripts/compose_fusion_report.py --enterprise '恒大地产集团有限公司' --keyword-type name --output full-profile-skill/output/02-high-risk-profile/report.json --report-output full-profile-skill/output/02-high-risk-profile/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 风险事件分类可追溯：风险维度分列处罚1、限高3676、开庭16568；处罚/限高有文号或案号、机关/法院和日期样本，开庭缺字段也以“-”保留。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011482964848000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=21；subject.enterprise=恒大地产集团有限公司，resolved=True；metrics[上游风险评分=0；对外投资=195；专利数量=2；商标数量=1433；招投标参与=68；舆情总数=3164；行政处罚=1；注册资本=人民币 39.40亿；融资轮次=12；在招岗位=1220]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=5；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/68)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；trademark:trademark_bigdata_trademark_profile=data；operation:operation_insight_company_trends=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_enterprise_rankings=data(10/11)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/195)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/16568)；risk:risk_insight_penalties=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=data(20/3676)；risk:risk_insight_chattel_mortgage=empty]
- **pass** 风险与经营事实不作无依据因果推断：经营规模、融资12、招聘1220与风险分区展示；洞察只称活动与司法暴露并存，不推断因果。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011482964848000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=21；subject.enterprise=恒大地产集团有限公司，resolved=True；metrics[上游风险评分=0；对外投资=195；专利数量=2；商标数量=1433；招投标参与=68；舆情总数=3164；行政处罚=1；注册资本=人民币 39.40亿；融资轮次=12；在招岗位=1220]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=5；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/68)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；trademark:trademark_bigdata_trademark_profile=data；operation:operation_insight_company_trends=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_enterprise_rankings=data(10/11)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/195)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/16568)；risk:risk_insight_penalties=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=data(20/3676)；risk:risk_insight_chattel_mortgage=empty]
- **pass** 空创新或招聘维度不被补零：创新实际返回专利2/商标1433，招聘实际返回1220；其他缺失字段保留“-”或省略，未作为零分。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011482964848000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=21；subject.enterprise=恒大地产集团有限公司，resolved=True；metrics[上游风险评分=0；对外投资=195；专利数量=2；商标数量=1433；招投标参与=68；舆情总数=3164；行政处罚=1；注册资本=人民币 39.40亿；融资轮次=12；在招岗位=1220]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=5；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/68)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；trademark:trademark_bigdata_trademark_profile=data；operation:operation_insight_company_trends=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_enterprise_rankings=data(10/11)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/195)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/16568)；risk:risk_insight_penalties=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=data(20/3676)；risk:risk_insight_chattel_mortgage=empty]
- **pass** 综合定位体现重大风险：verdict为人工司法核验/不予综合评级，blockers明确限高3676、开庭16568及高风险。 当前第五轮result.started_at=2026-10-26T18:44:43+08:00，invocation_id=1793011482964848000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=21；subject.enterprise=恒大地产集团有限公司，resolved=True；metrics[上游风险评分=0；对外投资=195；专利数量=2；商标数量=1433；招投标参与=68；舆情总数=3164；行政处罚=1；注册资本=人民币 39.40亿；融资轮次=12；在招岗位=1220]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=5；calls[news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；recruitment:recruitment_employer_profile=data；recruitment:recruitment_trend=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/68)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；trademark:trademark_bigdata_trademark_profile=data；operation:operation_insight_company_trends=data；trademark:trademark_bigdata_trademark_stats=data；operation:operation_insight_enterprise_rankings=data(10/11)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_invest_info=data(50/195)；enterprise:enterprise_get_enterprise_main_person_info=data(6/6)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/16568)；risk:risk_insight_penalties=data；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=data(20/3676)；risk:risk_insight_chattel_mortgage=empty]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)