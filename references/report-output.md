# 综合画像报告内容规范（事实版）

默认 direct-mcp 只整理工商、风险、经营、创新、商标、招投标、舆情、招聘八个维度的事实与缺口，不生成自定义综合分、雷达或排名。

## 一、章节与字段

1. 查询对象与口径：主体确认、匹配方式、覆盖维度、时间、缺口。
2. 数据总览：八维事实指标，每项带口径提示。
3. 核心分析：工商、股东、对外投资、专利商标、招投标、舆情、风险维度、开庭明细、经营、招聘；空章节跳过。
4. 代表性记录：只复述同报告事实。
5. 特征与洞察：证据字段 + 解释 + 边界。
6. 数据口径与来源。

## 二、内容整理（原始值 → 标签 → 证据）

| 原始字段 | 规范展示 | 证据位置 | 禁止 |
| --- | --- | --- | --- |
| `newsSentimentStats` | 正面/负面/中立/未知 + 总量 | `fp_news` | 只报正面占比、漏掉负面 |
| `bidding_total` | 招投标记录总量 | fp_bidding / metrics | 当作中标次数 |
| `winbidStatList` 合计 | 中标次数 | fp_bidding / metrics | 当作收入或份额 |
| `court_hearings_total` | 开庭公告总数 | fp_risk_dims / fp_hearings | 当作去重案件数 |
| `risk_score` + `risk_level` | 原值 + 接口未说明阈值/方向 | metrics / 代表记录 | 反推低风险、编造等级冲突 |
| `patentTypeStat` | 专利总数及类型分列 | fp_innovation | 把申请与授权合并为有效专利 |
| `tmCount` / `tmValidNumber` | 商标总数/有效/类别 | fp_innovation | 用有效数覆盖总数 |
| `recruitingCurrentCount` / `LastThreeMonthCount` | 同值时合并观察并注明窗口不可区分 | fp_recruitment | 当作两个独立信号 |
| 开庭明细字段 | 案号/日期/主体缺什么写什么 | fp_hearings note | 缺字段时声称“保留用于去重” |

- 英文 key 转中文标签；数值逐项保留；未知写“未返回”，不得写成 `0`。
- 明细展示条数与上游总量分别写清；样本/单页不得称全量。

## 三、语义审校门禁

1. **维度独立**：专利与商标、招投标与收入、招聘与经营动能分别判断，不用数量直接推导强弱。
2. **主题归类**：舆情按情感分类，风险按上游维度分类；不同类别不合并成“综合风险”或“创新实力”。
3. **同义合并**：仅在上游明确别名或字段含义一致时合并；不确定时保留原名并标“待核验”。
4. **主体口径**：主体未确认时全部指标标“同名检索线索，不归属该主体”。
5. **时间口径**：舆情月份、招聘窗口、开庭日期、专利年度分别标注；历史记录不得写成当前状态。
6. **冲突处理**：上游等级、总量、明细不一致时并列展示并写“未能对账”，不推断原因。
7. **置信度**：样本、单页预算、未纳入条数必须披露；不得把样本当全量。
8. **保留风险**：负面舆情、执行/限高、空维度、未知项不删除；不得被正面舆情或专利数量抵消。

## 四、AI 审校交付门禁（草稿 → final）

`compose_*` 正常生成与 `--dry-run` 只产出草稿：JSON 标记 `data_source.semantic_review.status=pending`，同名 HTML/Markdown 带“数据草稿（待AI语义审校）”提示，不能交付。`apply_content_review`/`organize_report` 是确定性整理，不是 AI 审校。

```bash
python scripts/review_report.py --input output/draft.json --request output/review-request.json
# 当前 AI 阅读请求中的 report 后写 output/ai-review.json
python scripts/review_report.py --input output/draft.json --review output/ai-review.json \
  --output output/final/report.json --report-output output/final/report.html
```

请求含 `source_sha256`、`report`、`visible_section_keys`、`instructions`、`response_fields`；响应：

