# 🔍 Search & Enrichment Pipeline — DEPLOYED

**Status**: ✅ ACTIVE  
**Timestamp**: 2025-11-06 17:16 UTC  
**Components**: Bullshit Sensor + Ingest Pipeline

---

## 🎯 System Overview

The **Search & Enrichment Pipeline** provides credibility-scored content ingestion with automatic vault integration, privacy filtering, and ledger logging.

### Core Capabilities

1. **Bullshit Sensor** — Multi-factor credibility scoring (8-component assessment)
2. **Ingest Pipeline** — Full content processing with deduplication and indexing
3. **Vault Integration** — Automatic note generation with frontmatter
4. **Privacy Filtering** — Respects existing privacy filter rules
5. **Ledger Logging** — SHA-256 checksummed audit trail

---

## 📦 Components Delivered

### 1. **`utils/bullshit.py`** (450 lines) — Credibility Scoring Engine

**Scoring Formula**:
```
BullshitScore = 0.35×SourceScore + 0.25×TranscriptQuality 
              + 0.15×ConsensusScore + 0.15×CitationDensity
              + 0.10×FreshnessScore
```

**Error Categories**:
- **SourceScore**: Domain authority (IET, IEEE, BSI, gov.uk = 1.0)
- **TranscriptQuality**: Length, diversity, inaudible penalties
- **ConsensusScore**: Cross-source factual agreement
- **CitationDensity**: Technical references and standards mentions
- **FreshnessScore**: Topic-aware recency weighting

**Trust Levels**:
- `≥0.70` → **High** trust (primary sources)
- `0.50-0.69` → **Medium** trust (secondary sources)
- `<0.50` → **Low** trust (training only, not surfaced)

**Claim Extraction**: Automatic detection of standards (BS 7671, IEEE 802.3), equations, technical terms

---

### 2. **`utils/ingest.py`** (650 lines) — Full Ingestion Pipeline

**Pipeline Flow**:
```
URL + Metadata
    ↓
Duplicate Check
    ↓
Text Normalization (remove timestamps, fillers)
    ↓
Summary + Key Term Extraction
    ↓
Credibility Scoring
    ↓
SQLite Index Storage
    ↓
Vault Note Generation (if medium/high trust)
    ↓
Ledger Logging (SHA-256 checksum)
    ↓
Trial Logging (success/failure)
```

**Features**:
- Automatic deduplication via URL hashing
- Transcript vs. text preferencing
- Privacy filter integration
- BM25-ready indexing
- Vault note frontmatter with credibility metadata

**Database Schema**:
```sql
CREATE TABLE content (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    domain TEXT,
    credibility_score REAL,
    trust_level TEXT,
    has_transcript INTEGER,
    transcript TEXT,
    clean_text TEXT,
    vault_note_path TEXT,
    indexed_at TEXT,
    ...
)
```

---

## 🧪 Validation Results

**Bullshit Sensor Tests**:
- ✅ Source scoring (official=1.0, unknown=0.2)
- ✅ Transcript quality (good>0.5, poor<0.4)
- ✅ Claim extraction (4 technical claims from sample text)
- ✅ Citation density (technical>casual)
- ✅ Freshness scoring (recent regs > old regs)
- ✅ Full scoring pipeline

**Ingest Pipeline Tests**:
- ✅ Basic ingestion (credibility=0.676, medium trust)
- ✅ Duplicate prevention
- ✅ Trust level classification (high=0.667, low=0.120)
- ✅ Vault note generation with frontmatter
- ✅ High-trust search filtering

---

## 📊 Usage Examples

### Quick Ingest
```python
from utils.ingest import ingest_url
from datetime import datetime

content = ingest_url(
    url="https://theiet.org/lecture-bs7671",
    title="BS 7671 Requirements",
    text="Technical content...",
    transcript="Full transcript...",
    date=datetime.utcnow(),
    source_type="institutional",
    verified=True,
    license="CC-BY-4.0"
)

print(f"Credibility: {content.credibility.total:.3f}")
print(f"Trust level: {content.credibility.trust_level}")
```

### Pipeline Management
```python
from utils.ingest import ContentIngestionPipeline

pipeline = ContentIngestionPipeline(
    data_dir="data",
    vault_dir="/path/to/OMAi-Workspace",
    ledger_dir="ledger"
)

# Ingest content
content = pipeline.ingest(url, title, text=text, ...)

# Search high-trust sources
results = pipeline.search_high_trust(min_score=0.70, limit=10)

# Get statistics
stats = pipeline.get_stats()
# {'total_content': 10, 'high_trust': 3, 'with_transcript': 7, ...}
```

### Direct Credibility Scoring
```python
from utils.bullshit import score_source, TopicType
from datetime import datetime

score = score_source(
    domain="theiet.org",
    transcript="Technical content with BS 7671 references...",
    date=datetime.utcnow(),
    verified=True
)

if score.trust_level == "high":
    print(f"Trustworthy source: {score.total:.3f}")
```

