# [v2.0 | cell 05a, optional] Rebuild the cell-05 files of an existing run from its all_results.json, no model calls. Order: 01 -> 02 -> 05a -> 05.
REBUILD_FROM = "/dbfs/FileStore/cmbs_pipeline/outputs/cmbs_v2.0_run11_<deal>_<stamp>"   # run folder to rebuild

RUN_DIR = REBUILD_FROM.rstrip("/")
with open(os.path.join(RUN_DIR, "all_results.json"), encoding="utf-8") as f:
    RESULTS = json.load(f)
_m = re.match(r"cmbs_(?P<ver>[^_]+)_(?P<ctx>[^_]+)_(?P<deal>.+)_(?P<stamp>\d{8}_\d{6})$", os.path.basename(RUN_DIR))
assert _m, "run folder name is not in the cmbs_{version}_{run}_{deal}_{stamp} pattern"
CODE_VERSION, ctx, DEAL_TAG, run_stamp = _m["ver"], _m["ctx"], _m["deal"], _m["stamp"]
OUTPUT_STEM = f"Complai_{DEAL_TAG}_{run_stamp[:4]}-{run_stamp[4:6]}-{run_stamp[6:8]}_{CODE_VERSION}"   # same file stem as a live run
DEAL_PROFILE, DEAL_PROFILE_SOURCE, CRITERIA_CITED_FROM_DOCS = None, "", ""
print(f"rebuilding from {RUN_DIR}: {len(RESULTS)} questions | {CODE_VERSION} | {ctx} | {DEAL_TAG} -> now run cell 05")
