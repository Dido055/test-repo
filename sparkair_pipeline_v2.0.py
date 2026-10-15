# sparkair_pipeline_v2.0.py — CMBS file-review pipeline, single-file version for VS Code (one "# %%" cell per Databricks cell).
# Run top to bottom (Run All) or cell by cell in the interactive window. Setup: see README_vscode.md. Built by build_vscode.py.

# %% 01 Spark AIR API
# [v2.0 | cell 01] Spark AIR API layer: token/uid, headers, document list, advanced_chat call, run_llm_step, OUTPUT_DIR. Run first.
import json, os, re, time
from datetime import datetime
import requests

import builtins
BASE_DIR = os.environ.get("CMBS_PIPELINE_DIR", os.getcwd())   # folder with FRT_Criteria_mapping.xlsx; outputs/ is created inside it
token = os.environ.get("SPARKAIR_TOKEN") or input("Spark AIR token: ").strip()   # api token
uid = os.environ.get("SP_SSO_UID") or input("SP_SSO_UID: ").strip()   # SSO uid
if not hasattr(builtins, "display"):   # outside a Jupyter kernel (plain python run)
    def display(df): print(df.to_string(index=False))
headers = {"Authorization": f"Bearer {token}", "SP_SSO_UID": uid, "Content-Type": "application/json"}

BASE_URL = "https://ratings-genai-dashboard-rest.api.uat.spratingsvpc.com"   # UAT
APP = "sparkair"
THREAD_PREFIX = "FileReview CMBS"

TEMPERATURE = 0.1   # house default; identical runs can still flip a few answers

def get_document_list():
    """Documents visible to this user in the Spark AIR vector DB."""
    resp = requests.post(f"{BASE_URL}/user/auth_documents_list_from_vector_db", json={"app": APP}, headers=headers, timeout=240)
    resp.raise_for_status()
    return resp.json()

def doc_name(d):
    if isinstance(d, str):
        return d
    if isinstance(d, dict):
        for k in ("name", "document_name", "file_name", "title"):
            if k in d:
                return str(d[k])
    return str(d)

def chat_with_document(prompt, document_list, top_k=6, temperature=TEMPERATURE, thread_name=THREAD_PREFIX):
    """One advanced_chat (RAG) call; document_list=[] = no retrieval."""
    payload = {
        "app": APP,
        "documents": document_list,
        "retrieval_strategy": "rrf",
        "reranker": True,
        "enable_streaming": False,   # must stay False (streaming returns SSE; resp.json() fails)
        "flow_name": "advanced_chat",
        "history": [],
        "optionalParameter": {
            "Temperature": temperature,
            "Top_k": top_k,
            "Penalty": 1.1,
            "DefaultPrompt": " ",
            "prompt_id": "Default",
            "prompt_title": "Default",
        },
        "query": prompt,
        "select_all": False,
        "thread_id": str(int(time.time() * 1000)),
        "thread_name": thread_name,
    }
    resp = requests.post(f"{BASE_URL}/llm/advanced_chat", json=payload, headers=headers, timeout=240)
    resp.raise_for_status()
    return resp.json()

def extract_answer_text(resp_json):
    if isinstance(resp_json, dict):
        for key in ("answer", "response", "output", "content", "result", "text", "message"):
            val = resp_json.get(key)
            if isinstance(val, str) and val.strip():
                return val
    return json.dumps(resp_json, indent=2, ensure_ascii=False)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("OUTPUT_DIR =", OUTPUT_DIR)

ARCHIVE_RAW_CALLS = False   # True = also archive every raw call

PRINT_PREVIEW_CHARS = 2000   # console preview only; the full answer goes to all_results.json

def run_llm_step(step_name, prompt, docs, stamp, top_k=6):
    """Call the model, print a preview, return the answer text."""
    print(f"\n===== {step_name} =====")
    print("documents:", [doc_name(d) for d in docs])
    t0 = time.time()
    resp_json = chat_with_document(prompt, docs, top_k=top_k, thread_name=f"{THREAD_PREFIX} {step_name}")
    answer = extract_answer_text(resp_json)
    if ARCHIVE_RAW_CALLS:
        with open(os.path.join(OUTPUT_DIR, f"{stamp}_{step_name}_raw.json"), "w") as f:
            json.dump(resp_json, f, indent=2, ensure_ascii=False)
        with open(os.path.join(OUTPUT_DIR, f"{stamp}_{step_name}_answer.txt"), "w") as f:
            f.write(answer)
    print(f"[{time.time()-t0:.1f}s]")
    if len(answer) > PRINT_PREVIEW_CHARS:
        print(answer[:PRINT_PREVIEW_CHARS] + f"\n... [console preview capped; {len(answer)} chars total — "
              "full text is saved to all_results.json]")
    else:
        print(answer)
    return answer

# %% 02 RUN CONFIG + mapping + documents
# [v2.0 | cell 02] RUN CONFIG (the only block to edit between runs) + mapping load + document scoping. Requires cell 01.
MAPPING_PATH = os.path.join(BASE_DIR, "FRT_Criteria_mapping.xlsx")   # .xlsx or .json; columns Q_id, Question, Criteria_reference, Criteria_content, Criteria_summary
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

