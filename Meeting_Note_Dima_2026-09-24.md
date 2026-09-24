# Meeting script — Dima, 2026-09-24 — CP-72 Change #1 Country Risk

> 用法：每个要点分三层。**讲稿**是可以照读的英文；**背景**是给自己看的中文，解释这句话为什么成立、依据在哪；**追问**是 Dima 可能问的问题和答法。
> 配套：`CP-72_Change1_CountryRisk_Review_Tracker.xlsx`（投屏用；sheet 名在括号里）、`Change1_CountryRisk_Review_Plan.md`。
> 口径：观察点一律用 "AQV noted …"，不说 "should"、不提修改建议（Ground Rule G）。

---

## 0. 先弄懂的几个词（给自己看）

- **Country risk assessment（CR）**：每个国家一个 1–6 的分数（1 最好）。公司在多个国家经营时，按各国 exposure 加权平均得到公司的 CR。
- **CICRA**：CR 和 industry risk（IR，也是 1–6）经 Table 1 合成的分数。Table 1 的关键性质：**CR 1–3 对 CICRA 完全中性**（CICRA = IR），只有 CR 4–6 才把 CICRA 往坏推。
- **BRP**：business risk profile（1 excellent … 6 vulnerable），由 CICRA 和 competitive position（CP）经 Table 2 合成。
- **Anchor**：BRP 和 financial risk profile（FRP）经 Table 3 合成的起点 rating（如 bbb/bbb-）。
- **Category vs notch**：CR、CICRA、BRP 的一格叫一个 category；anchor 的一格叫一个 notch（bbb → bbb- 是 1 notch）。一个 category 的变动可以传导成多个 notch。
- **Weighted average vs weak-link**：前者按 exposure 加权；后者取最弱的国家（例如资产在高风险国、收入在低风险国时按高风险国算）。
- **Rule-based vs judgment-based**：前者有明确条件（满足就调、不满足就不调），后者靠分析师判断。AJ（analytical judgement）评分就是在给 judgment-based 节点打分：degree 0–5、impact 1–3。
- **Ground Rules**（Operational Guidelines）：**B** AQV 可以在会上直接对 validation 流程要求（含 impact testing 的 data requirements）表态；**F** 只对 Methodologies Supervisors 已经看过或讨论过的文件提问题；**G** 只识别 potential issue，不提 recommendation，不对 criteria 措辞给意见。
- **Comment vs Finding**：Comment 是 squad 通常会解决的问题（改文字、补测试）；Finding 是没解决的 Comment，很少见。

---

## 1. 开场（1 分钟）

**讲稿**
> Since we last spoke I did three things. First, I read the CP-49 Covered Bonds and CP-64 RAS final validation reports end to end to learn the report structure and the depth expected per change. Second, I broke Change #1 down into its sub-changes and mapped every sub-change to the validation dimensions in the working doc and to the sections of the CVR template. Third, I ran the analyses that do not depend on squad materials — the completeness mapping, the downstream reference sweep and the sensitivity of the anchor to a one-category move in country risk. Everything is in one tracker workbook. I would like to walk you through what I have, flag a few observations, and then ask you a handful of questions that will decide how I spend the next two weeks.

**背景**
CP-64 是 Dima 自己写的，说读过它等于在说"我知道你期待什么深度"。三件事对应 Gregoire 方法的前三步（先读 CVR、scenario 推演、wording 审查）。

---

## 2. 展示：已完成的工作（5 分钟）

### 2.1 #1 拆成 4 个 sub-change（Tracker: Overview 与 Plan §0）

**讲稿**
> The September deck actually contains four distinct sub-changes, and I think they need to be validated separately because they have different mechanics and different evidence. 1a is the blending mechanics: removing the 5% exposure threshold, removing the rounding of weights to 5% increments, taking exposure data as reported by the company, and expanding the list of exposure indicators. 1b is the aggregation rule: weighted average as the default, weak-link as an alternative "when more relevant", plus a new negative one-category adjustment to the weighted-average outcome. 1c is the removal of the diversity adjustment in paragraphs 48 to 51. And 1d is the removal of the paragraph 26 exception that lets a CICRA-5 company get a BRP of 2. I am treating the September deck as the current version — it allows a negative adjustment only, whereas the July deck said "down or up by one".

**背景**
拆分的价值：1a 是纯机械变动（几乎零影响），1b 引入新的判断节点（AQV 最关心），1c 和 1d 是删除现有 upward 机制（靠 usage 数据说话）。不拆开就没法给每块配证据。Sept pptx 的 "+1 被多数否决（与 S/S/D double counting）" 是判断以 Sept 为准的依据。

