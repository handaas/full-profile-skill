# 上市科技企业综合画像

- 用户需求：为宁德时代新能源科技股份有限公司生成工商、风险、经营、创新、品牌、市场、舆情和人才八维画像。
- 决策用途：形成投资研究的统一事实底稿。
- 本轮结果：**本轮检查通过**
- 实际工具调用：23；失败 0
- 章节覆盖率：90%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 八个维度的覆盖状态清楚
- 综合评分不掩盖缺失维度
- 创新与市场交叉结论有双域证据
- 主体名称一致

## 本轮自动检查发现


## 使用局限

- 不是证券投资建议
- 报告不包含未公开财务预测

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 full-profile-skill/scripts/compose_fusion_report.py --enterprise '宁德时代新能源科技股份有限公司' --keyword-type name --output full-profile-skill/output/01-investment-profile/report.json --report-output full-profile-skill/output/01-investment-profile/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 八个维度的覆盖状态清楚：数据范围写覆盖8/8数据源；工商、风险、经营、专利、商标、标讯、舆情、招聘均有独立指标或章节，quality_report为10/11、91%。 当前第五轮result.started_at=2026-10-26T18:44:41+08:00，invocation_id=1793011481099545000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=20；subject.enterprise=宁德时代新能源科技股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=159；专利数量=26876；商标数量=1534；招投标参与=390；舆情总数=5572；注册资本=人民币 45.64亿；融资轮次=22；在招岗位=8606；开庭公告=229]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/390)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/34)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(15/15)；enterprise:enterprise_get_enterprise_invest_info=data(50/159)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/229)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=data]
- **pass** 综合评分不掩盖缺失维度：不生成自定义综合/专项评分，specialty_scores为空；开庭229触发“不予综合评级”，并披露1个空章节。 当前第五轮result.started_at=2026-10-26T18:44:41+08:00，invocation_id=1793011481099545000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=20；subject.enterprise=宁德时代新能源科技股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=159；专利数量=26876；商标数量=1534；招投标参与=390；舆情总数=5572；注册资本=人民币 45.64亿；融资轮次=22；在招岗位=8606；开庭公告=229]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/390)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/34)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(15/15)；enterprise:enterprise_get_enterprise_invest_info=data(50/159)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/229)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=data]
- **pass** 创新与市场交叉结论有双域证据：洞察引用专利26876与中标33，明确两类公开记录并存且缺少权属、履约、转化和同行分母。 当前第五轮result.started_at=2026-10-26T18:44:41+08:00，invocation_id=1793011481099545000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=20；subject.enterprise=宁德时代新能源科技股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=159；专利数量=26876；商标数量=1534；招投标参与=390；舆情总数=5572；注册资本=人民币 45.64亿；融资轮次=22；在招岗位=8606；开庭公告=229]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/390)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/34)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(15/15)；enterprise:enterprise_get_enterprise_invest_info=data(50/159)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/229)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=data]
- **pass** 主体名称一致：subject、match_raw及工商企业名称均为宁德时代新能源科技股份有限公司，统一信用代码已返回。 当前第五轮result.started_at=2026-10-26T18:44:41+08:00，invocation_id=1793011481099545000；calls=23，HTML/MD均含当前标题。；本轮当前产物：technical=passed，successful_data_calls=20；subject.enterprise=宁德时代新能源科技股份有限公司，resolved=True；metrics[上游风险评分=100；对外投资=159；专利数量=26876；商标数量=1534；招投标参与=390；舆情总数=5572；注册资本=人民币 45.64亿；融资轮次=22；在招岗位=8606；开庭公告=229]；quality={'total_sections': 10, 'populated_sections': 9, 'empty_sections': 1, 'coverage_pct': 90, 'data_sources': 8, 'cross_insights': 3}；非空章节=['工商基础信息', '股东出资结构', '对外投资清单（关联方敞口）', '专利与商标公开统计', '招投标公开统计', '风险维度统计', '开庭公告明细', '经营规模与资本运作', '招聘公开统计']；代表记录=4；calls[recruitment:recruitment_trend=data；recruitment:recruitment_employer_profile=data；news:news_bigdata_news_stats=data；patent:patent_bigdata_patent_stats=data；trademark:trademark_bigdata_trademark_profile=data；trademark:trademark_bigdata_trademark_stats=data；bidding:bid_bigdata_bid_win_stats=data；bidding:bid_bigdata_bidding_info=data(20/390)；operation:operation_insight_business_scale=data；operation:operation_insight_financing_info=data；operation:operation_insight_company_trends=data；operation:operation_insight_enterprise_rankings=data(10/34)；enterprise:enterprise_get_enterprise_base_info=data；enterprise:enterprise_get_enterprise_holder_info=data；enterprise:enterprise_get_enterprise_main_person_info=data(15/15)；enterprise:enterprise_get_enterprise_invest_info=data(50/159)；risk:enterprise_risk_insight_score=data；risk:risk_insight_litigation_risk_profile=data；risk:risk_insight_court_hearings=data(20/229)；risk:risk_insight_penalties=empty；risk:risk_insight_business_anomalies=empty；risk:risk_insight_consumption_restrictions=empty；risk:risk_insight_chattel_mortgage=data]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)
[页面截图](browser.png)