run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
DEAL_TAG = re.sub(r"[^A-Za-z0-9]+", "_", DEAL_NAME).strip("_") or "deal"
RUN_DIR = os.path.join(OUTPUT_DIR, f"cmbs_{CODE_VERSION}_{ctx}_{DEAL_TAG}_{run_stamp}")
OUTPUT_STEM = f"Complai_{DEAL_TAG}_{datetime.now().strftime('%Y-%m-%d')}_{CODE_VERSION}"   # file stem for the cell-05 outputs
RUN_LOG = os.path.join(RUN_DIR, f"{OUTPUT_STEM}_intermediate.md")   # every intermediate output of the run, appended as it happens

def log_md(title, body=""):
    """Append one section to the run's intermediate-output file (creates the run folder on first use)."""
    os.makedirs(RUN_DIR, exist_ok=True)
    new = not os.path.exists(RUN_LOG)
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        if new: f.write(f"# Intermediate outputs — {DEAL_NAME} — run {ctx} — {run_stamp} — {CODE_VERSION}\n")
        f.write(f"\n## {title}\n\n{body}\n")

# %% 02b deal profile (3 model calls)
# [v2.0 | cell 02b] Deal profile: three calls over the deal documents (core facts, criteria citations, per-question condition check);
# the result is injected into every Step B; raw outputs go to the run's _intermediate.md. Requires cells 01 and 02; always run, even with USE_DEAL_PROFILE = False. No sector words in the prompts.
# call 1: core facts
PROFILE_PROMPT_FACTS = f"""You are building a fact profile of the securitization transaction "{DEAL_NAME}" \
from its internal rating records (rating analysis documents, review documents, and related internal files). \
The documents MAY ALSO COVER OTHER TRANSACTIONS reviewed in the same batch: use only content about \
"{DEAL_NAME}" and ignore other transactions entirely. Copy facts exactly as the documents state them; never \
infer beyond what is written; write Unknown where the documents are silent about THIS transaction. If the \
documents span different reviews or dates and disagree on a fact, take time-varying facts from the MOST \
RECENT document and record the disagreement under CONFLICTS.

Output exactly these lines, nothing else:
TRANSACTION: what is securitized and how the structure works, in the documents' own words, 1-3 lines
ACTION_TYPE: the kind of review the documents record (new issue / surveillance / annual review) with dates
JURISDICTION: country of the assets
CLASSES_AND_RATINGS: each class of notes with its current rating
MODELS_USED: what the documents say about model use in this review, or Unknown
CONFLICTS: any material fact on which the documents disagree, as: value A (document X) vs value B (document Y) -- or: none noticed"""

# call 2: criteria citations (phrased like the citation sentences so retrieval finds them)
PROFILE_PROMPT_CITATIONS = f"""Scan the documents for citations of rating criteria articles, considering only \
the parts of the documents concerning the transaction "{DEAL_NAME}" (the documents may also cover other \
transactions — ignore those). In these documents a citation typically reads like: "... paragraph N of the \
<article name> criteria, published <date> ..." or "... our <article name> criteria published <date>, states \
...". Such citations appear inline throughout the body, inside ordinary analysis paragraphs of any kind — not \
in one dedicated criteria section.

Output format:
CITING_SENTENCES:
1. "<one sentence quoted verbatim from the documents that cites a criteria article>"
2. ... (every citing sentence you can find, up to 10; quote exactly, do not paraphrase)
CRITERIA_CITED: every distinct criteria article named in the sentences above, each with its publication \
date if stated (write "no date given" where it is not), separated by " | " -- or: none found"""

# call 3: does each question's precondition apply to this deal
def build_condition_prompt(questions):
    qlines = "\n".join(f"{q['id']}: {q['question']}" for q in questions)
    return f"""The documents in scope are internal rating records; the transaction under review is \
"{DEAL_NAME}". The documents MAY ALSO COVER OTHER TRANSACTIONS reviewed in the same batch — decide every \
precondition FOR "{DEAL_NAME}" ONLY, ignoring other transactions entirely. Below are review questions this \
file will be checked against. Many contain a precondition (they begin like "If the transaction ...", "For \
<some kind of> transactions ...", or otherwise apply only to transactions with a certain feature). Do NOT \
answer the questions; only decide the preconditions.

Decide each question in three steps, in this order:
1. CONDITION — copy the precondition from THAT question's own words. Use only the condition written in the \
question itself: never carry a condition, threshold or transaction type over from a neighbouring question, \
however similar the two questions look. A question with no precondition of its own is "no condition" even if \
the questions around it have one.
2. FACT — find the fact about this transaction, copied from the documents, that decides that condition.
3. COMPARE — direction matters. If the fact SATISFIES the condition, the verdict is "applies". The verdict \
"does not apply" is allowed ONLY when the fact shows the condition FAILS. A precondition usually names a \
CATEGORY of transactions; the transaction satisfies it whenever it belongs to that category BY MEANING, even \
if the documents use a different word for it than the question does — so "does not apply" requires that the \
transaction falls OUTSIDE the named category, and a merely different label is not enough. If the documents do \
not settle whether the transaction is inside or outside the category, the verdict is "cannot tell", never \
"does not apply".

For EACH question output exactly one line, in the same order, starting with the question id and a colon, then \
EXACTLY ONE of these four verdicts:
  applies          (the condition is met for this transaction)
  does not apply   (the documents show the condition FAILS for this transaction)
  cannot tell      (ONLY for a question that HAS a precondition which the documents do not decide; never use \
it for a question without a precondition, and never because you cannot answer the question itself)
  no condition     (the question has no precondition; it applies to every transaction)
then " -- condition: " and the question's own precondition in a few words (write none for no condition), then \
" ; fact: " and the deciding fact copied from the documents (for cannot tell: the missing fact; for no \
condition: n/a). Never write Unknown or anything else in the verdict position.

Questions:
{qlines}

Output the question lines only, nothing else."""