**追问**
- "Why separate 1d?" → 因为 para 26 是 BRP 层面的 exception，不在 country risk section（paras 40–51）里；squad 只是把它放进了 country risk deck。归属要问他（见 §4 问题 2）。

### 2.2 12 题 review plan 与分工（Tracker: Overview 的"分工"列；Plan §6）

**讲稿**
> I laid out twelve analysis items and, for each one, whether AQV performs the analysis itself or reviews the squad's analysis. Following the CP-49 and CP-64 wording: conceptual soundness, sensitivity, consistency of application, analytical judgement, transparency, usage statistics and scope verification are AQV's own work; impact testing, back-testing, calibration, the rating-impact statement and the alternatives considered are the squad's work that AQV reviews and attests. Each item is mapped to where it lands in the report — the Section 2 rows, the test rationale, Section 4 comments, 8.1 and Appendix 4.

**背景**
判别标准是 CVR 的动词：squad 做的地方写 "the squad conducted… AQV reviewed… found it sufficient"；AQV 自做的地方写 "AQV conducted a sensitivity test…"、"Reviewing ratings actions since 2010, AQV found…"。CP-64 §8.1 里 "AQV independently verified the ratings in scope" 说明即使是 squad 的 impact testing，AQV 也要独立核 scope。

**追问**
- "Which items are the heavy ones?" → 题 2 conceptual soundness、题 5 usage、题 8 AJ、题 10 impact review；impact 重要但篇幅不长，因为 #1 声称零影响，写出来就是核对计数。

### 2.3 三项已完成的分析（Tracker: 1_Completeness、3_Downstream、7_Sensitivity）

**讲稿**
> Three pieces are done. The completeness mapping takes the eighteen concepts in the current country risk paragraphs and tracks each into the proposal: six are retained, five modified, four removed, one is new, and six are unclear because the deck does not mention them — the exporter mitigation in paragraph 45, the estimation rule in 47, the 75% rule in 50, the de facto head office definition in 51, how regional scores are derived, and whether the final integer rounding survives.
> The downstream sweep found sixteen places that consume the country risk assessment: Table 1, Table 2, paragraph 87 on the SER volatility adjustment, paragraph 123 that selects the volatility table through CICRA, several thresholds in the sector-specific methodology written as "country risk of 3 or better" or "4 or better", and four other criteria that inherit the corporate determination by reference.
> The sensitivity piece is a formula workbook that pushes a one-category worsening in country risk through Tables 1, 2 and 3. Within country risk 1 to 3 nothing happens, because Table 1 is neutral there. Within 4 to 6, one category of country risk can move CICRA by two categories, that can move BRP by three categories, and the anchor can fall by three to five notches at an intermediate FRP and by up to eight notches at a minimal FRP.

**背景**
- 6 个 unclear 是"deck 没提"，不是"squad 删了"；所以措辞是 unclear，要等 draft。
- 下游 sweep 的意义：country risk 的位置没变，但 determination 的分布变了，会经 CICRA 传到 volatility table（FRP 用哪张表）和 SSCM 门槛。所以 impact testing 不能只看 ICR。
- Sensitivity 的具体链条：IR 3、CR 5→6 → CICRA 4→6（Table 1 第 3 行）→ CP 3 时 BRP 3→6（Table 2 第 3 行）→ FRP 3 时 anchor bbb/bbb- → bb-/b+（3–5 notch）；CP 1、FRP 1 时 BRP 2→5，anchor aa/aa- → bb+（7–8 notch）。这些格子都能在 Tracker 的 7_Sensitivity 里指给他看。

**追问**
- "Is that cliff new?" → 不是。Table 1/2 本来就这样；para 49 的 +1 和 para 26 的 exception 也都是一个 category 的机制。新的是触发权从 rule 交给了 judgment（见 §3.1）。
- "How often does that corner occur?" → 不知道，需要 portfolio 数据（CR ≥4 且 weighted average 在 x.5 附近的 entity 数）；这是 §4 问题 5。

---

## 3. 发现：请 Dima 判断是否成立、何时提出（8 分钟）

开场一句：
> A few observations. These are based on the deck only, so I am raising them with you first rather than with the squad, and I am framing them as things AQV noted, not as suggestions.

### 3.1 −1 notching 的 impact 不是 1 notch，而且没有触发条件

**讲稿**
> AQV noted that the proposed negative adjustment is described with a single example — a dependency on a dominant supplier in a higher-risk country — and no conditions for when it applies. Combined with the sensitivity result, the adjustment's potential impact should not be recorded as one notch in the analytical judgement appendix; in the country-risk-4-to-6 region it can be two to three notches, and more in corner cases. For comparison, the Ratings Above The Sovereign corporate criteria, paragraph 58, also allows a one-notch downward adjustment to the blended sovereign rating, but it defines the two conditions — head office location and funding location — under which it applies. So a defined-trigger version of this adjustment already exists inside our own criteria.

