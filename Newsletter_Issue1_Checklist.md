# Newsletter Issue 1 (end Sept 2026) — 待办清单

范围（2026-09-09 定）：US Banks = 条目 1、3、5(可选)；US Insurance = 条目 1、2、3、4。
未选条目已存进 project memory（newsletter.md → Backlog），以后再补。

---

## A. US Banks

### A0. 刷新到 2026Q2（条目 1、3、5 的前提）
- [ ] 确认 pbix 里现在是哪个季度的 Y-9C
- [ ] CapIQ：同一 screen，period 换成 2026Q2，重导出 `USBanksFromAQVDashboard.xlsx`
- [ ] 跑 `process_capiq_to_powerbi_v3.py` → 看 log：49 家左右、integrity check 全过
- [ ] Power BI → Refresh；核对 treemap 总量 vs 脚本 log

### A1. 条目 1 — Headline baseline（从刷新后的 dashboard 读数）
- [ ] 家数（rated BHC，parent 去重后）
- [ ] Total Loans & Leases ($T)
- [ ] Loans to NDFI ($T) + NDFI % of total loans
- [ ] Business Credit ($bn) + BC % of NDFI + BC % of total loans
- 文案口径：BCI = 下限/核心 proxy，total NDFI = 上限，写成 estimation range

### A3. 条目 3 — Trend line（需要补历史）
- [ ] CapIQ：确认 NDFI 五分类字段最早从哪个季度有值（2024Q1 或 2024Q2）
- [ ] 同一 screen 加 period 列：从最早季度到 2026Q2（约 8–9 期）；
      如果方便，`Loans to NDFI` 总量和 `Total Loans` 可以再往前拉到 2021Q1（总量线有更长历史）
- [ ] 把导出文件的 header（前 4–5 行）截图或复制给 Claude → 改脚本支持多期（输出加 `Period` 列）
- [ ] 决策：trend 用固定 universe（= 2026Q2 的 49 家，推荐，避免样本变化干扰）还是每期各自筛
- [ ] Power BI：新建 line chart（X=Period，Y=NDFI % of total loans；第二条线 BC $bn）
- 外部对照：FDIC Q2 2026 QBP 全行业 NDFI +22.4% YoY vs total loans +6.8%

### A5. 条目 5（可选）— Lender 评级分布
- [ ] 从 ratings bar chart 算 "% of NDFI loans held by banks rated A- or above"
      （Excel 里按 rating 汇总 Loans to NDFI 即可，或加一个 DAX measure）
- [ ] 确认 rating 列全是 public rating（银行侧一般是，看一眼即可）

### A-News（已选配对）
- Fed SLOOS July 2026（NDFI 五类贷款 special questions：标准处于 tighter end）
- FDIC Q2 2026 QBP + FDIC 2026 Risk Review（NDFI $1.4T @ YE2025、top-10 占 66%、PDNA 0.15% vs C&I 1.39%）
- Fitch US private credit default rate 6.0% TTM Q2 2026（record）
- Fed FSR May 2026 Box 4.1（BDC 赎回 > 申购，银行 credit line 是 backstop）
- 内部：S&P MI 季度 NDFI 系列（内网找 Q2 2026 篇）

---

## B. US Insurance

### B0. 收尾 Part 0（条目 1、2、3 的前提，见 PowerBI_Insurance_Charts_Guide.md Part 0）
- [ ] 0-1：卡片改名 "PP Bond BACV (Sched D Pt 1)"；measure 改名 PL % of PP / NAIC 3-6 % of PP
- [ ] 0-2：建 `PP % of Invested Assets`、`PP % of C&S` 两个 measure + 卡片（C1 公式）
- [ ] A3 对账：卡片 vs 脚本 log

### B1. 条目 1 — Headline baseline（读数）
- [ ] PP BACV ($bn)、Holders Count
- [ ] PP % of Invested Assets（行业级，合理区间 10–20%）
- [ ] PP % of C&S（行业级，合理区间 1x–4x）
- [ ] 脚注直接用 guide C4 那段英文（Sched D Pt 1 / ex-144A / ex-Sched BA&B / BACV / YE2025）