log_md("Run config", f"deal: {DEAL_NAME} | run label: {ctx} | code: {CODE_VERSION}\nmapping: {MAPPING_PATH} [{MAPPING_SHEET}]\n"
       f"criteria version label: {CRITERIA_VERSION_LABEL}\nquestions ({len(RUN_QIDS)}): {', '.join(RUN_QIDS)}\n"
       f"STEP_A_TOP_K={STEP_A_TOP_K} STEP_A_MODE={STEP_A_MODE} USE_DEAL_PROFILE={USE_DEAL_PROFILE} "
       f"DEMOTE_BOILERPLATE={DEMOTE_BOILERPLATE} TEMPERATURE={TEMPERATURE}\nDEAL_DOC_KEYS={DEAL_DOC_KEYS} PROFILE_DOC_KEYS={PROFILE_DOC_KEYS}\n"
       f"documents in scope: {[doc_name(d) for d in DEAL_DOCS]}")
DEAL_PROFILE, DEAL_PROFILE_SOURCE, CRITERIA_CITED_FROM_DOCS = None, "", ""
if USE_DEAL_PROFILE:
    PROFILE_DOCS = [d for d in DEAL_DOCS
                    if not PROFILE_DOC_KEYS
                    or any(_norm(k) in _norm(doc_name(d)) for k in PROFILE_DOC_KEYS)]
    if not PROFILE_DOCS:
        print(f"WARNING: PROFILE_DOC_KEYS={PROFILE_DOC_KEYS} matched nothing in scope -> profiling over ALL in-scope docs")
        PROFILE_DOCS = DEAL_DOCS
    DEAL_PROFILE_SOURCE = ", ".join(doc_name(d) for d in PROFILE_DOCS)
    print(f"profile source doc(s): {DEAL_PROFILE_SOURCE}")
    try:
        _facts = run_llm_step("deal_profile_facts", PROFILE_PROMPT_FACTS, PROFILE_DOCS, "profile", top_k=15).strip()
        log_md("Deal profile — call 1: core facts (raw)", f"source docs: {DEAL_PROFILE_SOURCE}\n\n{_facts}")
        _cites_raw = run_llm_step("deal_profile_citations", PROFILE_PROMPT_CITATIONS, PROFILE_DOCS, "profile", top_k=20).strip()
        log_md("Deal profile — call 2: criteria citations (raw)", _cites_raw)
        _mc = re.search(r"CRITERIA_CITED:.*", _cites_raw)   # only the summary line goes into the profile
        _cites = _mc.group(0) if _mc else "CRITERIA_CITED: Unknown"
        _conds = run_llm_step("deal_profile_conditions", build_condition_prompt([QBYID[qid] for qid in RUN_QIDS]),
                              PROFILE_DOCS, "profile", top_k=15).strip()
        log_md("Deal profile — call 3: condition check per question (raw)", _conds)
        DEAL_PROFILE = _facts + "\n" + _cites + "\nCONDITION_CHECK:\n" + _conds
        print("---- DEAL PROFILE (core facts + this question's condition line go into each Step B) ----\n" + DEAL_PROFILE)
    except Exception as e:
        print(f"deal profile extraction failed ({e}); continuing WITHOUT a profile")
        log_md("Deal profile — FAILED", str(e))
        DEAL_PROFILE = None

if DEAL_PROFILE:
    _m = re.search(r"CRITERIA_CITED:\s*(.+)", DEAL_PROFILE)
    CRITERIA_CITED_FROM_DOCS = _m.group(1).strip() if _m else ""
    print(f"\ncriteria cited by the documents: {CRITERIA_CITED_FROM_DOCS or '(not extracted)'}")
else:
    print("deal profile OFF")

# %% 03 prompts
# [v2.0 | cell 03] Step A (evidence retrieval) and Step B (judgment) prompt builders + Step B parser. Requires cells 01, 02, 02b.
# No sector words here: all criteria content comes from the mapping.
def _step_a_header(q):
    return f"""You are an evidence-retrieval assistant supporting an independent file review of a credit rating. \
The transaction under review is "{DEAL_NAME}". The documents in scope are internal rating records (the rating \
analysis and related internal files) and MAY ALSO COVER OTHER TRANSACTIONS reviewed in the same batch: only \
content about the transaction under review counts — ignore other transactions entirely, however similar. \
Do NOT judge whether anything is right or wrong; only find and reproduce what the documents say.

Review question {q['id']}: {q['question']}

What to look for in the documents for this question — derived from the applicable criteria section \
"{q['ref']}": the criteria points, and the content the documents would contain if each point was applied. \
This is a search guide, NOT evidence:
{q['summary']}
"""