**背景**
- AJ 的 impact scale：1 = one notch；2 = 2–3 notches；3 = more than 3 notches（CP-64 Appendix 4）。CP-64 把 short-economic-life 的 "up to 8 notches" 记为 impact 3。
- CP-49 Comment 7 就是"三处 AJ 没有 guidance"，squad 的解决办法是加了 guidance 和 likely notching。所以这类 Comment 有先例、也有解决路径。
- 引 C&G RAS para 58 的作用：说明 defined triggers 可行，而不是建议怎么写（避免违反 Ground Rule G）。

**追问**
- "Isn't the weak-link approach already judgment?" → 是，但现行 para 44 列了三种定义情形（fixed assets、不可转移的出口收入、不可替代的供应商）；proposal 把它弱化成 "when more relevant"，同时另加了一个只有示例的 notching。判断空间是变宽了。

### 3.2 与项目方向的张力：删掉的是 rule，加上的是 judgment

**讲稿**
> The three mechanisms being removed — the paragraph 26 exception, the diversity adjustment, and possibly the paragraph 45 exporter mitigation — are all rule-based, with defined conditions. The one mechanism being added is judgment-based. The direction is consistent with the squad's own point that country risk is asymmetric, so I am not questioning the direction. But the Supervisory feedback in March was that judgment should be concentrated at a limited number of junctures rather than added at the factor level. Unless the draft gives the adjustment defined triggers, I expect this to be a comment.

**背景**
- Supervisory feedback（2026-03-23，Gregg L-S、Mike A.、Peter K.，在 working doc §A）："we are essentially not making any systematic changes to our approach around analytical judgement and might actually be adding more judgment at certain junctures rather than incorporating judgment systematically at a limited number of junctures."
- "Asymmetric" 是 squad 自己在 Slide 1 写的：有利环境中性、不利环境约束。negative-only notching 与之自洽，这是 AQV 可以给 squad 的正面结论。

### 3.3 Squad 自身逻辑要核实的两处

**讲稿**
> Two statements in the deck do not line up with the current text. Slide 4 says that for single-industry companies country diversification is captured in scale, scope and diversity. Paragraphs 217 to 219 assess geographic diversity as breadth of served markets and concentration of facilities — that is concentration risk, not diversification across country-risk levels. So the double-counting argument for rejecting a positive adjustment needs support from the draft wording of S/S/D. And Slide 1 says the supply-chain country is missing from the blending options, whereas paragraph 44 already treats a non-substitutable supplier in a higher-risk country as an exposure under the weak-link approach.

**背景**
- 这两点是逻辑问题，不是措辞问题；提前跟 Dima 讲是为了确认 AQV 的理解没错。
- 第二点可能是 squad 指 CCST 的 blending 输入表里没有供应商所在地字段（那是工具问题），要让 Dima 帮忙澄清。

### 3.4 para 26 删除的 "no rating impact"

**讲稿**
> For the paragraph 26 removal, the deck says no rating impact because the two entities benefit from parent or government support. That statement is about the ICR. Removing the exception moves their BRP from 2 to 3, which moves the anchor and the SACP; whether the ICR holds depends on the support likelihood under the group or GRE methodology. Also, Nakilat and Qatar Gas Transport appear to be the same group, so the usage may be one credit rather than two.

**背景**
- GRE 逻辑：support likelihood 很高时 ICR 与 government rating 挂钩，SACP 降了 ICR 不动；likelihood 低时 ICR 会跟着 SACP 走。所以 "no impact" 成立与否取决于这两个 entity 的 support 评估。
- Nakilat 是 Qatar Gas Transport Company 的商用名；两个名字可能是母公司和发债主体。要名单核实。

### 3.5 跨 practice 分叉

**讲稿**
> Removing the 5% threshold and the 5% rounding puts the corporate methodology out of line with the financial institutions methodology, paragraph 36, which still uses both, with an example that rounds 2.55 up to 3. Separately, the diversity adjustment in paragraph 49 has a mirror in the Ratings Above The Sovereign criteria, paragraph 57, with the same three conditions; after this change the two criteria diverge. Divergence is not necessarily a problem — the scales and the data granularity differ — but the squad will need to state why it is acceptable, and the FI example is useful evidence for how the mid-point rounding should be stated.

**背景**
- FI para 36："typically only includes countries where it conducts more than 5% of its business… All weightings are rounded to the nearest 5%"；Table 2 示例 2.55 → 3。
- C&G RAS para 57 的三个条件：head office 在更强国家；没有 >20% exposure 在等于或弱于 preliminary 的国家；holding 层面融资。与 para 49 一字不差地平行。