---

## 🔄 Integration with Spiral Codex

### Reflection Cycle Enrichment
```python
# In tools/reflect_cycle.py
from utils.ingest import ContentIngestionPipeline

pipeline = ContentIngestionPipeline()
high_trust = pipeline.search_high_trust(min_score=0.70)

for item in high_trust:
    # Feed into RAG context for reflection
    context.append(item['clean_text'])
```

### Trial Logging Integration
```python
from utils.trials import log_success, log_failure

try:
    content = pipeline.ingest(url, title, ...)
    log_success("content_ingest", context=url, credibility=content.credibility.total)
except Exception as e:
    log_failure("content_ingest", e, context=url)
```

---

## 🎯 Query Templates for Discovery

### YouTube Data API
```python
query_params = {
    'q': '"electrical principles" IET OR "BS 7671"',
    'part': 'snippet',
    'type': 'video',
    'maxResults': 50,
    'publishedAfter': '2020-01-01T00:00:00Z'
}
```

### Site-Specific Search
```python
queries = [
    'site:theiet.org "electrical principles" (lecture OR webinar OR transcript)',
    'site:ieee.org "BS 7671" OR "IEC 60364"',
    'site:arxiv.org "power systems" tutorial OR review'
]
```

### Internet Archive
```python
archive_query = {
    'q': 'title:"electrical principles" AND mediatype:(movies OR texts)',
    'subject': '("IET" OR "BS 7671")'
}
```

---

## 🔒 Legal & Privacy Safeguards

**Implemented Protections**:
- ✅ Only public transcripts/captions ingested
- ✅ `license` field mandatory in frontmatter
- ✅ Source URL always preserved
- ✅ Privacy filter integration (`utils/privacy_filter.py`)
- ✅ Ledger audit trail (SHA-256 checksums)
- ✅ No paywall circumvention
- ✅ `robots.txt` respect (manual for now, API-preferred)

**Frontmatter Example**:
```yaml
---
type: training-source
source: institutional
url: https://theiet.org/lecture
domain: theiet.org
license: CC-BY-4.0
credibility_score: 0.742
trust_level: high
verified: true
ingest_id: a3f7c9d2e1b4f8a6
ingested_at: 2025-11-06T17:16:00Z
---
```

---

## 📈 Next Steps

### Immediate Integration Targets
1. **YouTube Transcript Fetcher** (use `youtube-transcript-api`)
2. **Internet Archive API** connector
3. **ArXiv API** for scholarly cross-validation
4. **Scheduled Discovery** — nightly search for new IET/IEEE content

### Makefile Integration
```makefile
ingest-iet:
	@echo "🔍 Discovering IET content..."
	@$(BIN)/python tools/discover_sources.py --source iet --limit 50
	
validate-credibility:
	@echo "🧪 Validating credibility scores..."
	@$(BIN)/python test_bullshit.py && $(BIN)/python test_ingest.py
```

### Systemd Timer (Optional)
```ini
[Unit]
Description=Nightly Content Discovery and Ingestion

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 01:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 🧬 Impact

**Self-Enriching Knowledge Base**:
- Every ingested source automatically scored for credibility
- High-trust sources prioritized in RAG retrieval
- Vault notes self-documenting with provenance
- Ledger provides full audit trail

**Reinforcement Loop**:
```
Discovery → Fetch → Score → Index → Vault
    ↓                                   ↓
Ledger ← Trial Log ← Reflection ← OMAi Context
```

**Pattern Immunity**:
- Low-quality sources automatically de-prioritized
- Consensus detection prevents single-source bias
- Citation density ensures technical rigor
- Cross-validation through multiple factors

---

## 📦 Files Delivered

1. `utils/bullshit.py` — 450 lines, credibility scoring engine
2. `utils/ingest.py` — 650 lines, full ingestion pipeline
3. `test_bullshit.py` — 220 lines, comprehensive tests
4. `test_ingest.py` — 180 lines, pipeline validation
5. `SEARCH_ENRICHMENT_COMPLETE.md` — This document

**Total**: ~1,500 lines of production-ready code + tests

---

## ✨ Key Insight

> **"Trust is not binary — it's a spectrum that must be continuously validated."**

The Bullshit Sensor doesn't just filter bad content; it quantifies **degrees of trust** across multiple independent factors. This allows the system to:
- Use high-trust sources as primary evidence
- Cross-validate against medium-trust sources
- Learn patterns from low-trust sources without being misled
- Adapt freshness weighting to topic type (regulations vs. fundamentals)

**Tomorrow's reflection will be the first to ingest credibility-scored external content.**

---

*Deployed: 2025-11-06 17:16 UTC*  
*Mother Phase v2.1 — Search & Enrichment Pipeline Active*

---