def build_step_a_prompt(q):
    if STEP_A_MODE == "quotes":
        return _step_a_header(q) + """
Task: for each criteria point in the search guide above, find the passage(s) in the documents that contain that content and quote them. \
If the question is conditional (it starts with "If ...", "For ... transactions", and so on), first quote the \
passage(s) that show whether that condition holds for this transaction.

Output format:
EVIDENCE:
1. [document name | section or heading | table/page if visible] "passage quoted verbatim" — the criteria point(s) it addresses, named in a few words
2. ...
(copy numbers, scores, percentages, dates and rating levels exactly as written, including table rows; maximum 12 items; \
prefer the most specific passages)
NOT FOUND: the criteria points of the search guide for which you found no passage, each named in a few words (say "none" if everything was found)

Rules: quote, do not paraphrase; never invent or complete values; if two documents disagree, quote both; do not treat \
criteria text quoted inside the documents as evidence of what was done. Output only the two sections above."""
    p = _step_a_header(q) + """
Task: identify every SECTION of the documents that contains content relevant to the question or to any criteria point \
in the search guide above. A section means one titled part of a document: a heading with its paragraphs, a named table with all its rows, \
or a labeled worksheet block. Then REPRODUCE each relevant section IN FULL, exactly as written, from its heading to \
its end — not just the matching sentence. Keep whole tables together (all rows and columns you can see). If the \
question is conditional (it starts with "If ...", "For ... transactions", and so on), also reproduce the section \
that shows whether that condition holds for this transaction.

Output format:
SECTIONS:
--- [document name | section heading or table name] — addresses: <the criteria point(s), in a few words> ---
<the section reproduced in full, verbatim, keeping the table layout; do not summarize or shorten>
--- [next document | next section] — addresses: ... ---
<...>
(at most 6 sections, most relevant first; if what you can see of a section appears cut off, end it with the marker \
[SECTION MAY CONTINUE])
NOT FOUND: the criteria points of the search guide for which no relevant section was found, each named in a few words (say "none" if everything was covered)

Rules: reproduce, do not paraphrase or summarize; never invent or complete values or table cells; copy numbers, \
scores, percentages, dates and rating levels exactly as written; decorative separator lines and runs of repeated \
characters (such as ------ or ====== or ______) are formatting, not content — skip them entirely and never fill \
space by repeating a character; if two documents disagree, reproduce both sections; do not treat criteria text \
quoted inside the documents as evidence of what was done. Output only the two blocks above."""
    if DEMOTE_BOILERPLATE and DEAL_PROFILE:   # profile on: Step A skips overview sections
        p = p.replace("Output only the two blocks above.",
                      "Do not spend your section budget on the documents' standard overview sections (transaction "
                      "overview, basic transaction information) unless a criteria point in the search guide explicitly asks for them "
                      "(the deal's basic facts are already captured by a separate profile step). "
                      "Output only the two blocks above.")
    return p

# Step B rules added only when a deal profile exists
STEP_B_PROFILE_RULES = """
A deal profile extracted from the documents is provided below, including a CONDITION_CHECK line stating whether \
this question's precondition applies to this transaction; treat the profile's facts as evidence. If the condition \
does not apply, answer "N/A" and cite the deciding fact in EVIDENCE_BASIS. If the condition cannot be resolved \
because it depends on information outside the file, answer "TBD", name the missing fact in \
REVIEWER_FOLLOW_UP, and set CONFIDENCE to Low. Before answering "Yes" for a question about a particular \
analytical approach or treatment, check the eligibility preconditions stated in the criteria text against the \
evidence: a label used in the documents for a different purpose, or standard disclosure language reproduced in \
the file, is not evidence that the approach was applied. When the criteria text lists the characteristics of \
transactions eligible for an approach (for example a list introduced by "the transactions we rate using this \
approach are:"), verify EACH listed characteristic against the evidence one by one; if any characteristic \
fails or cannot be verified, the answer must not be Yes — name the failing or unverified characteristic in \
RATIONALE. If the criteria versions cited in the documents \
(the profile's CRITERIA_CITED line) differ from the criteria version being tested here{version_tag}, steps \
introduced by the tested version may be legitimately absent from the file — where that explains missing \
evidence, say so in RATIONALE. If the documents say no models were used, or a step's numbers would normally \
live in a model file rather than these documents, say so in RATIONALE rather than implying the analysts \
failed to document their work. If the Step A evidence is empty, CONFIDENCE must be Low."""

