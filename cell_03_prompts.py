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
