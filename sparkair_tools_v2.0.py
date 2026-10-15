# sparkair_tools_v2.0.py — optional tools for the CMBS pipeline (VS Code, "# %%" cells). No model calls. Built by build_vscode.py.
# Cell 1 loads the API layer and the run config from sparkair_pipeline_v2.0.py (its cells 01 and 02 only).

# %% setup: cells 01-02 of the pipeline (API + config + mapping), no model calls
import os, re
_PIPELINE = os.path.join(os.environ.get("CMBS_PIPELINE_DIR", os.getcwd()), "sparkair_pipeline_v2.0.py")
_src = open(_PIPELINE, encoding="utf-8").read()
_cells = {s.split("\n", 1)[0].strip(): s.split("\n", 1)[1] for s in re.split(r"^# %% ", _src, flags=re.M)[1:]}
exec(_cells["01 Spark AIR API"]); exec(_cells["02 RUN CONFIG + mapping + documents"])
DEAL_PROFILE, DEAL_PROFILE_SOURCE, CRITERIA_CITED_FROM_DOCS = None, "", ""

# %% 05a rebuild the result files of an existing run (then run the next cell)
# [v2.0 | cell 05a, optional] Rebuild the cell-05 files of an existing run from its all_results.json, no model calls. Order: 01 -> 02 -> 05a -> 05.
REBUILD_FROM = os.path.join(OUTPUT_DIR, "cmbs_v2.0_run11_<deal>_<stamp>")   # run folder to rebuild

RUN_DIR = REBUILD_FROM.rstrip("/")
with open(os.path.join(RUN_DIR, "all_results.json"), encoding="utf-8") as f:
    RESULTS = json.load(f)
_m = re.match(r"cmbs_(?P<ver>[^_]+)_(?P<ctx>[^_]+)_(?P<deal>.+)_(?P<stamp>\d{8}_\d{6})$", os.path.basename(RUN_DIR))
assert _m, "run folder name is not in the cmbs_{version}_{run}_{deal}_{stamp} pattern"
CODE_VERSION, ctx, DEAL_TAG, run_stamp = _m["ver"], _m["ctx"], _m["deal"], _m["stamp"]
OUTPUT_STEM = f"Complai_{DEAL_TAG}_{run_stamp[:4]}-{run_stamp[4:6]}-{run_stamp[6:8]}_{CODE_VERSION}"   # same file stem as a live run
RUN_LOG = os.path.join(RUN_DIR, f"{OUTPUT_STEM}_intermediate.md")
DEAL_PROFILE, DEAL_PROFILE_SOURCE, CRITERIA_CITED_FROM_DOCS = None, "", ""
print(f"rebuilding from {RUN_DIR}: {len(RESULTS)} questions | {CODE_VERSION} | {ctx} | {DEAL_TAG} -> now run cell 05")

# %% 05 results (re-run after 05a)
exec(_cells["05 results"])

# %% 07 compare two runs
# [v2.0 | cell 07, optional] Compare two runs' answers question by question (stability check), no API calls. None/None = the two newest run folders.
RUN_DIR_A = None   # e.g. ".../outputs/cmbs_v2.0_run11_<deal>_<stamp>"
RUN_DIR_B = None   # None, None = second-newest vs newest

import glob
_folders = sorted(glob.glob(os.path.join(OUTPUT_DIR, "cmbs_*")), key=os.path.getmtime)
if RUN_DIR_A is None or RUN_DIR_B is None:
    assert len(_folders) >= 2, f"need at least two run folders under {OUTPUT_DIR}; found {len(_folders)}"
    RUN_DIR_A, RUN_DIR_B = _folders[-2], _folders[-1]

def _load_results(run_dir):
    with open(os.path.join(run_dir, "all_results.json"), encoding="utf-8") as f:
        return json.load(f)

A, B = _load_results(RUN_DIR_A), _load_results(RUN_DIR_B)
rows = []
for qid in sorted(set(A) | set(B), key=lambda q: int(q[1:])):
    a, b = A.get(qid, {}), B.get(qid, {})
    same = a.get("ANSWER_norm") == b.get("ANSWER_norm")
    rows.append({"Q": qid, "Run A": a.get("ANSWER_norm", "-"), "Run B": b.get("ANSWER_norm", "-"),
                 "Match": "SAME" if same else "FLIP",
                 "Conf A": a.get("CONFIDENCE", "-"), "Conf B": b.get("CONFIDENCE", "-")})

import pandas as pd
dfc = pd.DataFrame(rows)
try:
    display(dfc)
except Exception:
    print(dfc.to_string(index=False))
flips = [r["Q"] for r in rows if r["Match"] == "FLIP"]
print(f"\n{len(rows) - len(flips)}/{len(rows)} questions stable; FLIPPED: {flips or 'none'}")
print(f"A = {RUN_DIR_A}\nB = {RUN_DIR_B}")
cmp_path = os.path.join(RUN_DIR_B, "run_comparison.csv")
dfc.to_csv(cmp_path, index=False)
print("comparison csv ->", cmp_path)
