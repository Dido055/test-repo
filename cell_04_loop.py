# [v2.0 | cell 04] The loop: per question, Step A (RAG over the deal docs) then Step B (no docs); all_results.json is rewritten after every question. Requires cells 01-03.
EVIDENCE_MAX_CHARS = 45_000   # cap so Step A cannot overflow the Step B context

def sanitize_evidence(text):
    if not text:
        return text
    kept = [ln for ln in text.splitlines()
            if len(ln.strip()) < 4 or re.search(r"[A-Za-z0-9]", ln)]
    text = re.sub(r"([-=_~.*#•·+—–…|─-╿])\1{3,}", r"\1\1\1", "\n".join(kept))
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) > EVIDENCE_MAX_CHARS:
        text = text[:EVIDENCE_MAX_CHARS] + "\n[EVIDENCE TRUNCATED FOR LENGTH]"
    return text

RESULTS = {}
run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
DEAL_TAG = re.sub(r"[^A-Za-z0-9]+", "_", DEAL_NAME).strip("_") or "deal"
RUN_DIR = os.path.join(OUTPUT_DIR, f"cmbs_{CODE_VERSION}_{ctx}_{DEAL_TAG}_{run_stamp}")
os.makedirs(RUN_DIR, exist_ok=True)
OUTPUT_STEM = f"Complai_{DEAL_TAG}_{datetime.now().strftime('%Y-%m-%d')}_{CODE_VERSION}"   # file stem for the cell-05 outputs

for qid in RUN_QIDS:
    q = QBYID[qid]; t0 = time.time()
    _raw_a = run_llm_step(f"{qid}_A_evidence", build_step_a_prompt(q), DEAL_DOCS, run_stamp, top_k=STEP_A_TOP_K)
    evidence = sanitize_evidence(_raw_a)
    if len(_raw_a) - len(evidence) > 200:
        print(f"   sanitizer: removed {len(_raw_a) - len(evidence)} chars of separator/decoration junk from Step A")
    step_b_prompt = build_step_b_prompt(q, evidence)
    try:
        verdict_raw = run_llm_step(f"{qid}_B_judgment", step_b_prompt, [], run_stamp)
    except Exception as e:
        print(f"empty document list rejected ({e}); retrying with the first deal doc in scope")
        verdict_raw = run_llm_step(f"{qid}_B_judgment_retry", step_b_prompt, DEAL_DOCS[:1], run_stamp)   # fallback if documents=[] is rejected
    v = parse_step_b(verdict_raw)
    RESULTS[qid] = {"question": q["question"], "ref": q["ref"], "evidence": evidence, "verdict_raw": verdict_raw, **v,
                    "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(RUN_DIR, "all_results.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=1)   # crash-safe archive
    print(f"\n>>> {qid}: {v['ANSWER_norm']} | {v['LAYER']} | conf {v['CONFIDENCE']} | {RESULTS[qid]['seconds']}s")

print(f"\nsaved {len(RESULTS)} results -> {RUN_DIR}")