### B2. 条目 2 — 评级透明度分层（读数）
- [ ] 视觉②：PL / No Symbol / FE / Other 四桶的 $bn 和 %（universe 已从 $882.8bn 换成 $934.4bn，四个数都要重读）
- [ ] 文案：PL 定义写中性（"ratings not publicly disclosed; assigned via SVO PL filing"）——S&P Ratings 自己也出 private letter rating
- 外部对照：NAIC Spring 2026 — SVO 收到的 PLR filings 1,961 (2022) → 12,269 (2025)，+526%

### B3. 条目 3 — 信用质量（读数）
- [ ] 视觉①：NAIC 1 / NAIC 2 / NAIC 3-6 / Not Designated 的 %（重点 NAIC 2 和 3-6）
- 外部对照：Moody's（6/2026）private & illiquid 组合 43% NAIC 2、9% below-IG vs 整体债券 36% / 5%
  ⚠️ 文中注明 Moody's 口径更宽（$807bn，含 Sched BA 等），只做方向对照不做直接比较

### B4. 条目 4 — Migration matrix（要建）
- [ ] CapIQ：同一 screen，designation / SVO / Modifier 的季度列换成 [06/26 Q]（2026Q2，8 月中已 filing）；
      如果 CapIQ 还没加载 Q2，就用现有 [03/26 Q]
- [ ] 脚本：`LATEST_PERIODS` 加 '2026q2'（保留 '2026q1' 兜底）→ 重跑 → 出 `PowerBI_Ready_Insurance_v2.xlsx`
- [ ] ⚠️ Refresh 前删 pbix 里手建的 DAX 列 `NAIC_Sort_Latest`（脚本会自带同名列）
- [ ] Refresh 后：`NAIC_Bucket_Latest` → Sort by column `NAIC_Sort_Latest`；A3 对账（快照层数字不能变）
- [ ] 新建页 "US Insurance — Quarterly Monitor"（guide §B1b）：
      - Matrix：Rows=`NAIC_Bucket`，Columns=`NAIC_Bucket_Latest`，Values=`PP BACV`
      - 辅助列（Fact_Holdings 上建 DAX calculated column）：
        `Is_Downgraded = IF(NOT ISBLANK(Fact_Holdings[NAIC_Designation_Latest]) && Fact_Holdings[NAIC_Sort_Latest] > Fact_Holdings[NAIC_Sort], 1, 0)`
      - Measures：
        `Downgraded BACV = CALCULATE([PP BACV], Fact_Holdings[Is_Downgraded] = 1)`
        `Downgraded % of PP = DIVIDE([Downgraded BACV], [PP BACV])`
        `Disposed BACV = CALCULATE([PP BACV], ISBLANK(Fact_Holdings[NAIC_Designation_Latest]))`
      - 下调明细表：Issuer Name / Entity Name / NAIC_Designation_Raw / NAIC_Designation_Latest / PP BACV，视觉筛选 Is_Downgraded = 1
      - 页面标题注明季度："Designation Migration — YE2025 → 2026Q2"
- [ ] 读数：Downgraded BACV $ 与 % of PP、下调 issuer 数、Disposed BACV
- 文案提醒：PL 评级多在年末统一更新，年中 migration 小是正常的，第一期定位 "early read"

### B-News（已选配对）
- 内部：S&P Ratings "Scenario Analysis: North American Life Insurers Can Manage Private Credit Market Stress If One Occurs"（2026/4）；
        "Insurance In Focus: U.S. Private Credit Exposure and Capital Model Comparisons" webinar（5/19）；
        S&P MI 5/27：life insurers PP bonds 23.4% of admitted bonds (2025) vs 18.3% (2021)
- Moody's（6/8 报道）：private & illiquid FI $807bn = 20% of $4T，+$122bn YoY
- NAIC Spring 2026（PLR filings、SVO 资源、CLO RBC 12/31/2026 生效）+ KBRA 6/8（PLR review process）

---

## C. 发布前
- [ ] private / unpublished S&P ratings 一律不进邮件
- [ ] Insurance 任何总量不带 "Total"
- [ ] 和 lead 确认部门邮件里点名 entity 的尺度
- [ ] 每个数字标注数据截止日（Banks 2026Q2 Y-9C；Insurance YE2025 + migration 2026Qx）
