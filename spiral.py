#!/usr/bin/env python3
"""
SPIRAL - The One True Chat
Online → Local fallback | Auto-logs to Obsidian | Multi-agent | Tools
"""
import requests, json, re, subprocess, os, sys, shlex, asyncio, hashlib
from pathlib import Path
from datetime import datetime
from textwrap import shorten
import psutil
import yaml
from typing import Dict, Any
try:
    import pandas as pd
except Exception:  # pandas optional for Excel previews
    pd = None
from master_agent_ecosystem import Task, TaskPriority
from specialized_agents import CsvExcelExpertAgent
from tools.obsidian_logger import log_chat, log_build, log_training
from autonomous_intelligence import get_autonomous_intelligence
from contextual_reasoning import create_reasoning_engine

# ===== CONFIG ===== - Enhanced with Smart Cloud Router Integration
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
FREE_KEYS = {
    "google/gemini-2.0-flash-exp:free": os.environ.get("GEMINI_FREE_KEY", "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"),
    "nvidia/nemotron-nano-9b-v2:free": os.environ.get("NEMOTRON_FREE_KEY", "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"),
    "moonshotai/kimi-dev-72b:free": os.environ.get("KIMI_FREE_KEY", "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")
}
OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "moonshotai/kimi-dev-72b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODELS = ["llama3-70b-8192", "mixtral-8x7b-32768"]
OLLAMA_MODEL = "llama3.1:8b"
ROOT_DIR = Path(__file__).resolve().parent
OBSIDIAN = Path.home() / "Documents/Obsidian/OMAi/Spiral"
CIS_BASE_URL = os.environ.get("CIS_BASE_URL", "http://localhost:8012")
ECIR_BUFFER = Path("/tmp/ecir.json")
CERT_OUTPUT_DIR = Path.home() / "Documents/Obsidian/OMAi/Build-Logs/Certificates"
OWNER = os.environ.get("SPIRAL_OWNER", "Declan")
TEMPLATE_CACHE = {}
SCAN_MAX_CHARS = 8000
ALLOWLIST_PATH = ROOT_DIR / "config/doc_access_allowlist.yaml"
DEFAULT_ALLOW_PATHS = [
    "~/Documents",
    "~/Downloads/attachments",
    "~/Downloads/certsamples",
    "~/Documents/Obsidian",
]
DOC_ALLOWLIST: list[str] = []
CSV_AGENT: CsvExcelExpertAgent | None = None
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
DATA_SOURCES_PATH = TEMPLATE_DIR / "data_sources.json"
BUILD_HASHES_PATH = TEMPLATE_DIR / "build_hashes.json"

# Colors
C, G, Y, R, M, BOLD, X = "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[35m", "\033[1m", "\033[0m"

# ===== SETUP =====
OBSIDIAN.mkdir(parents=True, exist_ok=True)
CERT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SESSION = OBSIDIAN / f"{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
SESSION_ID = SESSION.stem
SESSION.write_text(f"# Spiral Session\n{datetime.now()}\n\n")

conversation, stats = [], {
    "openrouter": 0,
    "groq": 0,
    "local": 0,
    "files": 0,
    "openrouter_fail": 0,
    "groq_fail": 0,
}
current_openrouter = 0
current_groq = 0

# ===== CORE FUNCTIONS =====
def log(user, ai, agent):
    """Log to Obsidian"""
    SESSION.write_text(SESSION.read_text() + f"\n### {datetime.now().strftime('%H:%M')} - {agent}\n**You:** {user}\n**Spiral:** {ai}\n\n")
    try:
        log_chat(SESSION_ID, OWNER, user, ai, agent, tags=[agent])
    except Exception:
        pass


def cis_available() -> bool:
    try:
        requests.get(f"{CIS_BASE_URL}/health", timeout=3)
        return True
    except requests.RequestException:
        return False


def _load_ecir_payload():
    if not ECIR_BUFFER.exists():
        return None
    try:
        return json.loads(ECIR_BUFFER.read_text())
    except Exception:
        return None


def _save_ecir_payload(payload):
    ECIR_BUFFER.parent.mkdir(parents=True, exist_ok=True)
    ECIR_BUFFER.write_text(json.dumps(payload, indent=2))


def _kv_pairs(raw: str):
    pairs = re.findall(r'(\w+)=(".*?"|\'.*?\'|\S+)', raw)
    data = {}
    for key, value in pairs:
        cleaned = value.strip("\"'")
        data[key.lower()] = cleaned
    return data