```json
{
  "source_sha256": "<与请求一致>",
  "summary": [{"text": "逐句摘要", "sources": ["/core_analysis/..."], "kind": "fact"}],
  "normalizations": [{"sources": ["/core_analysis/..."], "category": "类别", "normalized": "规范表达", "evidence": "原文摘录", "reason": "理由"}],
  "insights": [{"feature": "特征", "evidence": "证据摘录", "interpretation": "解读", "sources": ["/metrics/0"]}]
}
```

- `source_sha256` 必须与请求一致；不一致须重新请求，不能沿用旧判断。
- `sources` 使用 JSON Pointer，只能指向本报告实际存在的 `/subject/…`、`/core_analysis/…`、`/metrics/…`、`/caliber/…`、`/data_source/…`、`/analysis_request/…`；`/core_analysis/sections`、`/data_source/semantic_review` 与旧 `abstract`/`summary`/`insights` 不是事实依据。
- 每项至少一个来源且不能重复路径；同一来源可支持多项判断；不能借其他企业、案例、记录或常识补本记录。
- `summary` 写 3–5 句有信息量的逐句摘要，`kind` 只能是 `fact`/`interpretation`/`limitation`；无数据依据只能写 `limitation`。`normalizations` 是独立视图，原文不改写；`evidence` 必填，由当前 AI 选择简洁可读的原文摘录作为“原文依据”列，并由同项 `sources` 支撑，完整原值仍保留在 draft/request 与来源 SHA 记录中；必须保留否定、最高、至少、至多、试用期、转正后、仅限、部分、疑似、待定、已失效等限定；不同主体、互斥金额或比例不能合并；没有实际归类需要时可为空；`insights` 的 `feature`、`evidence`、`interpretation` 都须由同一 `sources` 支撑；`evidence` 是实际 AI 写的简洁可读证据摘录，保留来源数字、单位与限定。
- 所有文本（含 `normalized`、`category`、`reason`、`evidence`、洞察）中的数字必须逐字出现在所引 values 中，不新造派生数字、不改精度；需要派生指标先在脚本计算再引用。
- 只使用本次数据，不调用 MCP/外部模型 API/新增查询。应用后 `status=reviewed` 并记录来源 SHA-256、原 `generated_at`、审校时间与判断证据；原查询时间和原件不变。`summary` 写入 `abstract`/`summary`/`executive_summary`，`normalizations` 写入 `core_analysis.ai_normalization`（独立表格），`insights` 写入 `insights`；原始字段不改写。

**展示与交付**：空板块连标题和目录一起隐藏，但只能影响展示，不能从 `quality_report` 分母抹去未覆盖维度或提高覆盖率；真实 `0`/`False` 保留，缺失/未查询不等于 0；失败只写口径限制，不推断“无风险”。AI 标准化/摘要是解释视图，不新增数据来源或覆盖率。核对最终 JSON/HTML/Markdown 后才交付；请求文件、草稿或手工润色件不算完成。

## 五、离线复核

`compose_direct.apply_content_review(report, calls=None)` 对冻结报告做纯本地整理：修复 `fp_news` 键不一致导致的舆情章节缺失，从既有 `calls.json` 恢复负面舆情与中标次数，补写招聘窗口提示和开庭明细备注，修正风险等级措辞。不调用 MCP，不改证据文件。

正常生成 `compose_direct.build_direct_payload`（`compose_fusion_report.py` 默认直连模式）在返回前调用同一函数；`calls=None` 时自动读取 `data["calls"]` / `_meta["calls"]` 中已有的调用证据并传入，不发起二次查询。主体未确认（`subject.resolved=false`）时即使存在同案调用证据也不新增舆情/中标事实。整理只重算章节填充数并保留构建时声明的章节总数，缺失维度不会被折叠成 100% 覆盖。

审校复核：完整保留有来源的摘要句子及采集层“数据缺口／主体解析受阻”提示；重审不得引用 `/core_analysis/ai_normalization` 等既有 AI 视图作为原始证据。HTML 与 Markdown 应使用一致的样本数量、趋势顺序及数据列，单元格中的竖线和换行不得破坏表格结构。