### 3.6 Wording 观察点

**讲稿**
> I have thirteen wording and consistency observations at deck level — for example the paragraph references in the deck do not match the published numbering, and the final integer rounding and the mid-point rule are not stated. I will hold these until there is draft text, since most of them can only be confirmed on the text.

**背景**
清单在 Tracker 的 9_Wording，已经写成 "AQV noted…" 格式。现在不逐条读，只说有、说等 draft。

---

## 4. 提问：需要 Dima 回答（8 分钟）

### 问题 1（最重要）：testing 能否输出 factor-level 数据

**讲稿**
> The question that matters most for my plan: does the testing tool save the factor-level inputs and outputs — the country risk score, CICRA, BRP, anchor and SACP before and after — or only the ICR? Country risk 1 to 3 is neutral to CICRA and the final integer rounding absorbs most of the movement, so for the large majority of entities the ICR will not move no matter what. If the tool only records ICR outcomes, the testing cannot detect the change, and the statement "rating impact: none" for 1a and 1b will have no evidence behind it. Can AQV ask the squad now for factor-level before-and-after outputs as a data requirement for the impact testing?

**背景**
- Ground Rule B 允许 AQV 在会上对 impact testing 的 data requirements 直接表态，所以这不是越界。
- CP-64 Comments 12–13 就是 impact testing 的 rationale 支持不足，AQV 要求补跑；这次最好在 testing 结束前就把要求提出去，而不是事后补。

### 问题 2：para 26 exception 的归属

**讲稿**
> Should the removal of the paragraph 26 exception be validated under Change #1, or under the BRP and anchor changes? It sits in the country risk deck, but the mechanism is a BRP exception rather than a country risk determination.

### 问题 3：draft 文本的时间表

**讲稿**
> Is there a timeline for draft text on the country risk section? Six concepts in the current paragraphs are simply not mentioned in the deck, and I cannot classify them as retained or removed until I see text.

### 问题 4：SSCM 与 CCST 的范围

**讲稿**
> Two scope questions. Is the Sector-Specific Corporate Methodology being revised as part of CP-72? Several sector thresholds are written as "country risk of 3 or better" or "4 or better", and the negative adjustment could move an entity across them. And will the CCST country risk module — the removed rounding, the new notching field — go through a separate model validation, or is it inside this validation?

**背景**
SSCM 不在 11 项 change 的 legend 里；utilities 的 medial volatility table 资格依赖 CR ≤4，是 −1 notching 的第二条传导路径。

### 问题 5：AQV 的数据源

**讲稿**
> For the usage and sensitivity work I need portfolio-level data: the distribution of country risk scores and CICRA, how many entities are multi-country, how many sit near a rounding boundary, and how often the weak-link approach, the exporter mitigation and regional assessments are used. Where does AQV normally pull this from — a CCST extract, or something else?

### 问题 6：back-testing

**讲稿**
> Does the squad have a back-testing plan for this change? The guidelines encourage AQV to propose back-testing cases from its own research. For country risk, the natural cases are entities whose country risk score moved in the past thirteen years and whose CICRA or rating moved with it — Russia in 2022, Argentina, Turkey — to see whether the proposed determination would have behaved differently.

**背景**
Guidelines 的 ATB 阶段活动："Discuss with Squad their plan for impact testing and for back-testing, leverage research to identify back-testing cases". 这是 AQV 主动提议的合规空间。

### 问题 7：Slide 1 的 follow-ups 是否已过 Supervisors

**讲稿**
> Last one on process. Slide 1 lists squad follow-ups — aligning to a 10% threshold, dropping the country risk analysis for scores of 1 to 3, and the rejected positive adjustment. Have these been discussed with the Methodologies Supervisors? I want to respect the rule that AQV only raises questions on concepts that have been reviewed at that level, so I would like to know when I can take my observations to the squad.

**背景**
Ground Rule F。问清楚这个，后面提 Comment 的时机就不会踩线。

---

## 5. 收尾

**讲稿**
> Based on your answers I plan to spend the next two weeks on three things: drafting the conceptual soundness rationale for the test in the CP-49 format, preparing the data request for usage statistics, and setting up the verification method for the impact testing — scope check, sample representativeness, and a re-performance of the new country risk computation on five to ten entities from public segment data. I will send you the tracker after this call.

---

## 6. 会后待办（会上填）

- [ ] 1d 归属：
- [ ] Testing 能否输出 factor-level 数据：
- [ ] Draft 时间表：
- [ ] SSCM / CCST 范围：
- [ ] 数据源：
- [ ] Back-testing 安排：
- [ ] 何时可向 squad 提问：