STEP_B_FRAME = """You are a compliance reviewer checking whether the rating file for the transaction "{deal}" \
applied S&P Global Ratings' criteria correctly. You are given (1) one review question, (2) the relevant criteria \
text, verbatim, and (3) evidence quoted from the internal rating records by a previous step. Judge ONLY from \
these inputs, and only as they concern this transaction.

Permissibility has three layers:
- Layer 1, explicit requirement: the criteria text says what must be done (a table value, a formula, a floor, a cap, a \
threshold, a required step). The file must follow it.
- Layer 2, discretion within the criteria: the criteria text allows a range or a judgment (words such as "may", \
"typically", "generally", "up to", "we consider", "starting point", a benchmark that can be adjusted). Any choice inside \
that range is permissible even if it relies heavily on judgment; do not second-guess it. Only check that the choice, and \
the reason where the text asks for one, are documented.
- Layer 3, not authorized: a step, adjustment, cap or benefit that the criteria text never mentions or authorizes. \
This is not permissible.
The test for any step is: can it be traced to an explicit rule or to an allowed area of discretion in the criteria text? \
Relying on judgment is not suspicious; lacking any criteria authorization is.
If the question is conditional and the evidence shows the condition is not met for this transaction (for example the \
question is about floating-rate loans and the loan is fixed-rate), answer "N/A". If the condition is met (or the question \
is unconditional) but the evidence does not show how the required step was applied, answer "TBD" (a \
documentation gap for the reviewer to resolve); do not assume it was done correctly.{profile_rules}

{profile_block}Review question {qid}: {question}

Criteria text (verbatim from the applicable S&P Global Ratings criteria; reference: {ref}):
{criteria}

Evidence from the internal rating records (Step A output):
{evidence}

Output exactly this format, one field per line, no other text:
ANSWER: Yes | No | N/A | TBD | Yes - deviated from standard approach     (Yes = applied in line with the \
criteria's standard treatment; Yes - deviated from standard approach = the criteria name a standard or typical \
treatment — a benchmark value, a table assumption, a default approach — and the file used a different one within \
allowed discretion; merely exercising judgment where the criteria set no standard is plain Yes; No = not in line \
or not authorized; N/A = the question's condition is not met for this transaction; TBD = the condition is met, or \
there is no condition, but the file does not show how the step was applied)
LAYER: Explicit requirement | Discretion within criteria | Not authorized by criteria | Not applicable | TBD
CRITERIA_BASIS: the criteria sentence(s) relied on, quoted briefly
EVIDENCE_BASIS: the evidence item(s) relied on, quoted briefly, with the document name
RATIONALE: 3-6 sentences explaining WHY the answer is what it is, by linking the quoted evidence to the criteria text. For Yes: name the criteria provision (the explicit requirement or the area of discretion) that authorizes what the file did, and show how the evidence complies with it, naming every number, score or threshold you checked. For Yes - deviated from standard approach: state the standard treatment (quote it), state what the file did instead, and quote the file's documented reasoning for the departure verbatim — the validator will separately judge whether that reasoning is well-reasoned, so reproduce it faithfully and say plainly if no reasoning is documented. For No: name the provision breached, or the step that has no authorization in the criteria text. For N/A: quote the evidence showing the condition is not met. For TBD: list the criteria point(s) for which no evidence was found and why that prevents a Yes
REVIEWER_FOLLOW_UP: what a human reviewer must still verify (model file, legal documents, missing sections), or None
CONFIDENCE: High | Medium | Low     (High = the deciding fact, number or step is quoted verbatim in the evidence or \
the profile AND the criteria provision applied reads one way only; Medium = the evidence supports the answer only \
indirectly or partially — a step asserted but not shown, a value inferred rather than stated, a criteria wording open \
to more than one reading, or a condition decided from the profile alone; Low = the answer rests on absence of \
evidence, on a characteristic that could not be verified, or on an assumption — TBD is always Low)"""

def _profile_for(qid):
    """Core profile lines + this question's CONDITION_CHECK line only; a malformed line is dropped."""
    keep = []
    for ln in DEAL_PROFILE.splitlines():
        m = re.match(r"\s*(Q\d+)\s*:", ln)
        if m:
            if m.group(1) != qid:
                continue
            if not re.search(r"applies|does not apply|cannot tell|no condition", ln, re.I):
                continue
        keep.append(ln)
    return "\n".join(keep).strip()

def build_step_b_prompt(q, evidence):
    if DEAL_PROFILE:   # read at call time
        _vt = f' ("{CRITERIA_VERSION_LABEL}")' if CRITERIA_VERSION_LABEL else ""   # version tag = mapping tab name
        pr = STEP_B_PROFILE_RULES.format(version_tag=_vt)
        src = DEAL_PROFILE_SOURCE if DEAL_PROFILE_SOURCE else "the deal documents"
        pb = (f"Deal profile (extracted from {src} in a previous step; treat these facts as evidence, and where "
              "older documents in the evidence disagree with the profile on time-varying facts, the profile is "
              "the more recent statement):\n"
              + _profile_for(q["id"]) + "\n\n")
    else:
        pr = pb = ""
    return STEP_B_FRAME.format(qid=q["id"], question=q["question"], ref=q["ref"], criteria=q["content"],
                               evidence=evidence, deal=DEAL_NAME, profile_rules=pr, profile_block=pb)

