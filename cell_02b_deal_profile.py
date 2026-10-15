# [v2.0 | cell 02b] Deal profile: three calls over the deal documents (core facts, criteria citations, per-question condition check);
# the result is injected into every Step B. Requires cells 01 and 02; always run, even with USE_DEAL_PROFILE = False. No sector words in the prompts.
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
        _cites_raw = run_llm_step("deal_profile_citations", PROFILE_PROMPT_CITATIONS, PROFILE_DOCS, "profile", top_k=20).strip()
        _mc = re.search(r"CRITERIA_CITED:.*", _cites_raw)   # only the summary line goes into the profile
        _cites = _mc.group(0) if _mc else "CRITERIA_CITED: Unknown"
        _conds = run_llm_step("deal_profile_conditions", build_condition_prompt([QBYID[qid] for qid in RUN_QIDS]),
                              PROFILE_DOCS, "profile", top_k=15).strip()
        DEAL_PROFILE = _facts + "\n" + _cites + "\nCONDITION_CHECK:\n" + _conds
        print("---- DEAL PROFILE (core facts + this question's condition line go into each Step B) ----\n" + DEAL_PROFILE)
    except Exception as e:
        print(f"deal profile extraction failed ({e}); continuing WITHOUT a profile")
        DEAL_PROFILE = None

if DEAL_PROFILE:
    _m = re.search(r"CRITERIA_CITED:\s*(.+)", DEAL_PROFILE)
    CRITERIA_CITED_FROM_DOCS = _m.group(1).strip() if _m else ""
    print(f"\ncriteria cited by the documents: {CRITERIA_CITED_FROM_DOCS or '(not extracted)'}")
else:
    print("deal profile OFF")
