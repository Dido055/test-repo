# [v2.0 | cell 01] Spark AIR API layer: widgets, headers, document list, advanced_chat call, run_llm_step, OUTPUT_DIR. Run first.
import json, os, re, time
from datetime import datetime
import requests

dbutils.widgets.text("Token", "")   # api token
dbutils.widgets.text("UID", "")   # SSO uid
token = dbutils.widgets.get("Token")
uid = dbutils.widgets.get("UID")
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

OUTPUT_DIR = None   # DBFS first: survives a cluster restart
for cand in ("/dbfs/FileStore/cmbs_pipeline/outputs", "/tmp/cmbs_pipeline_outputs"):
    try:
        os.makedirs(cand, exist_ok=True)
        with open(os.path.join(cand, ".write_test"), "w") as f: f.write("ok")
        OUTPUT_DIR = cand; break
    except Exception as e:
        print(f"cannot write to {cand}: {e}")
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
