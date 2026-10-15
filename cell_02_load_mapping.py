# [v2.0 | cell 02] RUN CONFIG (the only block to edit between runs) + mapping load + document scoping. Requires cell 01.
MAPPING_PATH = "/dbfs/FileStore/cmbs_pipeline/FRT_Criteria_mapping.xlsx"   # .xlsx or .json; columns Q_id, Question, Criteria_reference, Criteria_content, Criteria_summary
MAPPING_SHEET = "GlobalCMBS_refined_v3"   # the tab holding this criteria's question set
CRITERIA_VERSION_LABEL = "Global CMBS Methodology And Assumptions (Aug. 21, 2025); CMBS Global Property Evaluation Methodology (Aug. 21, 2025)"   # criteria version tested; Step B compares the file's citations with it
DEAL_NAME = "<deal name>"   # must appear in every filename of this deal's uploaded docs
DEAL_DOC_KEYS = ["RAMP", "Master File", "single loan", "Deal overview"]   # optional doc-type filter; [] = all docs matching DEAL_NAME
RUN_QIDS = None   # None = all; or a subset, e.g. ["Q01", "Q06"]
STEP_A_TOP_K = 10   # retrieval top_k for Step A
PROFILE_DOC_KEYS = []   # docs the deal profile reads; [] = all in-scope docs
USE_DEAL_PROFILE = True   # False = no profile (cell 02b still runs)
DEMOTE_BOILERPLATE = False   # True = Step A skips overview sections
STEP_A_MODE = "sections"   # "sections" = whole sections | "quotes" = targeted passages
ctx = "run10"   # run label: bump every run
CODE_VERSION = "v2.0"   # goes into folder and file names

def load_mapping(path, sheet):
    if path.lower().endswith(".xlsx"):
        import pandas as pd
        rows = pd.read_excel(path, sheet_name=sheet).fillna("").to_dict("records")
    else:
        rows = json.load(open(path, encoding="utf-8"))["questions"]
    def _content(r):   # older mappings: core + supporting text
        return r.get("Criteria_content") or (r.get("Criteria_text_core", "") +
               ("\n\n" + r["Criteria_text_supporting"] if r.get("Criteria_text_supporting") else ""))
    return [{"id": r["Q_id"], "question": r["Question"], "ref": r["Criteria_reference"],
             "content": _content(r), "summary": r["Criteria_summary"]} for r in rows]

QUESTIONS = load_mapping(MAPPING_PATH, MAPPING_SHEET)
QBYID = {q["id"]: q for q in QUESTIONS}
RUN_QIDS = RUN_QIDS or [q["id"] for q in QUESTIONS]
print(f"loaded {len(QUESTIONS)} questions from {MAPPING_PATH} [{MAPPING_SHEET}]; running {len(RUN_QIDS)}")

all_docs = get_document_list()["documents"].copy()
print(f"documents visible in Spark AIR ({len(all_docs)}):")
for d in all_docs: print("  -", doc_name(d))

def _norm(s):
    """Name match ignoring case, spaces, underscores and punctuation."""
    return re.sub(r"[^a-z0-9]", "", s.lower())

DEAL_DOCS = [d for d in all_docs
             if _norm(DEAL_NAME) in _norm(doc_name(d))
             and (not DEAL_DOC_KEYS or any(_norm(k) in _norm(doc_name(d)) for k in DEAL_DOC_KEYS))]
skipped = [doc_name(d) for d in all_docs if _norm(DEAL_NAME) in _norm(doc_name(d)) and d not in DEAL_DOCS]
print("deal documents in scope:", [doc_name(d) for d in DEAL_DOCS])
if skipped: print("NOTE - contain DEAL_NAME but excluded by DEAL_DOC_KEYS:", skipped)
assert DEAL_DOCS, (f"no documents matched: DEAL_NAME '{DEAL_NAME}' must appear in the uploaded filenames "
                   "(and DEAL_DOC_KEYS, if set, must match too) — check the names printed above")