def _bool_from_text(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y", "on"}


def _float_or_default(value, default):
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fetch_templates(force=False):
    global TEMPLATE_CACHE
    if TEMPLATE_CACHE and not force:
        return TEMPLATE_CACHE
    try:
        resp = requests.get(f"{CIS_BASE_URL.rstrip('/')}/templates", timeout=5)
        resp.raise_for_status()
        templates = resp.json().get("templates", [])
        TEMPLATE_CACHE = {tpl["id"]: tpl for tpl in templates}
    except requests.RequestException:
        TEMPLATE_CACHE = {}
    return TEMPLATE_CACHE


def _match_template_from_text(text: str):
    templates = _fetch_templates()
    if not templates:
        return None
    lower = text.lower()
    for tpl in templates.values():
        if tpl["id"] in lower or tpl.get("name", "").lower() in lower:
            return tpl["id"]
    return None


def _get_template_detail(template_id: str):
    if not template_id:
        return None
    templates = _fetch_templates()
    if template_id in templates:
        return templates[template_id]
    try:
        resp = requests.get(f"{CIS_BASE_URL.rstrip('/')}/templates/{template_id}", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        TEMPLATE_CACHE[template_id] = {
            "id": data.get("id", template_id),
            "name": data.get("name", template_id),
            "description": data.get("description"),
            "certificate_type": data.get("certificate_type"),
            "source": data.get("source"),
        }
        return data
    except requests.RequestException:
        return None


def _cis_post(path: str, payload, params=None):
    url = f"{CIS_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    resp = requests.post(url, json=payload, params=params or {}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _ensure_csv_agent() -> CsvExcelExpertAgent:
    global CSV_AGENT
    if CSV_AGENT is None:
        CSV_AGENT = CsvExcelExpertAgent()
    return CSV_AGENT


def _run_csv_agent_task(task_type: str, title: str, description: str, input_data: dict) -> Dict[str, Any]:
    agent = _ensure_csv_agent()
    task = Task(
        id=f"{task_type}_{int(datetime.now().timestamp())}",
        title=title,
        description=description,
        task_type=task_type,
        priority=TaskPriority.MEDIUM,
        complexity=5,
        required_capabilities=["excel_analysis"],
        input_data=input_data
    )
    return asyncio.run(agent.process_task(task))


def _load_doc_allowlist():
    global DOC_ALLOWLIST
    entries = DEFAULT_ALLOW_PATHS.copy()
    if ALLOWLIST_PATH.exists():
        try:
            data = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
            entries = data.get("allowed", entries)
        except Exception:
            entries = DEFAULT_ALLOW_PATHS.copy()
    normalized = []
    for entry in entries:
        try:
            normalized.append(str(Path(entry).expanduser().resolve()))
        except Exception:
            continue
    DOC_ALLOWLIST = normalized


def _save_doc_allowlist():
    data = {"allowed": DOC_ALLOWLIST}
    ALLOWLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    ALLOWLIST_PATH.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _load_json_file(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_json_file(path: Path, data: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_data_sources() -> Dict[str, Any]:
    return _load_json_file(DATA_SOURCES_PATH)


def _save_data_sources(data: Dict[str, Any]):
    _save_json_file(DATA_SOURCES_PATH, data)


def _load_build_hashes() -> Dict[str, Any]:
    return _load_json_file(BUILD_HASHES_PATH)


def _save_build_hashes(data: Dict[str, Any]):
    _save_json_file(BUILD_HASHES_PATH, data)


def _resolve_user_path(path_str: str) -> Path:
    expanded = Path(path_str.strip().strip('"').strip("'")).expanduser()
    return expanded.resolve()


def _path_allowed(path: Path) -> bool:
    if not DOC_ALLOWLIST:
        _load_doc_allowlist()
    try:
        resolved = path.resolve()
        home = Path.home().resolve()
    except Exception:
        return False
    if not str(resolved).startswith(str(home)):
        return False
    for entry in DOC_ALLOWLIST:
        try:
            root = Path(entry).expanduser().resolve()
            if str(resolved).startswith(str(root)):
                return True
        except Exception:
            continue
    return False


def _extract_pdf_text(path: Path, max_chars: int = SCAN_MAX_CHARS) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout[:max_chars]
    except FileNotFoundError:
        pass
    except subprocess.SubprocessError:
        pass

    # Fallback to PyPDF2 if available
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception:
        return ""
    try:
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
            if sum(len(p) for p in pages) >= max_chars:
                break
        return "\n".join(pages)[:max_chars]
    except Exception:
        return ""


def _summarize_text_snippet(snippet: str) -> str:
    msgs = [
        {"role": "system", "content": "You summarize electrical certificates. Highlight board info, circuit rows, and observations."},
        {"role": "user", "content": f"Summarize this excerpt:\n\n{snippet}"},
    ]
    response, _ = call_best_online(msgs)
    if not response:
        response, _ = call_local(msgs)
    return response or "Unable to summarize document excerpt."


def _extract_excel_text(path: Path, max_chars: int = SCAN_MAX_CHARS) -> str:
    if pd is None:
        return ""
    try:
        sheet_names = pd.ExcelFile(path).sheet_names
        primary_sheet = sheet_names[0] if sheet_names else None
        if not primary_sheet:
            return ""
        df = pd.read_excel(path, sheet_name=primary_sheet)
        preview = df.head(20).to_csv(index=False)
        header = f"Sheet: {primary_sheet}\n\n"
        return (header + preview)[:max_chars]
    except Exception:
        return ""


def handle_document_scan(user_input: str) -> bool:
    tokens = user_input.strip()
    if not tokens:
        return False

    command = None
    path_part = None
    if tokens.lower().startswith(("scan ", "read ", "extract ")):
        command, path_part = tokens.split(" ", 1)
        path_part = path_part.strip()
    elif tokens.startswith("/") or tokens.startswith("~"):
        path_part = tokens

    if not path_part:
        return False

    try:
        file_path = _resolve_user_path(path_part)
    except Exception:
        return False

    if not file_path.exists():
        print(f"{Y}⚠️ File not found: {file_path}{X}")
        return True
    if not _path_allowed(file_path):
        print(f"{Y}⚠️ Path not permitted. Use `/allow-read \"{file_path.parent}\"` to grant access.{X}")
        return True
    suffix = file_path.suffix.lower()
    supported = {".pdf", ".xls", ".xlsx"}
    if suffix not in supported:
        print(f"{Y}⚠️ Unsupported format {suffix}. Currently supported: PDF, XLS, XLSX.{X}")
        return True

    print(f"{C}📄 Scanning document: {file_path}{X}")
    if suffix == ".pdf":
        text = _extract_pdf_text(file_path)
        handler = "pdf"
    else:
        text = _extract_excel_text(file_path)
        handler = "excel"
    if not text:
        if handler == "pdf":
            print(f"{R}❌ Unable to extract text from PDF. Ensure pdftotext is installed or the PDF contains selectable text.{X}")
        else:
            print(f"{R}❌ Unable to read Excel file. Ensure pandas/openpyxl are installed and file is not corrupted.{X}")
        return True

    preview = shorten(text, width=600, placeholder=" ...")
    print(f"{G}Preview:{X}\n{preview}\n")

    summary = _summarize_text_snippet(text[:SCAN_MAX_CHARS])
    print(f"{G}Summary:{X}\n{summary}\n")

    log_build(
        "scan_document",
        {"path": str(file_path), "chars": len(text), "handler": handler},
        ok=True,
        tags=["docs", "scan"],
    )
    return True


def handle_excel_agent_commands(user_input: str) -> bool:
    stripped = user_input.strip()
    lower = stripped.lower()

    if not (lower.startswith("/excel") or lower.startswith("/reconcile-ecir")):
        return False

    base_pairs = _kv_pairs(user_input)
    tokens = shlex.split(user_input)
    token_pairs = {}
    for tok in tokens[1:]:
        if "=" in tok:
            key, value = tok.split("=", 1)
            token_pairs[key.lower()] = value
    pairs = {**base_pairs, **token_pairs}

    def extract_path():
        if "path" in pairs:
            return pairs["path"]
        for token in tokens[1:]:
            if not token.startswith("--") and not token.startswith("sheet="):
                return token
        return None

    if lower.startswith("/excel-summary"):
        path = extract_path()
        if not path:
            print(f"{Y}⚠️ Usage: /excel-summary path=/path/to/workbook.xlsx{X}")
            return True
        result = _run_csv_agent_task(
            "excel_summary",
            "Excel workbook summary",
            "Summarize workbook sheets",
            {"path": path}
        )
        if not result.get("success"):
            print(f"{R}❌ Excel summary failed: {result.get('error')}{X}")
            return True
        print(f"{G}📊 Workbook: {result['workbook']} ({result['sheet_count']} sheets){X}")
        for detail in result["details"]:
            print(f"  • {detail['sheet']}: {detail['rows']} rows / {detail['columns']} cols")
        log_build("excel_summary", {"workbook": result["workbook"], "sheets": result["sheet_count"]}, ok=True, tags=["excel", "agent"])
        return True

    elif lower.startswith("/excel-sheet"):
        path = extract_path()
        sheet = pairs.get("sheet")
        if not path or not sheet:
            print(f"{Y}⚠️ Usage: /excel-sheet sheet=\"Sheet1\" path=/path/to/workbook.xlsx [max_rows=200] [output=/tmp/out.csv]{X}")
            return True
        input_data = {"path": path, "sheet": sheet}
        if "max_rows" in pairs:
            input_data["max_rows"] = int(pairs["max_rows"])
        if "output" in pairs:
            input_data["output_path"] = pairs["output"]
        result = _run_csv_agent_task(
            "excel_sheet_extract",
            "Excel sheet extract",
            "Extract sheet preview",
            input_data
        )
        if not result.get("success"):
            print(f"{R}❌ Sheet extraction failed: {result.get('error')}{X}")
            return True
        print(f"{G}📄 Sheet {result['sheet']} ({result['rows']} rows){X}")
        print(result["csv_preview"][:1000])
        if result.get("saved_path"):
            print(f"{C}Saved copy → {result['saved_path']}{X}")
        log_build("excel_sheet_extract", {"workbook": result["workbook"], "sheet": result["sheet"]}, ok=True, tags=["excel", "agent"])
        return True

    elif lower.startswith("/excel-validate"):
        path = extract_path()
        if not path:
            print(f"{Y}⚠️ Usage: /excel-validate path=/path/to/workbook.xlsx [sheet=Sheet1] [required=\"col1,col2\"] [numeric=\"Rating (A)\"]{X}")
            return True
        input_data = {"path": path}
        if "sheet" in pairs:
            input_data["sheet"] = pairs["sheet"]
        if "required" in pairs:
            input_data["required_columns"] = [c.strip() for c in pairs["required"].split(",") if c.strip()]
        if "numeric" in pairs:
            input_data["numeric_columns"] = [c.strip() for c in pairs["numeric"].split(",") if c.strip()]
        result = _run_csv_agent_task(
            "excel_validation",
            "Excel validation",
            "Validate workbook structure",
            input_data
        )
        if not result.get("success"):
            print(f"{R}❌ Validation failed: {result.get('error')}{X}")
            return True
        status_icon = "✅" if result["status"] == "ok" else "⚠️"
        print(f"{status_icon} Validation status: {result['status']} (sheets checked: {len(result['checked_sheets'])})")
        for issue in result["issues"]:
            print(f"  • Sheet {issue.get('sheet')}: {issue.get('issue')} {issue.get('columns') or issue.get('column')}")
        log_build("excel_validation", {"workbook": result["workbook"], "status": result["status"], "issues": len(result["issues"])}, ok=True, tags=["excel", "agent"])
        return True

    elif lower.startswith("/reconcile-ecir"):
        path = extract_path()
        pdf = pairs.get("pdf")
        sheet = pairs.get("sheet")
        if not path or not pdf:
            print(f"{Y}⚠️ Usage: /reconcile-ecir path=/path/to/workbook.xlsx pdf=/path/to/certificate.pdf [sheet=SheetName]{X}")
            return True
        input_data = {"path": path, "pdf_path": pdf}
        if sheet:
            input_data["sheet"] = sheet
        result = _run_csv_agent_task(
            "excel_reconcile",
            "ECIR Reconciliation",
            "Align PDF headers with workbook columns",
            input_data
        )
        if not result.get("success"):
            print(f"{R}❌ Reconciliation failed: {result.get('error')}{X}")
            return True
        print(f"{G}🔗 Reconciled sheet {result['sheet']} vs PDF headers{X}")
        if result["missing_in_excel"]:
            print(f"{Y}Missing in Excel:{X} {', '.join(result['missing_in_excel'])}")
        if result["extra_in_excel"]:
            print(f"{C}Extra columns in Excel:{X} {', '.join(result['extra_in_excel'])}")
        print(f"{C}Recommended order:{X} {', '.join(result['recommended_order'])}")
        log_build("excel_reconcile", {"workbook": result["workbook"], "sheet": result["sheet"], "missing": len(result["missing_in_excel"])}, ok=True, tags=["excel", "agent"])
        log_training("ECIR reconciliation", {"workbook": result["workbook"], "sheet": result["sheet"], "missing": result["missing_in_excel"], "extra": result["extra_in_excel"]}, severity="info", tags=["excel", "ecir"])
        return True

    else:
        return False


def _template_path(template_id: str) -> Path:
    safe_id = template_id.strip().replace(" ", "_")
    return TEMPLATE_DIR / f"{safe_id}.template.json"


def _load_template(template_id: str) -> Dict[str, Any]:
    path = _template_path(template_id)
    if not path.exists():
        raise FileNotFoundError(f"Template {template_id} not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_template(template_id: str, data: Dict[str, Any]):
    path = _template_path(template_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _df_to_markdown(df):
    if df.empty:
        return "_No circuit rows available._"
    headers = list(map(str, df.columns))
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join([" --- " for _ in headers]) + "|"]
    for row in df.itertuples(index=False):
        values = ["" if (value != value) else str(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def handle_template_commands(user_input: str) -> bool:
    stripped = user_input.strip()
    lower = stripped.lower()
    if not lower.startswith("/template"):
        return False

    tokens = shlex.split(user_input)
    kv = {}
    for token in tokens[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            kv[key.lower()] = value

    cmd = tokens[0].lower()
    data_sources = _load_data_sources()

    if cmd == "/template-new":
        template_id = kv.get("id")
        if not template_id:
            print(f"{Y}⚠️ Template ID required.{X}")
            print(f"{C}Example: /template-new id=my_eicr title=\"Domestic EICR\"{X}")
            return True
        title = kv.get("title", template_id)
        template = {
            "template_id": template_id,
            "version": 1,
            "title": title,
            "sections": [
                {
                    "id": "client_details",
                    "title": "Client / Installation",
                    "slots": [
                        {"key": "client.name", "label": "Client Name", "type": "text", "required": True},
                        {"key": "installation.address", "label": "Address", "type": "multiline", "required": True},
                        {"key": "supply.characteristics", "label": "Supply Characteristics", "type": "dropbox", "source": "supply_characteristics", "required": True}
                    ]
                },
                {
                    "id": "circuit_schedule",
                    "title": "Schedule of Test Results",
                    "slots": [
                        {
                            "key": "circuits",
                            "label": "Circuits",
                            "type": "dropbox-table",
                            "source": "circuit_chart",
                            "rules": {
                                "omit_spares": True,
                                "mark_unused_as": "Breaker not in use",
                                "apply_order_from": "pdf_reconciliation"
                            }
                        }
                    ]
                }
            ],
            "uniqueness": {
                "salt_fields": ["client.name", "installation.address"],
                "deny_duplicate_hash": True
            }
        }
        _write_template(template_id, template)
        print(f"{G}✅ Created template {template_id} at {_template_path(template_id)}{X}")
        return True

    if cmd == "/template-bind":
        template_id = kv.get("id")
        if not template_id:
            print(f"{Y}⚠️ Template ID required.{X}")
            print(f"{C}Example: /template-bind id=my_eicr source=supply_characteristics:TN-C-S{X}")
            return True
        template_sources = data_sources.get(template_id, {})
        source_specs = [token.split("=", 1)[1] for token in tokens[1:] if token.startswith("source=")]
        if not source_specs:
            print(f"{Y}⚠️ Data source binding required.{X}")
            print(f"{C}Example: /template-bind id=my_eicr source=supply:TN-C-S source=phase:Single{X}")
            return True
        for spec in source_specs:
            if ":" not in spec:
                print(f"{Y}⚠️ Invalid source '{spec}'. Use name:value.{X}")
                continue
            src_name, src_value = spec.split(":", 1)
            src_name = src_name.strip()
            src_value = src_value.strip()
            if src_name == "circuit_chart":
                entry = {
                    "type": "csv",
                    "path": str(Path(src_value).expanduser())
                }
                if "sheet" in kv:
                    entry["sheet"] = kv["sheet"]
                if "workbook" in kv:
                    entry["workbook"] = str(Path(kv["workbook"]).expanduser())
                if "pdf" in kv:
                    entry["pdf"] = str(Path(kv["pdf"]).expanduser())
                template_sources["circuit_chart"] = entry
            elif src_name == "supply_characteristics":
                values = [item.strip() for item in src_value.split(",") if item.strip()]
                template_sources["supply_characteristics"] = {"type": "kv", "values": values}
            else:
                template_sources[src_name] = {"type": "text", "value": src_value}
        data_sources[template_id] = template_sources
        _save_data_sources(data_sources)
        print(f"{G}✅ Updated sources for {template_id}.{X}")
        return True

    if cmd == "/template-build":
        template_id = kv.get("id")
        if not template_id:
            print(f"{Y}⚠️ Provide template id via id=<value>.{X}")
            return True
        template = _load_template(template_id)
        sources = data_sources.get(template_id)
        if not sources:
            print(f"{Y}⚠️ No data sources bound to {template_id}. Use /template-bind first.{X}")
            return True

        field_values = {}
        for key, value in kv.items():
            if key.startswith("field."):
                field_key = key[len("field.") :]
                field_values[field_key] = value

        supply_entries = sources.get("supply_characteristics", {})
        supply_values = supply_entries.get("values", [])

        circuit_source = sources.get("circuit_chart")
        if not circuit_source:
            print(f"{Y}⚠️ circuit_chart source missing for {template_id}.{X}")
            return True
        if pd is None:
            print(f"{R}❌ pandas is required to build templates with circuit tables.{X}")
            return True
        circuit_path = Path(circuit_source["path"]).expanduser()
        if not circuit_path.exists():
            print(f"{Y}⚠️ Circuit CSV not found: {circuit_path}{X}")
            return True
        df = pd.read_csv(circuit_path)
        rules = template["sections"][1]["slots"][0].get("rules", {})
        if rules.get("omit_spares"):
            desc_cols = [col for col in df.columns if "description" in col.lower()]
            if desc_cols:
                mask = True
                for col in desc_cols:
                    mask &= ~df[col].astype(str).str.contains("spare", case=False, na=False)
                df = df[mask]
        if rules.get("mark_unused_as"):
            note_col = "Status"
            desc_cols = [col for col in df.columns if "description" in col.lower()]
            unused_mask = None
            if desc_cols:
                for col in desc_cols:
                    col_mask = df[col].astype(str).str.contains("unused", case=False, na=False) | (df[col].astype(str).str.strip() == "")
                    unused_mask = col_mask if unused_mask is None else (unused_mask | col_mask)
            if unused_mask is not None:
                if note_col not in df.columns:
                    df[note_col] = ""
                df.loc[unused_mask, note_col] = rules["mark_unused_as"]
        if rules.get("apply_order_from") == "pdf_reconciliation":
            workbook = circuit_source.get("workbook")
            pdf_path = circuit_source.get("pdf")
            sheet_name = circuit_source.get("sheet")
            if workbook and pdf_path and sheet_name:
                recon = _run_csv_agent_task(
                    "excel_reconcile",
                    "Template auto-reconcile",
                    "Align order for template build",
                    {"path": workbook, "pdf_path": pdf_path, "sheet": sheet_name}
                )
                if recon.get("success"):
                    order = recon.get("recommended_order", [])
                    ordered_cols = [col for col in order if col in df.columns]
                    df = df[ordered_cols + [c for c in df.columns if c not in ordered_cols]]

        validation_status = None
        workbook_path = circuit_source.get("workbook")
        if workbook_path:
            val = _run_csv_agent_task(
                "excel_validation",
                "Template validation",
                "Ensure circuit schedule integrity",
                {"path": workbook_path, "sheet": circuit_source.get("sheet")}
            )
            if val.get("success"):
                validation_status = val.get("status")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_target = kv.get("out") or str(TEMPLATE_DIR / f"{template_id}_{timestamp}.md")
        output_path = Path(output_target).expanduser()
        pdf_requested = output_path.suffix.lower() == ".pdf"
        if pdf_requested:
            actual_path = output_path.with_suffix(".md")
        else:
            actual_path = output_path

        lines = [f"# {template.get('title', template_id)}", f"_Generated {datetime.now().isoformat()}_"]
        for section in template.get("sections", []):
            lines.append(f"\n## {section.get('title', section.get('id'))}")
            for slot in section.get("slots", []):
                slot_type = slot.get("type")
                label = slot.get("label", slot.get("key"))
                key = slot.get("key")
                if slot_type in ("text", "multiline"):
                    value = field_values.get(key, "[[fill]]")
                    lines.append(f"- **{label}:** {value}")
                elif slot_type == "dropbox":
                    if slot.get("source") == "supply_characteristics":
                        entries = "\n".join(f"  - {item}" for item in supply_values) or "  - [empty]"
                        lines.append(f"**{label}:**\n{entries}")
                    else:
                        lines.append(f"- **{label}:** (source {slot.get('source')})")
                elif slot_type == "dropbox-table":
                    table_md = _df_to_markdown(df)
                    lines.append(f"**{label}:**\n{table_md}")
                else:
                    lines.append(f"- **{label}:** (unsupported slot type {slot_type})")

        uniqueness = template.get("uniqueness", {})
        salt_fields = uniqueness.get("salt_fields", [])
        hash_payload = {field: field_values.get(field, "") for field in salt_fields}
        hash_value = hashlib.sha256(json.dumps(hash_payload, sort_keys=True).encode()).hexdigest()
        hashes = _load_build_hashes()
        template_hashes = hashes.setdefault(template_id, {})
        if uniqueness.get("deny_duplicate_hash") and hash_value in template_hashes:
            existing = template_hashes[hash_value]
            print(f"{Y}⚠️ Duplicate detected (hash {hash_value}). Previous output: {existing.get('output')}{X}")
            return True
        template_hashes[hash_value] = {"timestamp": datetime.now().isoformat(), "output": str(actual_path)}
        _save_build_hashes(hashes)

        actual_path.parent.mkdir(parents=True, exist_ok=True)
        actual_path.write_text("\n".join(lines), encoding="utf-8")
        if pdf_requested:
            print(f"{C}ℹ️ PDF requested but Markdown created at {actual_path}. Convert via pandoc/reportlab as needed.{X}")
        print(f"{G}✅ Template built → {actual_path}{X}")

        log_build(
            "template_build",
            {
                "template": template_id,
                "output": str(actual_path),
                "hash": hash_value,
                "validation": validation_status or "unknown"
            },
            ok=True,
            tags=["template", "drop-assist"]
        )
        log_training(
            "Template build complete",
            {
                "template": template_id,
                "output": str(actual_path),
                "hash": hash_value,
                "validation": validation_status or "unknown"
            },
            severity="info",
            tags=["template", "drop-assist"]
        )
        return True

    print(f"{Y}⚠️ Unknown template command.{X}")
    return True


_load_doc_allowlist()


def handle_allow_read_command(user_input: str) -> bool:
    lower = user_input.strip().lower()
    if not lower.startswith("/allow-read"):
        return False
    if not DOC_ALLOWLIST:
        _load_doc_allowlist()

    # Handle --list
    if "--list" in lower or user_input.strip() == "/allow-read":
        print(f"{C}📂 Allowed paths:{X}")
        for entry in DOC_ALLOWLIST:
            print(f"- {entry}")
        print(f"\n{C}Usage:{X}")
        print(f"  /allow-read ~/Downloads              # Add path")
        print(f"  /allow-read ~/Documents/myfile.xlsx  # Add specific file's directory")
        print(f"  /allow-read --revoke ~/Downloads     # Remove path")
        print(f"  /allow-read --list                   # Show this list")
        return True

    # Handle --revoke
    if "--revoke" in lower:
        rest = user_input.replace("--revoke", "", 1).strip()
        # Extract path after /allow-read and --revoke
        target = rest.replace("/allow-read", "").strip()
        if not target:
            print(f"{Y}⚠️ Provide a path to revoke.{X}")
            return True
        try:
            normalized = str(Path(target).expanduser().resolve())
        except Exception:
            print(f"{Y}⚠️ Unable to resolve path: {target}{X}")
            return True
        DOC_ALLOWLIST[:] = [
            p for p in DOC_ALLOWLIST if str(Path(p).expanduser().resolve()) != normalized
        ]
        _save_doc_allowlist()
        print(f"{G}✅ Removed {normalized} from allowlist.{X}")
        return True

    # Handle add path - extract everything after /allow-read
    target = user_input.replace("/allow-read", "", 1).strip()
    if not target:
        print(f"{Y}⚠️ Provide a path to allow.{X}")
        print(f"{C}Example: /allow-read ~/Downloads/myfile.xlsx{X}")
        return True
    
    try:
        resolved = Path(target).expanduser().resolve()
    except Exception:
        print(f"{Y}⚠️ Unable to resolve path: {target}{X}")
        return True
    
    if not str(resolved).startswith(str(Path.home().resolve())):
        print(f"{Y}⚠️ Only paths under your home directory can be allowed.{X}")
        return True
    
    # If it's a file, allow its parent directory
    if resolved.is_file():
        entry = str(resolved.parent)
        print(f"{C}ℹ️ File detected - allowing parent directory: {entry}{X}")
    else:
        entry = str(resolved)
    
    if entry not in DOC_ALLOWLIST:
        DOC_ALLOWLIST.append(entry)
        _save_doc_allowlist()
        print(f"{G}✅ Added {entry} to allowlist.{X}")
    else:
        print(f"{C}ℹ️ Path already allowed: {entry}{X}")
    return True


def handle_ecir_shortcuts(user_input: str) -> bool:
    text = user_input.strip()
    lower = text.lower()
    if not lower:
        return False
    pairs = _kv_pairs(text)

    if lower.startswith("/templates") or "list templates" in lower:
        if not cis_available():
            print(f"{Y}⚠️ CIS on {CIS_BASE_URL} is not reachable. Start it with `uvicorn cis.app:app --port 8012`.{X}")
            return True
        templates = _fetch_templates(force=True)
        if not templates:
            print(f"{Y}⚠️ No templates available from CIS.{X}")
            return True
        print(f"{C}📑 Available Certificate Frames:{X}")
        for tpl in templates.values():
            print(f"- {tpl['id']}: {tpl.get('name')} ({tpl.get('certificate_type')})")
            if tpl.get("description"):
                print(f"    {tpl['description']}")
        return True

    if lower.startswith("/set-template"):
        payload = _load_ecir_payload()
        if payload is None:
            print(f"{Y}⚠️ No ECIR in progress. Run 'create ECIR' first.{X}")
            return True
        template_id = pairs.get("template") or _match_template_from_text(lower)
        if not template_id:
            print(f"{Y}⚠️ Provide template id, e.g., /set-template template=distribution_board_roa38{X}")
            return True
        tpl = _get_template_detail(template_id)
        if not tpl:
            print(f"{R}❌ Template '{template_id}' not found via CIS.{X}")
            return True
        payload["template_id"] = template_id
        _save_ecir_payload(payload)
        print(f"{G}✅ Applied template {tpl.get('name', template_id)} to ECIR payload.{X}")
        return True

    if "create ecir" in lower or "create certificate" in lower:
        if not cis_available():
            print(f"{Y}⚠️ CIS on {CIS_BASE_URL} is not reachable. Start it with `uvicorn cis.app:app --port 8012`.{X}")
            return True
        template_id = pairs.get("template") or _match_template_from_text(lower)
        template_meta = _get_template_detail(template_id) if template_id else None
        payload = {
            "cert_id": f"ECIR-AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_name": "New Installation",
            "site_address": "TBD",
            "context": {"supply_type": "TN-C-S", "special_locations": ["704 Construction"]},
            "circuits": [],
            "inspections": [],
        }
        if template_id:
            payload["template_id"] = template_id
        _save_ecir_payload(payload)
        try:
            _cis_post("/validate", payload)
        except requests.RequestException:
            pass
        log_build("ecir_create", {"cert_id": payload["cert_id"]}, ok=True, tags=["cis", "ecir"])
        if template_meta:
            print(f"{G}✅ ECIR skeleton created with template {template_meta.get('name')} ({template_id}).{X}")
        else:
            print(f"{G}✅ ECIR skeleton created at {ECIR_BUFFER}.{X}")
        print(f"{C}Next:{X} `/add-circuit key=value`, `/validate`, `/render`. Use `/templates` to browse frames.")
        return True

    if lower.startswith("/add-circuit"):
        payload = _load_ecir_payload()
        if payload is None:
            print(f"{Y}⚠️ No ECIR in progress. Run 'create ECIR' first.{X}")
            return True
        if not pairs:
            print(f"{Y}⚠️ Provide fields like /add-circuit id=C1 device=\"MCB B\" in=32 design=26 zs=0.62 rcd=true{X}")
            return True
        circuit = {
            "id": pairs.get("id", f"C{len(payload['circuits']) + 1}"),
            "circuit_type": pairs.get("type", "Final circuit"),
            "description": pairs.get("description"),
            "cable_type": pairs.get("cable"),
            "install_method": pairs.get("install"),
            "protective_device": pairs.get("device", "MCB B"),
            "rated_current_a": _float_or_default(pairs.get("in") or pairs.get("rated"), 32),
            "design_current_a": _float_or_default(pairs.get("ib") or pairs.get("design") or pairs.get("load"), 32),
            "zs_measured_ohm": _float_or_default(pairs.get("zs"), None) if "zs" in pairs else None,
            "rcd_present": _bool_from_text(pairs.get("rcd", "false")),
            "notes": pairs.get("note"),
        }
        payload.setdefault("circuits", []).append(circuit)
        _save_ecir_payload(payload)
        log_build("ecir_add_circuit", {"cert_id": payload["cert_id"], "circuit": circuit["id"]}, ok=True, tags=["cis", "ecir"])
        print(f"{G}➕ Circuit {circuit['id']} captured. Run `/validate` when ready.{X}")
        return True

    if lower.startswith("/validate"):
        payload = _load_ecir_payload()
        if payload is None:
            print(f"{Y}⚠️ No ECIR file found at {ECIR_BUFFER}.{X}")
            return True
        try:
            report = _cis_post("/validate", payload)
        except requests.RequestException as err:
            print(f"{R}❌ CIS validate failed: {err}{X}")
            return True
        print(json.dumps(report, indent=2))
        log_build("ecir_validate", {"cert_id": payload["cert_id"], "status": report["status"]}, ok=(report["status"] == "ok"), tags=["cis", "ecir"])
        return True

    if lower.startswith("/render"):
        payload = _load_ecir_payload()
        if payload is None:
            print(f"{Y}⚠️ Nothing to render. Create an ECIR first.{X}")
            return True
        try:
            result = _cis_post("/render", payload, params={"fmt": "markdown"})
        except requests.RequestException as err:
            print(f"{R}❌ CIS render failed: {err}{X}")
            return True
        out_path = CERT_OUTPUT_DIR / f"{payload['cert_id']}.md"
        out_path.write_text(result.get("markdown", ""), encoding="utf-8")
        template_used = (result.get("template") or {}).get("name") if isinstance(result, dict) else None
        template_suffix = f" using template {template_used}" if template_used else ""
        print(f"{G}📝 Rendered ECIR{template_suffix} → {out_path}{X}")
        log_build("ecir_render", {"cert_id": payload["cert_id"], "path": str(out_path)}, ok=True, tags=["cis", "ecir"])
        return True

    return False

def call_openrouter(msgs):
    """Try OpenRouter models with intelligent task-based selection"""
    global current_openrouter, stats
    if not OPENROUTER_MODELS:
        return None, None

    # Get the user's message to analyze task complexity
    user_msg = msgs[-1]["content"] if msgs else ""
    preferred_model = select_best_model_for_task(user_msg)

    # Try preferred model first if specified
    models_to_try = []
    if preferred_model and preferred_model in OPENROUTER_MODELS:
        models_to_try.append(preferred_model)
        # Add other models (excluding the preferred one)
        models_to_try.extend([m for m in OPENROUTER_MODELS if m != preferred_model])
    else:
        models_to_try = OPENROUTER_MODELS.copy()

    # Try each model with appropriate API key
    for model in models_to_try:
        # Update current_openrouter if this is the current model
        if model in OPENROUTER_MODELS:
            current_openrouter = OPENROUTER_MODELS.index(model)

        # Determine which API key to use
        if model in FREE_KEYS and FREE_KEYS[model]:
            api_key = FREE_KEYS[model]
        elif OPENROUTER_KEY:
            api_key = OPENROUTER_KEY
        else:
            continue

        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://spiral-codex.local",
                    "X-Title": "Spiral AI Chat"
                },
                json={"model": model, "messages": msgs, "max_tokens": 2000},
                timeout=30,
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"].get("content", "").strip()
                if content:
                    stats["openrouter"] += 1
                    complexity = analyze_task_complexity(user_msg)
                    print(f"{Y}🧠 {model} ({complexity} complexity){X}")
                    return content, "openrouter"
        except Exception as e:
            print(f"{Y}⚠️ {model} failed: {str(e)[:50]}...{X}")
            pass

    stats["openrouter_fail"] += 1
    return None, None


def call_groq(msgs):
    """Try Groq-hosted models"""
    global current_groq, stats
    if not GROQ_KEY or not GROQ_MODELS:
        return None, None
    for _ in range(len(GROQ_MODELS)):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": GROQ_MODELS[current_groq], "messages": msgs, "max_tokens": 2000},
                timeout=30,
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"].get("content", "").strip()
                if content:
                    stats["groq"] += 1
                    return content, "groq"
        except:
            pass
        current_groq = (current_groq + 1) % len(GROQ_MODELS)
    stats["groq_fail"] += 1
    return None, None


def call_best_online(msgs):
    """Pick the least-busy online provider"""
    providers = []
    # Check for OpenRouter models (both paid and free)
    working_models = []
    for model in OPENROUTER_MODELS:
        if model in FREE_KEYS and FREE_KEYS[model]:
            working_models.append(model)
        elif OPENROUTER_KEY:
            working_models.append(model)

    if working_models:
        providers.append(("openrouter", call_openrouter))
    if GROQ_KEY:
        providers.append(("groq", call_groq))
    if not providers:
        return None, None
    providers.sort(key=lambda item: (stats.get(item[0], 0), stats.get(f"{item[0]}_fail", 0)))
    for name, func in providers:
        response, source = func(msgs)
        if response:
            stats[f"{name}_fail"] = 0
            return response, source
        else:
            stats[f"{name}_fail"] = stats.get(f"{name}_fail", 0) + 1
    return None, None

def call_local(msgs):
    """Fallback to Ollama"""
    global stats
    try:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in msgs])
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        if r.status_code == 200:
            stats["local"] += 1
            return r.json().get("response", ""), "local"
    except:
        pass
    return None, None

def detect_agent(msg):
    """Detect which agent to use"""
    m = msg.lower()
    # Check for BS7671 electrical regulations queries first (highest priority)
    if any(w in m for w in [
        'bs7671', 'iet wiring regulations', '18th edition', 'electrical regulations',
        'earth fault loop impedance', 'zs', 'ze', 'r1+r2', 'earth loop',
        'disconnection time', 'trip time', 'protective device', 'mcb', 'rcd', 'rcbo', 'fuse',
        'circuit design', 'cable sizing', 'protective conductor', 'cpc',
        'eicr', 'electrical installation certificate', 'minor works', 'certification',
        'verification', 'testing', 'inspection', 'electrical safety',
        'circuit charts', 'test results', 'maximum zs', '30mA rcd',
        'insulation resistance', 'polarity', 'prospective fault current', 'pfc'
    ]): return "⚡ BS7671 Expert"

    # Prioritize direct bash commands and system administration
    if msg.startswith('$') or msg.startswith('bash ') or msg.startswith('sh '): return "💾 SysAdmin"
    if any(w in m for w in ['ls', 'list', 'dir', 'find', 'search', 'disk', 'storage', 'memory', 'cpu', 'process', 'system', 'analyze', 'monitor']): return "💾 SysAdmin"
    # Prioritize project building (check for exact phrases first)
    if 'create project' in m or 'scaffold' in m or 'new project' in m or 'create react-app' in m or 'create python-api' in m or 'create nextjs-app' in m or 'create docker-service' in m: return "🏗️ Builder"
    if any(w in m for w in ['deploy', 'docker', 'kubernetes', 'ci/cd', 'pipeline']): return "🚀 DevOps"
    if any(w in m for w in ['code', 'function', 'write', 'implement']): return "💻 Coder"
    if any(w in m for w in ['error', 'bug', 'fix', 'debug']): return "🔧 Debug"
    if any(w in m for w in ['plan', 'design', 'architecture', 'strategy']): return "📋 Architect"
    if any(w in m for w in ['test', 'testing', 'quality', 'validation']): return "🧪 Tester"
    # General project keywords (less specific)
    if any(w in m for w in ['project', 'build', 'setup', 'init']): return "🏗️ Builder"
    return "💬 Chat"

def analyze_task_complexity(msg):
    """Analyze task complexity to guide model selection"""
    m = msg.lower()

    # High complexity indicators
    high_complexity = ['research', 'analyze', 'complex', 'architecture', 'system design', 'multiple steps']
    # Medium complexity indicators
    medium_complexity = ['explain', 'create', 'implement', 'debug', 'write']
    # Simple indicators
    simple_complexity = ['what', 'simple', 'basic', 'quick', 'hello', 'how are you']

    if any(word in m for word in high_complexity):
        return 'high'
    elif any(word in m for word in medium_complexity):
        return 'medium'
    elif any(word in m for word in simple_complexity):
        return 'low'
    return 'medium'  # default

def select_best_model_for_task(msg):
    """Select the best model based on task analysis"""
    complexity = analyze_task_complexity(msg)

    # High complexity: prefer powerful cloud models
    if complexity == 'high':
        # Prefer Nemotron for complex reasoning, then Gemini
        if "nvidia/nemotron-nano-9b-v2:free" in OPENROUTER_MODELS:
            return "nvidia/nemotron-nano-9b-v2:free"
        elif "google/gemini-2.0-flash-exp:free" in OPENROUTER_MODELS:
            return "google/gemini-2.0-flash-exp:free"

    # Medium complexity: any cloud model is fine
    elif complexity == 'medium':
        # Try current model, it will rotate if fails
        return OPENROUTER_MODELS[current_openrouter] if OPENROUTER_MODELS else None

    # Low complexity: can use any model, prioritize speed
    else:
        # Use current model, local fallback is fine
        return OPENROUTER_MODELS[current_openrouter] if OPENROUTER_MODELS else None

def create_file(filename, content):
    """Create file"""
    global stats
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(content)
    stats["files"] += 1
    return f"✅ Created {filename}"

def read_file(filename):
    """Read file"""
    return Path(filename).read_text()[:500]

def run_bash(cmd):
    """Execute command"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout[:500]

# ===== ENHANCED FILE SYSTEM & STORAGE OPERATIONS =====
import os
import shutil
import stat
import pwd
import grp
import psutil
import time
from datetime import datetime

def enhanced_bash(cmd, timeout=30, capture_output=True):
    """Enhanced bash command execution with better error handling and logging"""
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        execution_time = time.time() - start_time

        # Log the command execution
        log_entry = {
            "command": cmd,
            "exit_code": result.returncode,
            "execution_time": f"{execution_time:.2f}s",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if capture_output:
            log_entry["stdout"] = result.stdout[:1000] if result.stdout else ""
            log_entry["stderr"] = result.stderr[:500] if result.stderr else ""

        # Write command log to session
        with open(SESSION.with_suffix('.commands.log'), 'a') as f:
            f.write(f"[{log_entry['timestamp']}] $ {cmd}\\n")
            f.write(f"Exit: {result.returncode} | Time: {log_entry['execution_time']}\\n")
            if result.stdout:
                f.write(f"Output:\\n{result.stdout[:500]}\\n")
            if result.stderr:
                f.write(f"Error:\\n{result.stderr[:300]}\\n")
            f.write("-" * 50 + "\\n")

        stats["commands"] = stats.get("commands", 0) + 1
        return result.stdout if result.stdout else result.stderr

    except subprocess.TimeoutExpired:
        error_msg = f"❌ Command timed out after {timeout} seconds: {cmd}"
        log(f"Command timeout: {cmd}", error_msg, "System")
        return error_msg
    except Exception as e:
        error_msg = f"❌ Command execution failed: {str(e)}"
        log(f"Command error: {cmd}", error_msg, "System")
        return error_msg

def list_directory(path=".", detailed=False, hidden=False):
    """Enhanced directory listing with multiple options"""
    try:
        path = Path(path).expanduser().resolve()
        if not path.exists():
            return f"❌ Path does not exist: {path}"

        if not path.is_dir():
            return f"❌ Path is not a directory: {path}"

        result = f"📁 Directory: {path}\\n"

        if detailed:
            # Detailed listing with permissions, size, owner, etc.
            result += f"{'Permissions':<12} {'Owner':<10} {'Size':<10} {'Modified':<20} {'Name'}\\n"
            result += "-" * 80 + "\\n"

            for item in sorted(path.iterdir()):
                if not hidden and item.name.startswith('.'):
                    continue

                try:
                    stat_info = item.stat()
                    perms = stat.filemode(stat_info.st_mode)
                    size = format_bytes(stat_info.st_size)
                    modified = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                    try:
                        owner = pwd.getpwuid(stat_info.st_uid).pw_name[:8]
                    except:
                        owner = str(stat_info.st_uid)

                    result += f"{perms:<12} {owner:<10} {size:<10} {modified:<20} {item.name + ('/' if item.is_dir() else '')}\\n"
                except Exception as e:
                    result += f"{'Error:':<12} {'':<10} {'':<10} {'':<20} {item.name} - {str(e)}\\n"
        else:
            # Simple listing
            items = []
            for item in sorted(path.iterdir()):
                if not hidden and item.name.startswith('.'):
                    continue
                items.append(f"{'📁' if item.is_dir() else '📄'} {item.name}")
            result += "\\n".join(items)

        return result

    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"

def format_bytes(bytes_size):
    """Format bytes in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}PB"

def get_disk_usage(path="."):
    """Get comprehensive disk usage information"""
    try:
        path = Path(path).expanduser().resolve()
        usage = shutil.disk_usage(path)

        result = f"💾 Disk Usage for {path}:\\n"
        result += f"   Total: {format_bytes(usage.total)}\\n"
        result += f"   Used:  {format_bytes(usage.used)} ({usage.used/usage.total*100:.1f}%)\\n"
        result += f"   Free:  {format_bytes(usage.free)} ({usage.free/usage.total*100:.1f}%)\\n"

        return result

    except Exception as e:
        return f"❌ Error getting disk usage: {str(e)}"

def find_files(pattern="*", path=".", file_type="all", max_results=50):
    """Enhanced file search with multiple criteria"""
    try:
        path = Path(path).expanduser().resolve()
        results = []

        # Determine what to search for
        if file_type == "files":
            items = path.rglob(pattern) if "*" in pattern else path.rglob(f"*{pattern}*")
            items = [item for item in items if item.is_file()]
        elif file_type == "dirs":
            items = path.rglob(pattern) if "*" in pattern else path.rglob(f"*{pattern}*")
            items = [item for item in items if item.is_dir()]
        else:  # all
            items = path.rglob(pattern) if "*" in pattern else path.rglob(f"*{pattern}*")

        for item in sorted(items, key=lambda x: x.stat().st_mtime, reverse=True):
            if len(results) >= max_results:
                break

            try:
                stat_info = item.stat()
                size = format_bytes(stat_info.st_size) if item.is_file() else "<DIR>"
                modified = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                results.append(f"{'📁' if item.is_dir() else '📄'} {item.relative_to(path)} ({size}, {modified})")
            except Exception:
                results.append(f"{'📁' if item.is_dir() else '📄'} {item.relative_to(path)} (Error getting info)")

        if not results:
            return f"🔍 No files found matching '{pattern}' in {path}"

        header = f"🔍 Found {len(results)} items matching '{pattern}' in {path}:\\n"
        return header + "\\n".join(results[:max_results])

    except Exception as e:
        return f"❌ Error searching files: {str(e)}"

def get_system_info():
    """Get comprehensive system information"""
    try:
        result = "🖥️ System Information:\\n\\n"

        # Basic system info
        result += f"💻 Platform: {os.uname().sysname} {os.uname().release}\\n"
        result += f"🔧 Architecture: {os.uname().machine}\\n"
        result += f"🏷️  Hostname: {os.uname().nodename}\\n\\n"

        # CPU info
        result += "🔥 CPU Information:\\n"
        result += f"   Physical cores: {psutil.cpu_count(logical=False)}\\n"
        result += f"   Logical cores: {psutil.cpu_count(logical=True)}\\n"
        result += f"   Current usage: {psutil.cpu_percent(interval=1)}%\\n\\n"

        # Memory info
        memory = psutil.virtual_memory()
        result += "🧠 Memory Information:\\n"
        result += f"   Total: {format_bytes(memory.total)}\\n"
        result += f"   Available: {format_bytes(memory.available)}\\n"
        result += f"   Used: {format_bytes(memory.used)} ({memory.percent}%)\\n\\n"

        # Disk info
        result += "💾 Disk Information:\\n"
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                result += f"   {partition.device} ({partition.mountpoint})\\n"
                result += f"      Total: {format_bytes(usage.total)}\\n"
                result += f"      Free: {format_bytes(usage.free)} ({usage.free/usage.total*100:.1f}% free)\\n\\n"
            except PermissionError:
                result += f"   {partition.device} ({partition.mountpoint}) - Permission denied\\n\\n"

        # Network info
        result += "🌐 Network Interfaces:\\n"
        for interface, addrs in psutil.net_if_addrs().items():
            result += f"   {interface}:\\n"
            for addr in addrs:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    result += f"      {addr.family.name}: {addr.address}\\n"
            result += "\\n"

        return result

    except Exception as e:
        return f"❌ Error getting system info: {str(e)}"

def monitor_processes(search_term=None, limit=20):
    """Monitor system processes with optional filtering"""
    try:
        result = "⚙️  System Processes:\\n\\n"

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                pinfo = proc.info
                if search_term:
                    search_lower = search_term.lower()
                    if (search_lower not in pinfo['name'].lower() and
                        not any(search_lower in str(cmd).lower() for cmd in (pinfo['cmdline'] or []))):
                        continue

                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

        result += f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'MEM%':<8} {'User':<15} {'Command'}\\n"
        result += "-" * 100 + "\\n"

        for proc in processes[:limit]:
            name = proc['name'][:18]
            cpu = f"{proc['cpu_percent'] or 0:.1f}"
            mem = f"{proc['memory_percent'] or 0:.1f}"
            user = (proc['username'] or 'unknown')[:14]
            cmd = ' '.join(proc['cmdline'] or [])[:30]

            result += f"{proc['pid']:<8} {name:<20} {cpu:<8} {mem:<8} {user:<15} {cmd}\\n"

        if len(processes) > limit:
            result += f"\\n... and {len(processes) - limit} more processes"

        return result

    except Exception as e:
        return f"❌ Error monitoring processes: {str(e)}"

def analyze_file(path):
    """Analyze a specific file in detail"""
    try:
        path = Path(path).expanduser().resolve()

        if not path.exists():
            return f"❌ File does not exist: {path}"

        stat_info = path.stat()
        result = f"📄 File Analysis: {path}\\n\\n"

        # Basic info
        result += f"📏 Size: {format_bytes(stat_info.st_size)}\\n"
        result += f"📅 Created: {datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\\n"
        result += f"🔄 Modified: {datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\\n"
        result += f"👁️  Accessed: {datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')}\\n"

        # Permissions
        result += f"🔒 Permissions: {stat.filemode(stat_info.st_mode)}\\n"
        try:
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name
            result += f"👤 Owner: {owner}:{group}\\n"
        except:
            result += f"👤 Owner: {stat_info.st_uid}:{stat_info.st_gid}\\n"

        # File type detection
        if path.is_file():
            # Try to detect file type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type:
                result += f"🏷️  Type: {mime_type}\\n"

            # If it's a text file, show first few lines
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if content.isprintable():
                        result += f"\\n📖 Content preview:\\n{content}\\n"
            except UnicodeDecodeError:
                result += f"\\n🔒 Binary file (content not displayed)\\n"

        return result

    except Exception as e:
        return f"❌ Error analyzing file: {str(e)}"

# ===== PROJECT BUILDER INFRASTRUCTURE =====
PROJECT_TEMPLATES = {
    "react-app": {
        "description": "Modern React application with TypeScript",
        "files": {
            "package.json": """{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "@types/react": "^18.0.28",
    "@types/react-dom": "^18.0.11"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }},
  "browserslist": {{
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }}
}}""",
            "src/App.tsx": '''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>Get started by editing src/App.tsx</p>
      </header>
    </div>
  );
}}

export default App;''',
            "src/App.css": '''.App {{
  text-align: center;
}}

.App-header {{
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}}''',
            "src/index.tsx": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''',
            "public/index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>'''
        },
        "commands": ["npm install", "npm start"]
    },
    "python-api": {
        "description": "FastAPI Python REST API with SQLAlchemy",
        "files": {
            "requirements.txt": '''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6''',
            "main.py": '''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{project_name}")

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name} API"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

@app.post("/items/")
async def create_item(item: Item):
    return {{"message": "Item created", "item": item}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)''',
            "README.md": '''# {project_name}

A FastAPI REST API application.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.
'''
        },
        "commands": ["pip install -r requirements.txt", "uvicorn main:app --reload"]
    },
    "nextjs-app": {
        "description": "Next.js full-stack application with App Router",
        "files": {
            "package.json": """{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18"
  }},
  "devDependencies": {{
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0"
  }}
}}""",
            "app/page.tsx": '''export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">
          Welcome to {project_name}
        </h1>
      </div>
    </main>
  );
}}''',
            "README.md": '''# {project_name}

A Next.js application built with the App Router.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.
'''
        },
        "commands": ["npm install", "npm run dev"]
    },
    "docker-service": {
        "description": "Dockerized microservice with multi-stage build",
        "files": {
            "Dockerfile": '''# Multi-stage build for {project_name}
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY . .

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["npm", "start"]''',
            "docker-compose.yml": '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped''',
            ".dockerignore": '''node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.nyc_output
.vscode
.idea
*.swp
*.swo
*~'''
        },
        "commands": ["docker-compose up --build"]
    }
}

def create_project(project_type, project_name):
    """Create a new project from template"""
    if project_type not in PROJECT_TEMPLATES:
        return f"❌ Unknown project type: {project_type}. Available: {', '.join(PROJECT_TEMPLATES.keys())}"

    template = PROJECT_TEMPLATES[project_type]
    project_path = Path(project_name)

    if project_path.exists():
        return f"❌ Directory {project_name} already exists"

    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    # Create files from template
    for file_path, content in template["files"].items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Replace project name placeholder
        formatted_content = content.format(project_name=project_name)
        full_path.write_text(formatted_content)
        created_files.append(str(full_path))

    result = f"✅ Created {project_type} project '{project_name}'\\n"
    result += f"📁 Location: {project_path.absolute()}\\n"
    result += f"📄 Files created: {len(created_files)}\\n"
    result += "🚀 Next steps:\\n"

    for i, cmd in enumerate(template["commands"], 1):
        result += f"   {i}. cd {project_name} && {cmd}\\n"

    return result

def list_project_templates():
    """List available project templates"""
    result = "🏗️ Available Project Templates:\\n\\n"
    for template_type, template_info in PROJECT_TEMPLATES.items():
        result += f"📦 {template_type}\\n"
        result += f"   {template_info['description']}\\n"
        result += f"   Commands: {' | '.join(template_info['commands'])}\\n\\n"
    return result

def analyze_project_requirements(user_input):
    """Analyze user input to suggest project type"""
    input_lower = user_input.lower()

    # Keywords for different project types
    indicators = {
        "react-app": ["react", "frontend", "web app", "spa", "component"],
        "python-api": ["api", "backend", "fastapi", "flask", "django", "rest"],
        "nextjs-app": ["next.js", "nextjs", "fullstack", "ssr", "full stack"],
        "docker-service": ["docker", "container", "microservice", "deployment"]
    }

    suggestions = []
    for project_type, keywords in indicators.items():
        if any(keyword in input_lower for keyword in keywords):
            suggestions.append(project_type)

    return suggestions

def handle_sysadmin_commands(user_input):
    """Handle system administration and file system commands"""
    m = user_input.lower()

    # Directory listing commands
    if any(cmd in m for cmd in ['ls', 'list', 'dir']):
        # Parse options
        detailed = any(opt in m for opt in ['-l', 'long', 'detailed'])
        hidden = any(opt in m for opt in ['-a', 'all', 'hidden'])

        # Extract path (remove flags)
        path = "."
        # Remove flags from the command to extract the path
        clean_cmd = re.sub(r'\s+-[la]+', '', user_input, flags=re.IGNORECASE)
        clean_cmd = re.sub(r'\s+(long|detailed|all|hidden)', '', clean_cmd, flags=re.IGNORECASE)
        path_match = re.search(r'(?:ls|list|dir)\s+(.+)', clean_cmd.strip(), re.IGNORECASE)
        if path_match:
            path = path_match.group(1).strip()
        elif clean_cmd.strip() in ['ls', 'list', 'dir']:
            path = "."

        return list_directory(path, detailed=detailed, hidden=hidden)

    # File search commands
    elif 'find' in m or 'search' in m:
        # Extract search pattern
        pattern = "*"
        pattern_match = re.search(r'(?:find|search)\s+for\s+["\']?([^"\']+)["\']?', user_input, re.IGNORECASE)
        if pattern_match:
            pattern = pattern_match.group(1)

        # Extract path
        path = "."
        path_match = re.search(r'in\s+["\']?([^"\']+)["\']?$', user_input, re.IGNORECASE)
        if path_match:
            path = path_match.group(1)

        # Determine file type
        file_type = "all"
        if "files" in m:
            file_type = "files"
        elif "dirs" in m or "directories" in m:
            file_type = "dirs"

        return find_files(pattern, path, file_type)

    # Disk usage commands
    elif 'disk' in m or 'storage' in m or 'df' in m:
        path = "."
        path_match = re.search(r'(?:disk|storage|df)\s+(.+)', user_input, re.IGNORECASE)
        if path_match:
            path = path_match.group(1).strip()
        return get_disk_usage(path)

    # System information commands
    elif any(cmd in m for cmd in ['system', 'sysinfo', 'info', 'uname']):
        return get_system_info()

    # Process monitoring commands
    elif 'process' in m or 'ps' in m or 'monitor' in m:
        search_term = None
        search_match = re.search(r'(?:process|ps|monitor)\s+(.+)', user_input, re.IGNORECASE)
        if search_match:
            search_term = search_match.group(1).strip()
        return monitor_processes(search_term)

    # File analysis commands
    elif 'analyze' in m:
        file_match = re.search(r'analyze\s+["\']?([^"\']+)["\']?', user_input, re.IGNORECASE)
        if file_match:
            return analyze_file(file_match.group(1))
        else:
            return "❌ Please specify a file to analyze. Example: 'analyze myfile.txt'"

    # Memory commands
    elif 'memory' in m or 'ram' in m or 'mem' in m:
        memory = psutil.virtual_memory()
        result = "🧠 Memory Information:\\n"
        result += f"   Total: {format_bytes(memory.total)}\\n"
        result += f"   Available: {format_bytes(memory.available)}\\n"
        result += f"   Used: {format_bytes(memory.used)} ({memory.percent}%)\\n"
        return result

    # CPU commands
    elif 'cpu' in m:
        result = "🔥 CPU Information:\\n"
        result += f"   Physical cores: {psutil.cpu_count(logical=False)}\\n"
        result += f"   Logical cores: {psutil.cpu_count(logical=True)}\\n"
        result += f"   Current usage: {psutil.cpu_percent(interval=1)}%\\n"
        return result

    # Direct bash command execution
    elif user_input.startswith('$') or user_input.startswith('bash ') or user_input.startswith('sh '):
        cmd = user_input.lstrip('$bash sh ').strip()
        return enhanced_bash(cmd)

    # Default: try to execute as bash command
    else:
        # Common system commands
        system_commands = ['pwd', 'whoami', 'date', 'uptime', 'hostname', 'which', 'whereis']
        if any(cmd in m for cmd in system_commands):
            return enhanced_bash(user_input)

        return "💾 SysAdmin: Command not recognized. Try: ls, find, disk, system, process, analyze, memory, cpu"

# ===== AUTOMATED EXPERIENCE LOGGING =====
class SpiralExperienceLogger:
    """Integrated experience logger for Spiral sessions"""

    def __init__(self):
        self.obsidian_root = Path.home() / "Documents" / "Obsidian" / "OMAi"
        self.experiences_dir = self.obsidian_root / "Spiral_Experiences"
        self.session_stats = {
            "start_time": datetime.now(),
            "interactions": 0,
            "agents_used": set(),
            "features_used": set(),
            "commands_executed": 0,
            "projects_created": 0,
            "files_created": 0,
            "learning_opportunities": 0,
            "insights_applied": 0,
            "new_skills": 0,
        }
        self.experiences_dir.mkdir(exist_ok=True)

    def log_interaction(self, user_input, agent, response):
        """Log a user interaction"""
        self.session_stats["interactions"] += 1
        self.session_stats["agents_used"].add(agent.split(' ')[1] if ' ' in agent else agent)

        # Track features used
        if any(word in user_input.lower() for word in ['create project', 'scaffold', 'build']):
            self.session_stats["features_used"].add("Project Building")
        if any(word in user_input.lower() for word in ['system', 'disk', 'memory', 'process']):
            self.session_stats["features_used"].add("System Administration")
        if any(word in user_input.lower() for word in ['plan', 'design', 'architecture']):
            self.session_stats["features_used"].add("Project Planning")
        if user_input.startswith('$') or user_input.startswith('bash '):
            self.session_stats["commands_executed"] += 1
            self.session_stats["features_used"].add("Command Execution")

    def log_project_creation(self, project_type, project_name):
        """Log project creation"""
        self.session_stats["projects_created"] += 1
        self.session_stats["features_used"].add("Project Building")

    def log_file_creation(self):
        """Log file creation"""
        self.session_stats["files_created"] += 1

    def create_session_summary(self):
        """Create comprehensive session summary"""
        session_duration = datetime.now() - self.session_stats["start_time"]

        summary = f"""---
title: Spiral Session Summary
date: {datetime.now().strftime("%Y-%m-%d")}
type: session-summary
tags: [session, spiral, {', '.join(self.session_stats['features_used'])}]
---

# Spiral Session Summary

**Session Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Duration:** {str(session_duration).split('.')[0]}
**Session ID:** {SESSION.stem}

## 📊 Session Statistics

- **Total Interactions:** {self.session_stats["interactions"]}
- **Commands Executed:** {self.session_stats["commands_executed"]}
- **Projects Created:** {self.session_stats["projects_created"]}
- **Files Created:** {self.session_stats["files_created"]}

## 🤖 Agents Used

{chr(10).join(f"- **{agent}**" for agent in sorted(self.session_stats["agents_used"]))}

## 🚀 Features Used

{chr(10).join(f"- **{feature}**" for feature in sorted(self.session_stats["features_used"]))}

## 📝 Session Highlights

[Session content would be logged here from main session file]

---

*Generated automatically by Spiral Experience Logger*
"""

        # Save session summary
        summary_file = self.experiences_dir / f"session_{SESSION.stem}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

        return summary_file

# Initialize experience logger
experience_logger = SpiralExperienceLogger()

# ===== CONTINUOUS LEARNING INTEGRATION =====
class ContinuousLearningIntegration:
    """Integrates continuous learning feedback loop into Spiral"""

    def __init__(self):
        self.learning_dir = Path.home() / "Documents" / "Obsidian" / "OMAi" / "Spiral_Learning"
        self.insights_dir = self.learning_dir / "Insights"
        self.moments_dir = self.learning_dir / "Learning_Moments"
        self.learning_log = self.learning_dir / "learning_moments.json"
        self._ensure_directories()
        self.insights_cache = {}
        self.load_recent_insights()

    def _ensure_directories(self):
        for path in (self.learning_dir, self.insights_dir, self.moments_dir):
            path.mkdir(parents=True, exist_ok=True)

    def load_recent_insights(self):
        """Load recent insights for real-time suggestions"""
        if self.insights_dir.exists():
            for insight_file in self.insights_dir.glob("*.md"):
                try:
                    content = insight_file.read_text(encoding='utf-8')
                    # Extract key insights for quick reference
                    insights = self.extract_quick_insights(content)
                    self.insights_cache[insight_file.stem] = insights
                except:
                    continue

    def extract_quick_insights(self, content):
        """Extract key insights for quick reference"""
        insights = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith('###') and 'insight' in line.lower():
                insights.append(line.strip('#').strip())
            elif line.startswith('- **') and 'insight' in line.lower():
                insights.append(line.strip('-').strip('*').strip())
        return insights[:5]  # Top 5 insights

    def suggest_learning_resources(self, user_input, agent):
        """Suggest relevant learning resources based on current interaction"""
        suggestions = []

        # Analyze user input for learning opportunities
        input_lower = user_input.lower()

        # Check for patterns that might benefit from training
        if any(keyword in input_lower for keyword in ['create', 'build', 'implement', 'develop']):
            suggestions.append("🎓 **Project Building Training**: See Training_Modules/ for project scaffolding guides")

        if any(keyword in input_lower for keyword in ['system', 'admin', 'monitor', 'disk']):
            suggestions.append("💾 **System Administration Training**: See Training_Modules/ for system management guides")

        if any(keyword in input_lower for keyword in ['plan', 'design', 'architecture']):
            suggestions.append("📋 **Planning & Design Training**: See Training_Modules/ for architectural patterns")

        if any(keyword in input_lower for keyword in ['error', 'issue', 'problem', 'debug']):
            suggestions.append("🔧 **Troubleshooting Insights**: See Lessons_Learned/ for common solutions")

        # Add relevant insights if available
        relevant_insights = self.find_relevant_insights(input_lower)
        if relevant_insights:
            suggestions.append("💡 **Related Insights**: Based on similar experiences")
            for insight in relevant_insights[:2]:
                suggestions.append(f"   • {insight}")
            self._record_learning_metric("insights_applied")

        return suggestions

    def find_relevant_insights(self, user_input):
        """Find insights relevant to current user input"""
        relevant = []
        input_words = set(user_input.lower().split())

        for insight_file, insights in self.insights_cache.items():
            for insight in insights:
                insight_words = set(insight.lower().split())
                # Simple word overlap matching
                overlap = input_words.intersection(insight_words)
                if len(overlap) >= 2:  # At least 2 matching words
                    relevant.append(insight)
                    break

        return relevant[:3]  # Top 3 relevant insights

    def log_learning_moment(self, user_input, agent, response):
        """Log potential learning moments for future training"""
        learning_indicators = [
            'success', 'achieved', 'completed', 'solved', 'fixed',
            'learned', 'discovered', 'found', 'implemented', 'created'
        ]

        response_lower = response.lower()
        if any(indicator in response_lower for indicator in learning_indicators):
            # This might be a learning moment worth documenting
            learning_moment = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "agent": agent,
                "response_snippet": response[:200],
                "learning_type": self.classify_learning_type(response)
            }

            # Save to learning moments log
            self.save_learning_moment(learning_moment)
            self._record_learning_metric("learning_opportunities")
            self._append_markdown_moment(learning_moment)
            try:
                log_training(
                    f"{learning_moment['learning_type']} insight",
                    {
                        "agent": agent,
                        "snippet": learning_moment["response_snippet"],
                        "input": user_input
                    },
                    severity="info",
                    tags=["spiral", "learning"]
                )
            except Exception:
                pass

    def classify_learning_type(self, response):
        """Classify the type of learning in the response"""
        response_lower = response.lower()

        if any(keyword in response_lower for keyword in ['technical', 'code', 'implement', 'system']):
            return "technical"
        elif any(keyword in response_lower for keyword in ['process', 'workflow', 'method']):
            return "process"
        elif any(keyword in response_lower for keyword in 'design architecture pattern'):
            return "design"
        else:
            return "general"

    def save_learning_moment(self, learning_moment):
        """Save learning moment to log file"""
        moments = []
        if self.learning_log.exists():
            try:
                with open(self.learning_log, 'r', encoding='utf-8') as f:
                    moments = json.load(f)
            except json.JSONDecodeError:
                moments = []
            except FileNotFoundError:
                moments = []

        moments.append(learning_moment)

        # Keep only last 100 learning moments
        if len(moments) > 100:
            moments = moments[-100:]

        with open(self.learning_log, 'w', encoding='utf-8') as f:
            json.dump(moments, f, indent=2)

    def generate_learning_summary(self, session_stats):
        """Generate a learning summary for the session"""
        summary = f"""

## 🎓 Session Learning Summary

**Learning Opportunities Identified:** {session_stats.get('learning_opportunities', 0)}
**Insights Applied:** {session_stats.get('insights_applied', 0)}
**New Skills Practiced:** {session_stats.get('new_skills', 0)}

### 📚 Recommended Next Steps

Based on your session activity, consider these learning resources:

1. **Review Related Experiences**: Check Spiral_Experiences/ for similar scenarios
2. **Complete Training Modules**: Visit Spiral_Learning/Training_Modules/
3. **Study Lessons Learned**: Review Spiral_Learning/Lessons_Learned/
4. **Explore Knowledge Graph**: See Spiral_Learning/Knowledge_Graph/

### 💡 Continuous Learning

Your session contributed to the Spiral learning ecosystem.
Each interaction helps build knowledge for future development.
"""

        return summary

    def _append_markdown_moment(self, learning_moment):
        """Write learning moment to Markdown for Obsidian browsing"""
        date_key = datetime.now().strftime("%Y-%m-%d")
        file_path = self.moments_dir / f"Learning_{date_key}.md"
        header = (
            "---\n"
            f"type: learning-moment\n"
            f"date: {date_key}\n"
            f"agent: \"{learning_moment['agent']}\"\n"
            f"category: {learning_moment['learning_type']}\n"
            "---\n\n"
        )
        block = (
            f"### {learning_moment['timestamp']}\n"
            f"- **Agent:** {learning_moment['agent']}\n"
            f"- **Prompt:** {learning_moment['user_input']}\n"
            f"- **Response:** {learning_moment['response_snippet']}\n"
        )
        if not file_path.exists():
            file_path.write_text(header + block + "\n", encoding="utf-8")
        else:
            with file_path.open("a", encoding="utf-8") as handle:
                handle.write("\n" + block + "\n")

    def _record_learning_metric(self, kind: str):
        """Increment session stats safely."""
        if not hasattr(experience_logger, "session_stats"):
            return
        stat_map = {
            "learning_opportunities": "learning_opportunities",
            "insights_applied": "insights_applied",
            "new_skills": "new_skills",
        }
        key = stat_map.get(kind)
        if key and key in experience_logger.session_stats:
            experience_logger.session_stats[key] = experience_logger.session_stats.get(key, 0) + 1

# ===== RUNTIME SELF-HEALING IMPORT SYSTEM =====
class RuntimeImportValidator:
    """Dynamic import validation and recovery system"""

    def __init__(self):
        self.missing_functions = {}
        self.fallbacks = {}
        self.validation_results = {}

    def validate_import(self, module_name, function_name, fallback_func=None):
        """Validate and recover missing imports"""
        try:
            if module_name == "bs7671_handler":
                from bs7671_handler import handle_bs7671_query
                globals()[function_name] = handle_bs7671_query
                self.validation_results[f"{module_name}.{function_name}"] = "✅ Loaded"
                return True
            # Add more module validations as needed
            return False
        except ImportError as e:
            self.missing_functions[f"{module_name}.{function_name}"] = str(e)
            if fallback_func:
                globals()[function_name] = fallback_func
                self.fallbacks[f"{module_name}.{function_name}"] = "🔄 Fallback Active"
                return True
            self.validation_results[f"{module_name}.{function_name}"] = "❌ Missing"
            return False

    def create_bs7671_fallback(self):
        """Create fallback BS7671 handler"""
        def fallback_bs7671_query(user_input):
            return """⚡ **BS7671 Expert (Fallback Mode)**

I'm currently running in fallback mode due to missing BS7671 handler.

**Basic Guidance:**
- Always consult the latest BS7671 18th Edition regulations
- For specific values, refer to official tables in the regulations
- When in doubt, consult a qualified electrician
- Safety is paramount - never work on live electrical systems

**Common Requirements:**
- 32A Type B MCB max Zs: ~1.5Ω (verify in Table 41.3)
- 30mA RCD trip time: ≤40ms at rated current
- Minimum insulation resistance: 1.0MΩ for 230V circuits
- Maximum voltage drop: 3% lighting, 5% power circuits

Please ensure the complete BS7671 handler is properly installed for detailed guidance."""
        return fallback_bs7671_query

    def get_system_health_report(self):
        """Generate system health report"""
        report = "🔧 **System Health Report**\n\n"
        if self.validation_results:
            report += "**Import Status:**\n"
            for module, status in self.validation_results.items():
                report += f"  {status} {module}\n"
        if self.fallbacks:
            report += "\n**Active Fallbacks:**\n"
            for module, status in self.fallbacks.items():
                report += f"  {status} {module}\n"
        if self.missing_functions:
            report += "\n**Missing Functions:**\n"
            for module, error in self.missing_functions.items():
                report += f"  ❌ {module}: {error}\n"
        return report

# Initialize runtime validator
runtime_validator = RuntimeImportValidator()
runtime_validator.validate_import("bs7671_handler", "handle_bs7671_query",
                                 runtime_validator.create_bs7671_fallback())

# ===== QUANTUM DEBUG INTEGRATION =====
class LightweightQuantumMonitor:
    """Lightweight quantum monitoring for Spiral runtime"""

    def __init__(self):
        self.session_start = datetime.now()
        self.anomaly_count = 0
        self.guidance_events = []

    def detect_anomalies(self, user_input, agent, response):
        """Detect conversation anomalies"""
        anomalies = []

        # Check for error indicators
        if any(word in response.lower() for word in ['error', 'failed', 'unable', 'cannot']):
            anomalies.append("Error detected in response")

        # Check for missing functionality
        if any(word in response.lower() for word in ['not available', 'missing', 'unavailable']):
            anomalies.append("Missing functionality detected")

        # Check for system degradation
        if len(response) < 50 and "fallback" in response.lower():
            anomalies.append("System degradation detected")

        return anomalies

    def log_guidance_event(self, event_type, details):
        """Log guidance events"""
        self.guidance_events.append({
            "timestamp": datetime.now(),
            "type": event_type,
            "details": details
        })

    def get_quantum_summary(self):
        """Get quantum monitoring summary"""
        session_duration = datetime.now() - self.session_start
        return f"""
🌀 **Quantum Monitor Summary**
- Session Duration: {str(session_duration).split('.')[0]}
- Anomalies Detected: {self.anomaly_count}
- Guidance Events: {len(self.guidance_events)}
- System Status: {'⧛ Healthy' if self.anomaly_count < 3 else '⌬ Attention Needed'}
"""

# Initialize quantum monitor
quantum_monitor = LightweightQuantumMonitor()

# ===== CARETAKER INTEGRATION =====
class CaretakerIntegration:
    """Integrated caretaker system for domain expertise"""

    def __init__(self):
        self.caretakers = {}
        self.load_caretakers()

    def load_caretakers(self):
        """Load available caretaker systems"""
        try:
            # Try to load BS7671 caretaker
            caretaker_path = Path(__file__).parent / "caretakers" / "bs7671_caretaker.py"
            if caretaker_path.exists():
                sys.path.append(str(caretaker_path.parent))
                from bs7671_caretaker import BS7671Caretaker
                self.caretakers['bs7671'] = BS7671Caretaker()
                print(f"{G}✅ BS7671 Caretaker loaded{X}")
            else:
                print(f"{Y}⚠️ BS7671 Caretaker not found at {caretaker_path}{X}")
        except Exception as e:
            print(f"{Y}⚠️ Failed to load BS7671 Caretaker: {e}{X}")

    def get_caretaker_context(self, domain, query):
        """Get context from specific caretaker"""
        if domain in self.caretakers:
            try:
                caretaker = self.caretakers[domain]
                triggered, cleaned_query = caretaker.detect_trigger(query)
                payload = caretaker.build_payload(cleaned_query or query)
                caretaker.record_event("context_request", {
                    "query": cleaned_query or query,
                    "triggered": triggered
                })
                return payload
            except Exception as e:
                return {"error": f"Caretaker error: {e}"}
        return None

    def list_active_caretakers(self):
        """List all active caretaker systems"""
        return list(self.caretakers.keys())

# Initialize caretaker integration
caretaker_system = CaretakerIntegration()

# Initialize continuous learning integration
learning_integration = ContinuousLearningIntegration()

# ===== MAIN =====
print(f"{BOLD}{C}╔══════════════════════════════════════════════════╗{X}")
print(f"{BOLD}{C}║  🧠 SPIRAL - Learning Enhanced Assistant        ║{X}")
print(f"{BOLD}{C}║  🏗️ Builder • 💾 SysAdmin • 🌀 AI • 🚀 DevOps  ║{X}")
print(f"{BOLD}{C}╚══════════════════════════════════════════════════╝{X}")
print(f"{C}📚 Experience Logging: Active | 🎓 Learning: Integrated | Session: {SESSION.stem}{X}\n")
# Enhanced provider detection
online_caps = []
available_models = []

# Check OpenRouter models
working_openrouter_models = []
for model in OPENROUTER_MODELS:
    if model in FREE_KEYS and FREE_KEYS[model]:
        working_openrouter_models.append(f"{model.split('/')[-1]} (free)")
    elif OPENROUTER_KEY:
        working_openrouter_models.append(model.split('/')[-1])

if working_openrouter_models:
    online_caps.append(f"OpenRouter ({len(working_openrouter_models)} models)")
    available_models.extend(working_openrouter_models)
elif any(FREE_KEYS.values()):
    online_caps.append("OpenRouter (free models)")
else:
    print(f"{Y}⚠️  Set OPENROUTER_API_KEY to enable paid OpenRouter models{X}")

# Check Groq
if GROQ_KEY:
    online_caps.append("Groq")
    available_models.extend([m.split('-')[0] for m in GROQ_MODELS])
else:
    print(f"{Y}⚠️  Set GROQ_API_KEY to enable Groq models{X}")

# Display status
if online_caps:
    print(f"{G}✅ Online: {', '.join(online_caps)}{X}")
    if available_models:
        print(f"{C}🚀 Available: {', '.join(available_models[:5])}{'...' if len(available_models) > 5 else ''}{X}")
else:
    print(f"{R}❌ Online: No providers configured{X}")
print(f"{G}✅ Local: Ollama | ✅ Obsidian: {SESSION.name}{X}")
print(f"{C}💡 Type '/help' for commands, 'quit' to exit{X}\n")

# Initialize autonomous intelligence
autonomous_ai = get_autonomous_intelligence()
reasoning_engine = create_reasoning_engine(conversation)

while True:
    try:
        user_input = input(f"{C}You: {X}").strip()
        if not user_input or user_input.lower() in ['quit', 'exit', 'q']: break

        # 🧠 AUTONOMOUS INTELLIGENCE LAYER
        # Analyzes intent and auto-discovers files before executing commands
        if not user_input.startswith('/'):
            task_plan = autonomous_ai.understand_request(user_input)
            
            # For high-confidence tasks with file requirements, auto-search
            if task_plan.confidence > 0.7 and not task_plan.files_needed:
                search_terms = ['eicr', 'certificate', 'template']
                for term in search_terms:
                    if term in user_input.lower():
                        print(f"{C}🔍 Autonomously searching for {term} files...{X}")
                        discoveries = autonomous_ai.autonomous_file_search(term)
                        if discoveries:
                            print(f"{G}✅ Found {len(discoveries)} candidate file(s){X}")
                            task_plan.files_needed = [d.path for d in discoveries[:3]]
                        break

        # Help command
        if user_input.lower() in ['/help', 'help', '/commands']:
            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗{X}")
            print(f"{C}║  🌀 SPIRAL COMMANDS - Quick Reference                       ║{X}")
            print(f"{C}╚══════════════════════════════════════════════════════════════╝{X}\n")
            print(f"{G}📂 File Access:{X}")
            print(f"  /allow-read ~/Downloads/myfile.xlsx    # Allow file/directory")
            print(f"  /allow-read --list                     # Show allowed paths")
            print(f"  /allow-read --revoke ~/Downloads       # Remove access")
            print(f"\n{G}📊 Excel/CSV Analysis:{X}")
            print(f"  /excel-summary ~/file.xlsx             # Get workbook overview")
            print(f"  /excel-sheet ~/file.xlsx Sheet1        # Extract sheet data")
            print(f"  /excel-validate ~/file.xlsx            # Check BS7671 compliance")
            print(f"  /reconcile-ecir ~/file.xlsx            # Reconcile circuit data")
            print(f"\n{G}📝 Certificate Templates:{X}")
            print(f"  /template-new id=my_cert title=\"EICR\"  # Create template")
            print(f"  /template-bind id=my_cert source=supply:TN-C-S  # Bind data")
            print(f"  /template-build id=my_cert uniqueness=enforce   # Generate cert")
            print(f"\n{G}📄 Document Scanning:{X}")
            print(f"  ~/Downloads/certificate.pdf            # Scan PDF/Excel file")
            print(f"\n{G}💬 Natural Chat:{X}")
            print(f"  Just type normally - AI will respond!")
            print(f"  \"Create a Python script for...\"")
            print(f"  \"Explain how insulation resistance works\"")
            print(f"\n{C}Type 'quit' or 'exit' to leave{X}\n")
            continue

        if handle_allow_read_command(user_input):
            continue

        if handle_excel_agent_commands(user_input):
            continue

        if handle_template_commands(user_input):
            continue

        if handle_document_scan(user_input):
            continue

        if handle_ecir_shortcuts(user_input):
            continue
        
        # Detect agent
        agent = detect_agent(user_input)
        print(f"{M}{agent}{X}")
        
        # Handle file creation
        if 'create' in user_input.lower() and 'file' in user_input.lower():
            match = re.search(r'(\w+\.\w+)', user_input)
            if match:
                filename = match.group(1)
                # Generate code
                msgs = [{"role": "system", "content": "Generate clean code. Use ```python blocks."},
                        {"role": "user", "content": user_input}]
                response, source = call_best_online(msgs)
                if not response:
                    print(f"{Y}⚠️  Online unavailable, using local model...{X}")
                    response, source = call_local(msgs)
                if not response:
                    print(f"{R}❌ Unable to generate code from any provider.{X}")
                    continue
                
                # Extract code
                code_match = re.search(r'```(?:python)?\n(.*?)```', response, re.DOTALL)
                if code_match:
                    result = create_file(filename, code_match.group(1))
                    print(f"{G}Spiral: {result}{X}\n")
                    log(user_input, result, agent)
                    experience_logger.log_file_creation()
                    continue
        
        # Handle file reading
        if 'read' in user_input.lower():
            match = re.search(r'(\w+\.\w+)', user_input)
            if match:
                result = read_file(match.group(1))
                print(f"{G}Spiral: {result}{X}\n")
                continue

        # Handle system administration commands
        if agent == "💾 SysAdmin":
            result = handle_sysadmin_commands(user_input)
            print(f"{G}Spiral: {result}{X}\n")
            log(user_input, result, agent)
            continue

        # Handle project building commands
        if (any(phrase in user_input.lower() for phrase in ['create project', 'scaffold', 'new project']) or
            any(f"create {template}" in user_input.lower() for template in PROJECT_TEMPLATES.keys())):
            # Extract project type and name
            project_type = None
            project_name = None

            # Try to extract project type
            for ptype in PROJECT_TEMPLATES.keys():
                if ptype in user_input.lower():
                    project_type = ptype
                    break

            # Extract project name (look for patterns like "named X" or "called X")
            name_match = re.search(r'(?:named|called)\s+([^\s]+)', user_input, re.IGNORECASE)
            if name_match:
                project_name = name_match.group(1)
            else:
                # Try to extract from quotes
                quote_match = re.search(r'"([^"]+)"', user_input)
                if quote_match:
                    project_name = quote_match.group(1)

            # If no specific type, analyze and suggest
            if not project_type:
                suggestions = analyze_project_requirements(user_input)
                if suggestions:
                    project_type = suggestions[0]  # Use first suggestion
                    print(f"{Y}🤔 Detected project type: {project_type}{X}")
                else:
                    print(f"{Y}📋 Available project templates:{X}")
                    print(list_project_templates())
                    continue

            # If no name, ask for it
            if not project_name:
                print(f"{Y}📝 Please specify a project name. Example: 'create {project_type} named myapp'{X}")
                continue

            # Create the project
            result = create_project(project_type, project_name)
            print(f"{G}Spiral: {result}{X}")
            log(user_input, result, agent)
            experience_logger.log_project_creation(project_type, project_name)
            continue

        # Handle template listing
        if 'list templates' in user_input.lower() or 'show templates' in user_input.lower() or 'project types' in user_input.lower():
            result = list_project_templates()
            print(f"{G}Spiral: {result}{X}")
            log(user_input, result, agent)
            continue

        # Handle BS7671 Electrical Regulations queries
        if agent == "⚡ BS7671 Expert":
            lower_input = user_input.lower()
            
            # Smart EICR workflow guidance
            if 'eicr' in lower_input or 'certificate' in lower_input:
                if 'template' in lower_input or 'build' in lower_input or 'create' in lower_input:
                    print(f"{G}Spiral (BS7671 Expert):{X}")
                    print(f"\n📋 {C}EICR Certificate Workflow:{X}")
                    print(f"  1️⃣  {Y}Start with a PDF:{X}")
                    print(f"      /allow-read ~/Downloads")
                    print(f"      ~/Downloads/sample_EICR.pdf")
                    print(f"      → Extracts circuit data automatically")
                    print(f"\n  2️⃣  {Y}Or build from template:{X}")
                    print(f"      /template-new id=eicr_2024 title=\"Domestic EICR\"")
                    print(f"      /template-bind id=eicr_2024 source=supply:TN-C-S")
                    print(f"      /template-build id=eicr_2024 uniqueness=enforce")
                    print(f"\n  3️⃣  {Y}View created template:{X}")
                    print(f"      cat templates/my_cert.template.json")
                    print(f"\n{C}💡 Tip: If you have an existing EICR PDF, start there for faster setup!{X}\n")
                    log(user_input, "EICR workflow guidance provided", agent)
                    continue
                elif 'pdf' in lower_input or 'upload' in lower_input or 'scan' in lower_input:
                    print(f"{G}Spiral (BS7671 Expert):{X}")
                    print(f"\n📄 {C}PDF Scanning Workflow:{X}")
                    print(f"  1️⃣  First, allow access to your PDF:")
                    print(f"      /allow-read ~/Downloads/your_EICR.pdf")
                    print(f"\n  2️⃣  Then scan it (just type the path):")
                    print(f"      ~/Downloads/your_EICR.pdf")
                    print(f"\n  3️⃣  Spiral will:")
                    print(f"      • Extract all circuit data")
                    print(f"      • Validate against BS7671 Table 41.3")
                    print(f"      • Flag any compliance issues")
                    print(f"      • Suggest corrections\n")
                    log(user_input, "PDF scanning guidance provided", agent)
                    continue
            
            # Get caretaker context if available
            caretaker_context = caretaker_system.get_caretaker_context('bs7671', user_input)

            # Call BS7671 handler with enhanced context
            response = handle_bs7671_query(user_input)

            # Quantum monitoring for BS7671 queries
            anomalies = quantum_monitor.detect_anomalies(user_input, agent, response)
            if anomalies:
                quantum_monitor.anomaly_count += len(anomalies)
                quantum_monitor.log_guidance_event("BS7671_Anomaly", {
                    "query": user_input,
                    "anomalies": anomalies,
                    "caretaker_available": caretaker_context is not None
                })

            print(f"{G}Spiral (BS7671 Expert): {response}{X}\n")

            # Add caretaker info if context was enhanced
            if caretaker_context and "error" not in caretaker_context:
                print(f"{C}💡 BS7671 Caretaker context enhanced{X}\n")

            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": f"[BS7671 Expert] {response}"})
            log(user_input, response, agent)
            continue

        # Handle intelligent project planning
        if agent == "🏗️ Builder" and 'plan' in user_input.lower():
            # Use AI to help plan the project
            msgs = [{"role": "system", "content": "You are an expert software architect. Help the user plan their project by breaking it down into actionable steps, suggesting technologies, and identifying potential challenges. Be specific and practical."}]
            msgs.extend(conversation[-3:])
            msgs.append({"role": "user", "content": user_input})

            response, source = call_best_online(msgs)
            if not response:
                print(f"{Y}⚠️ Using local model for project planning...{X}")
                response, source = call_local(msgs)

            if response:
                # Add template suggestions based on the plan
                suggestions = analyze_project_requirements(user_input)
                if suggestions:
                    response += f"\n\n💡 **Suggested Templates**: {', '.join(suggestions)}"

                print(f"{G}Spiral (Project Planner): {response}{X}\n")
                conversation.append({"role": "user", "content": user_input})
                conversation.append({"role": "assistant", "content": response})
                log(user_input, response, agent)
                continue

        # 🧠 AUTONOMOUS COMMONSENSE HANDLER - Like GitHub Copilot CLI
        # Handles natural language requests intelligently with contextual reasoning
        lower_user = user_input.lower()
        
        # Use contextual reasoning engine FIRST
        # It will: 1) Check conversation context 2) Search filesystem 3) Fall back to AI
        def ai_fallback(query, context):
            """AI fallback function for reasoning engine"""
            msgs = [
                {"role": "system", "content": f"You are Spiral. Context: Current task is {context.current_task}. Recently mentioned files: {[str(f) for f in context.mentioned_files[-3:]]}. Be helpful and concise."}
            ]
            msgs.extend(conversation[-5:])
            msgs.append({"role": "user", "content": query})
            
            response, source = call_best_online(msgs)
            if not response:
                response, source = call_local(msgs)
            return response or "I couldn't generate a response."
        
        # Apply contextual reasoning for non-command queries
        if not user_input.startswith('/') and not user_input.startswith('$'):
            reasoning_result = reasoning_engine.reason(user_input, ai_fallback)
            
            # If high confidence answer found, use it
            if reasoning_result.confidence > 0.75:
                print(f"{G}Spiral ({reasoning_result.source.title()} Intelligence):{X}")
                print(f"{reasoning_result.answer}\n")
                
                if reasoning_result.files_consulted:
                    print(f"{C}📁 Consulted {len(reasoning_result.files_consulted)} file(s){X}\n")
                
                conversation.append({"role": "user", "content": user_input})
                conversation.append({"role": "assistant", "content": reasoning_result.answer})
                log(user_input, reasoning_result.answer, f"{reasoning_result.source.title()} Intelligence")
                continue
        
        # Auto-locate EICR files when mentioned
        if any(word in lower_user for word in ['eicr', 'certificate', 'find', 'locate', 'look for']):
            if any(action in lower_user for action in ['find', 'locate', 'search', 'look for', 'show me']):
                print(f"{C}🧠 Autonomous file search activated...{X}")
                search_type = 'eicr' if 'eicr' in lower_user else 'certificate'
                discoveries = autonomous_ai.locate_eicr_files()
                
                if discoveries:
                    print(f"\n{G}✅ Ready to process. Pick a file:{X}")
                    for i, disc in enumerate(discoveries[:5], 1):
                        print(f"  {i}. {disc.path}")
                    print(f"\n{C}💡 To scan: just type the path or number{X}\n")
                    log(user_input, f"Found {len(discoveries)} files autonomously", agent)
                    continue
        
        # Auto-execute template operations with file discovery
        if 'populate' in lower_user or 'fill' in lower_user:
            if 'template' in lower_user or 'eicr' in lower_user:
                print(f"{C}🧠 Autonomous template population...{X}")
                # Find template files
                template_discoveries = autonomous_ai.autonomous_file_search('template')
                # Find source data files
                data_discoveries = autonomous_ai.autonomous_file_search('eicr')
                
                if template_discoveries and data_discoveries:
                    template_file = template_discoveries[0].path
                    data_file = data_discoveries[0].path
                    print(f"{G}✅ Autonomous discovery:{X}")
                    print(f"  Template: {template_file}")
                    print(f"  Data source: {data_file}")
                    print(f"\n{C}🔄 Auto-executing: /template-bind...{X}\n")
                    # Could auto-execute here, for now we guide
                    print(f"{Y}💡 Run: /template-bind id=my_cert source=file:{data_file}{X}\n")
                    log(user_input, "Autonomous file pairing complete", agent)
                    continue

        # Regular chat
        msgs = [{"role": "system", "content": "You are Spiral. Be helpful and concise."}]
        msgs.extend(conversation[-5:])
        msgs.append({"role": "user", "content": user_input})
        
        response, source = call_best_online(msgs)
        if not response:
            print(f"{Y}⚠️ Using local Ollama...{X}")
            response, source = call_local(msgs)
        if not response:
            print(f"{R}❌ No response generated from online or local providers.{X}\n")
            continue
        
        if response:
            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": response})
            print(f"{G}Spiral: {response}{X}\n")
            log(user_input, response, agent)

            # Quantum monitoring for general chat
            anomalies = quantum_monitor.detect_anomalies(user_input, agent, response)
            if anomalies:
                quantum_monitor.anomaly_count += len(anomalies)
                quantum_monitor.log_guidance_event("Chat_Anomaly", {
                    "query": user_input,
                    "anomalies": anomalies,
                    "agent": agent
                })

            # Log interaction to experience logger
            experience_logger.log_interaction(user_input, agent, response)

            # Log learning moments and provide suggestions
            learning_integration.log_learning_moment(user_input, agent, response)
            learning_suggestions = learning_integration.suggest_learning_resources(user_input, agent)
            if learning_suggestions:
                print(f"{C}💡 Learning Resources:{X}")
                for suggestion in learning_suggestions:
                    print(f"   {suggestion}")
                print()

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"{R}Error: {e}{X}\n")

# Session summary and experience logging
online_total = stats['openrouter'] + stats['groq']
SESSION.write_text(
    SESSION.read_text()
    + f"\n---\n**Stats:** Online: {online_total} (OpenRouter {stats['openrouter']}, Groq {stats['groq']}) | "
      f"Local: {stats['local']} | Files: {stats['files']}\n"
)
print(f"\n{Y}Session saved: {SESSION}{X}")

# Create experience summary and system health report
try:
    summary_file = experience_logger.create_session_summary()
    print(f"{G}Experience summary logged: {summary_file.name}{X}")

    # Add learning summary
    learning_summary = learning_integration.generate_learning_summary(experience_logger.session_stats)
    print(f"{C}{learning_summary}{X}")

    # Add quantum monitoring summary
    quantum_summary = quantum_monitor.get_quantum_summary()
    print(f"{M}{quantum_summary}{X}")

    # Add system health report
    health_report = runtime_validator.get_system_health_report()
    if health_report.strip():
        print(f"{Y}{health_report}{X}")

    # Add caretaker status
    active_caretakers = caretaker_system.list_active_caretakers()
    if active_caretakers:
        print(f"{G}🤝 Active Caretakers: {', '.join(active_caretakers)}{X}")
    else:
        print(f"{Y}⚠️ No caretakers active{X}")

except Exception as e:
    print(f"{Y}System monitoring error: {e}{X}")