FIELDS = ["ANSWER", "LAYER", "CRITERIA_BASIS", "EVIDENCE_BASIS", "RATIONALE", "REVIEWER_FOLLOW_UP", "CONFIDENCE"]
def parse_step_b(text):
    out = {f: "" for f in FIELDS}; cur = None
    for line in text.splitlines():
        m = re.match(r"\s*\**\s*([A-Z_]+)\s*\**\s*:\s*(.*)", line)
        if m and m.group(1) in FIELDS:
            cur = m.group(1); out[cur] = m.group(2).strip()
        elif cur and line.strip():
            out[cur] += "\n" + line.rstrip()
    a = out["ANSWER"].strip().lower()
    if a.startswith("yes") and "deviat" in a:
        out["ANSWER_norm"] = "Yes - deviated from standard approach"
    elif a.startswith("tbd") or a.startswith("not evidenced"):
        out["ANSWER_norm"] = "TBD"
    elif a.startswith("n/a") or a.startswith("not applicable"):
        out["ANSWER_norm"] = "N/A"
    elif a.startswith("yes"):
        out["ANSWER_norm"] = "Yes"
    elif a.startswith("no"):
        out["ANSWER_norm"] = "No"
    else:
        out["ANSWER_norm"] = out["ANSWER"][:30]
    if out["ANSWER_norm"] == "TBD":
        out["CONFIDENCE"] = "Low"
    return out

for qid in RUN_QIDS:
    q = QBYID[qid]
    print(f"{qid}: Step A prompt ~{int(len(build_step_a_prompt(q))/3.6):>5} tok | criteria content ~{int(len(q['content'])/3.6):>5} tok")

# %% 04 loop (model calls)
# [v2.0 | cell 04] The loop: per question, Step A (RAG over the deal docs) then Step B (no docs); all_results.json is rewritten after every question,
# raw outputs go to the run's _intermediate.md. Requires cells 01-03.
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
os.makedirs(RUN_DIR, exist_ok=True)   # run_stamp, RUN_DIR, OUTPUT_STEM, RUN_LOG come from cell 02

for qid in RUN_QIDS:
    q = QBYID[qid]; t0 = time.time()
    _raw_a = run_llm_step(f"{qid}_A_evidence", build_step_a_prompt(q), DEAL_DOCS, run_stamp, top_k=STEP_A_TOP_K)
    evidence = sanitize_evidence(_raw_a)
    if len(_raw_a) - len(evidence) > 200:
        print(f"   sanitizer: removed {len(_raw_a) - len(evidence)} chars of separator/decoration junk from Step A")
    log_md(f"{qid} — Step A (raw model output, before the sanitizer; {len(_raw_a)} chars, {len(_raw_a) - len(evidence)} removed)", _raw_a)
    _cond = next((ln for ln in (DEAL_PROFILE or "").splitlines() if ln.startswith(f"{qid}:")), "(no profile / no condition line)")
    step_b_prompt = build_step_b_prompt(q, evidence)
    try:
        verdict_raw = run_llm_step(f"{qid}_B_judgment", step_b_prompt, [], run_stamp)
    except Exception as e:
        print(f"empty document list rejected ({e}); retrying with the first deal doc in scope")
        verdict_raw = run_llm_step(f"{qid}_B_judgment_retry", step_b_prompt, DEAL_DOCS[:1], run_stamp)   # fallback if documents=[] is rejected
    v = parse_step_b(verdict_raw)
    log_md(f"{qid} — Step B (raw model output)", f"condition line used: {_cond}\n\n{verdict_raw}")
    RESULTS[qid] = {"question": q["question"], "ref": q["ref"], "evidence": evidence, "verdict_raw": verdict_raw, **v,
                    "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(RUN_DIR, "all_results.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=1)   # crash-safe archive
    print(f"\n>>> {qid}: {v['ANSWER_norm']} | {v['LAYER']} | conf {v['CONFIDENCE']} | {RESULTS[qid]['seconds']}s")

print(f"\nsaved {len(RESULTS)} results -> {RUN_DIR}")

# %% 05 results
# [v2.0 | cell 05] Results: Complai_<deal>_<date>_<version>.xlsx (the sheet), .csv (same columns) and _report.md, written into RUN_DIR.
# Requires cells 01, 02 and 04 (or 05a). No numbering columns: FRT row numbers differ between workbooks; the question id stays internal.
_PROFILE, _CITED = DEAL_PROFILE, CRITERIA_CITED_FROM_DOCS   # from cell 02b

def risk_score(ans, layer, conf):
    """Risk score 1-5 from answer x layer x confidence, computed in code: 1-3 Permissible, 4-5 Recommend for Review, N/A none."""
    l = (layer or "").lower()
    if ans == "N/A":
        return None
    if ans == "Yes":
        if "explicit" in l:
            return 1
        return 2 if conf == "High" else 3
    if ans == "Yes - deviated from standard approach":
        return 3
    if ans == "TBD":
        return 4
    if ans == "No":
        return 4 if "authoriz" in l else 5
    return 4

def risk_verdict(score):
    return "N/A - out of scope" if score is None else ("Permissible" if score <= 3 else "Recommend for Review")

rows = []
for qid in [k for k in RUN_QIDS if k in RESULTS]:
    r = RESULTS[qid]
    _rs = risk_score(r["ANSWER_norm"], r["LAYER"], r["CONFIDENCE"])
    rows.append({"Question": r["question"], "Current File Review Relevance": "Yes",
                 "Application Permissible?": r["ANSWER_norm"], "Confidence": r["CONFIDENCE"],
                 "Rationale": r["RATIONALE"], "Criteria basis": r["CRITERIA_BASIS"],
                 "Evidence basis": r["EVIDENCE_BASIS"], "Evidence retrieved": r["evidence"],
                 "Reviewer follow-up": r["REVIEWER_FOLLOW_UP"], "Paragraph References": r["ref"],
                 "_layer": r["LAYER"], "_risk": _rs if _rs is not None else "", "_verdict": risk_verdict(_rs), "_qid": qid})   # xlsx-only (hidden columns)
CSV_COLUMNS = [c for c in rows[0] if not c.startswith("_")] if rows else []

# csv = the first ten columns; the last three are hidden in the xlsx
XLSX_HEADERS = ["Question", "Current File Review Relevance", "Application Permissible?", "Confidence", "Rationale",
                "Criteria basis", "Evidence basis", "Evidence retrieved", "Reviewer follow-up", "Paragraph References",
                "Layer (cross-sector view)", "Risk score (1-5, cross-sector view)", "Permissibility verdict"]
# header comments + Legend sheet
COLUMN_GUIDE = {
 "Question": "from FRT (wording as in the mapping workbook; refinements to the template wording are shown in red there)",
 "Current File Review Relevance": "from FRT",
 "Application Permissible?": ("DRAFT answer in the FRT's own vocabulary.\n"
    "Yes = the file applied the step in line with the criteria's standard treatment.\n"
    "Yes - deviated from standard approach = the criteria name a standard/typical treatment (a benchmark value, a table "
    "assumption, a default approach) and the file used a different one within the discretion the criteria allow; the "
    "rationale quotes the standard, what the file did and the file's documented reasoning so YOU can judge whether the "
    "deviation is well reasoned.\n"
    "No = the file's treatment is not in line with the criteria, or uses a step the criteria never authorize.\n"
    "N/A = the question's precondition is not met for this transaction (e.g. a floating-rate question on a fixed-rate "
    "deal); the deciding fact is quoted.\n"
    "TBD = the condition is met (or there is none) but the file does not show how the step was applied: a documentation "
    "gap for a human to resolve, NOT a finding."),
 "Confidence": ("The tool's self-assessed reliability of the row.\n"
    "High = the deciding fact, number or step is quoted verbatim from the file and the criteria provision reads one way only.\n"
    "Medium = support is indirect or partial (step asserted but not shown, value inferred, criteria wording open to more "
    "than one reading, or condition decided from the deal profile alone).\n"
    "Low = rests on absence of evidence, an unverified characteristic or an assumption; every TBD is Low.\n"
    "Treat Low as 'verify first'."),
 "Rationale": ("3-6 sentences linking the quoted evidence to the criteria text, drafted for the FRT's rationale "
    "column. For 'Yes - deviated' rows: the standard treatment, what the file did instead, and the file's reasoning."),
 "Criteria basis": "The criteria sentence(s) the answer relies on, quoted.",
 "Evidence basis": "The passage(s) of the file the answer relies on, quoted, with document name and section.",
 "Evidence retrieved": ("Everything the tool retrieved from the file for this question, verbatim: the "
    "complete audit trail behind the row (long by design). Each reproduced section is tagged 'addresses: <criteria point>' "
    "and the closing 'NOT FOUND: ...' names the criteria points of the question's search guide with no retrieved passage "
    "(the search guide is printed per question in the _report.md file). 'Not found' means not retrieved for this "
    "question, not proof that it is absent from the file."),
 "Reviewer follow-up": "What the tool could not verify and a human must check (model file, legal documents, missing sections); 'None' when nothing is outstanding.",
 "Paragraph References": "Criteria section the question is derived from (the FRT's paragraph-reference column).",
 "Layer (cross-sector view)": ("Which kind of criteria authority the answer rests on.\n"
    "Explicit requirement = a prescribed value, formula, floor, cap, threshold or required step.\n"
    "Discretion within criteria = a range or judgment the criteria allow ('may', 'typically', 'generally', 'up to').\n"
    "Not authorized by criteria = a step the criteria never mention or authorize.\n"
    "Not applicable = condition not met.  TBD = not evidenced."),
 "Risk score (1-5, cross-sector view)": ("Deterministic crosswalk to the cross-sector 1-5 scale, computed in code from answer x "
    "layer x confidence (never assigned by the model): Yes+Explicit=1; Yes+Discretion=2 (High confidence) or 3; "
    "Yes-deviated=3; TBD=4; No=4 (not authorized) or 5 (explicit breach); N/A=no score."),
 "Permissibility verdict": "Risk score <=3 = Permissible; >=4 = Recommend for Review; N/A = out of scope.",
}

report_path = os.path.join(RUN_DIR, f"{OUTPUT_STEM}_report.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"# Gemma4 draft answers — {DEAL_NAME} — run {run_stamp} — {CODE_VERSION}\n")
    f.write(f"\nMapping: {MAPPING_PATH} (criteria version tested: {CRITERIA_VERSION_LABEL or 'n/a'})\n"
            f"Documents: {[doc_name(d) for d in DEAL_DOCS]}\n")
    if _PROFILE:
        f.write(f"\n## Deal profile (injected into every Step B)\n\n```\n{_PROFILE}\n```\n")
    for n, qid in enumerate([k for k in RUN_QIDS if k in RESULTS], start=1):
        r = RESULTS[qid]
        f.write(f"\n---\n\n## {n}. ANSWER: {r['ANSWER_norm']} | Confidence: {r['CONFIDENCE']}\n")
        f.write(f"\n**Question:** {r['question']}\n\n**Criteria reference:** {r['ref']}\n")
        if qid in QBYID:
            f.write(f"\n**Search guide (the criteria points that NOT FOUND refers to):**\n\n{QBYID[qid]['summary']}\n")
        f.write(f"\n**Rationale:** {r['RATIONALE']}\n")
        f.write(f"\n**Criteria basis:** {r['CRITERIA_BASIS']}\n\n**Evidence basis:** {r['EVIDENCE_BASIS']}\n")
        f.write(f"\n**Reviewer follow-up:** {r['REVIEWER_FOLLOW_UP']}\n")
        f.write(f"\n### Evidence retrieved (verbatim)\n\n```\n{r['evidence']}\n```\n")
print("report ->", report_path)

try:
    import pandas as pd
    df = pd.DataFrame(rows)[CSV_COLUMNS]
    csv_path = os.path.join(RUN_DIR, f"{OUTPUT_STEM}.csv"); df.to_csv(csv_path, index=False)
    print("csv (same columns as the xlsx: answer + rationale + criteria/evidence basis + full retrieved evidence per question) ->", csv_path)
    _prev = df[["Application Permissible?", "Confidence", "Rationale", "Reviewer follow-up"]].astype(str)
    _prev.insert(0, "id", [r["_qid"] for r in rows])
    display(_prev)   # console preview with the internal id
except Exception as e:
    print("csv/display step problem:", e)
    for r in rows: print(r["_qid"], r["Application Permissible?"], r["Confidence"], "|", r["Rationale"][:120])
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.comments import Comment
    from openpyxl.utils import get_column_letter
    wb = Workbook(); ws = wb.active; ws.title = "Gemma_draft_answers"
    ws.append(XLSX_HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True)
        if c.value in COLUMN_GUIDE:
            c.comment = Comment(COLUMN_GUIDE[c.value], "File Review AI agent"); c.comment.width = 460; c.comment.height = 230
    NON_AI_HEADERS = {"Question", "Current File Review Relevance", "Paragraph References"}   # grey fill = not model output
    NON_AI_FILL = PatternFill("solid", fgColor="EDEDED")
    _non_ai_cols = [i for i, h in enumerate(XLSX_HEADERS, start=1) if h in NON_AI_HEADERS]
    _hidden_cols = list(range(XLSX_HEADERS.index("Paragraph References") + 2, len(XLSX_HEADERS) + 1))
    for r in rows:
        ws.append([r[h] for h in XLSX_HEADERS[:10]] + [r["_layer"], r["_risk"], r["_verdict"]])
    for col, w in zip("ABCDEFGHIJKLM", [55, 12, 14, 10, 55, 38, 38, 80, 38, 28, 22, 10, 20]):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    for i in _non_ai_cols:
        for c in ws[get_column_letter(i)]: c.fill = NON_AI_FILL
    for i in _hidden_cols:
        ws.column_dimensions[get_column_letter(i)].hidden = True
    ws.freeze_panes = "B2"   # question stays visible
    lg = wb.create_sheet("Legend"); lg.append(["Column", "Meaning and possible values"])
    for c in lg[1]: c.font = Font(bold=True)
    for h in XLSX_HEADERS: lg.append([h, COLUMN_GUIDE[h]])
    lg.append(["", ""]); lg.append(["How to read a row", "Every answer is a DRAFT. 'Evidence basis' and 'Evidence retrieved' "
        "let you verify each claim against the file; 'Reviewer follow-up' lists what the tool could not verify. "
        "TBD and Low-confidence rows are the ones to check first; N/A rows quote the fact that takes the question out of scope. "
        "Rows carry no FRT row number (numbering differs between FRT workbooks): match a row to the FRT on the question text."])
    lg.append(["Shading / hidden columns", "Grey-filled columns are NOT generated by the model (the question and its criteria "
        "reference from the mapping workbook, the template's relevance flag); unfilled columns are the model's output. "
        "The columns after 'Paragraph References' (Layer, risk score, verdict = the cross-sector view) are hidden by "
        "default — unhide them in Excel if you want that view."])
    lg.append(["Run", f"{DEAL_NAME} | run {run_stamp} | code {CODE_VERSION} | mapping {os.path.basename(MAPPING_PATH)} "
        f"[{CRITERIA_VERSION_LABEL or 'n/a'}]"])
    lg.column_dimensions["A"].width = 34; lg.column_dimensions["B"].width = 120
    for row in lg.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    xlsx_path = os.path.join(RUN_DIR, f"{OUTPUT_STEM}.xlsx"); wb.save(xlsx_path); print("xlsx ->", xlsx_path)
except Exception as e:
    print("openpyxl step skipped:", e)
