# Spiral Codex - Ethical Content Ingestion System

A comprehensive ethical content ingestion system for the Spiral Codex repository that discovers, fetches, scores, and indexes relevant content from multiple public sources while maintaining full provenance and ethical compliance.

## 🌟 Features

### Core Capabilities
- **Multi-Source Fetching**: Reddit, arXiv, Internet Archive, YouTube, PDF documents
- **Bullshit Scoring**: Advanced credibility assessment with 0-1 scale scoring
- **Provenance Tracking**: Complete logging of every fetch attempt and decision
- **Ethical Compliance**: Robots.txt respect, rate limiting, license detection
- **Credibility-Based Filtering**: Content filtering based on quality assessments

### Scoring System
The system uses a comprehensive bullshit scoring formula:
```
bullshit_score = (source_weight × 0.3) + (quality_weight × 0.25) +
                 (consensus_weight × 0.25) + (citation_weight × 0.2)
```

**Lower scores indicate higher credibility (0 = most credible, 1 = bullshit)**

### Credibility Tiers
- **HIGHLY_CREDIBLE** (0.0-0.2): Academic papers, reputable sources
- **CREDIBLE** (0.2-0.4): Technical documentation, established platforms
- **MODERATE** (0.4-0.6): Mixed quality, requires verification
- **QUESTIONABLE** (0.6-0.8): Social content, unverified sources
- **HIGH_BULLSHIT_RISK** (0.8-1.0): Clickbait, low-quality content

## 🚀 Quick Start

### Installation
```bash
# Install basic dependencies
pip install -r requirements_ingest.txt

# For PDF support (optional)
pip install pdfplumber PyPDF2

# For Reddit support (optional)
pip install asyncpraw

# For YouTube support (optional)
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Basic Usage
```bash
# Simple search
python ingest_driver.py --query "electrical principles IET" --max-items 10

# Use specific sources
python ingest_driver.py --query "machine learning" --sources arxiv,reddit

# Use configuration file
python ingest_driver.py --config ingest_config.json --query "AI ethics"
```

### Programmatic Usage
```python
import asyncio
from ingest_driver import IngestDriver

async def main():
    driver = IngestDriver("ingest_config.json")

    result = await driver.ingest(
        query="renewable energy",
        sources="arxiv,archive",
        max_items=20
    )

    driver.print_summary(result)
    return result

asyncio.run(main())
```

## 📁 Project Structure

```
spiral_codex_unified/
├── bullshit.py                    # Bullshit scoring system
├── ingest_driver.py               # Main orchestrator
├── ingest_config.json             # Configuration file
├── example_usage.py               # Usage examples
├── requirements_ingest.txt        # Dependencies
├── README_INGEST.md              # This file
├── fetchers/                      # Source fetchers
│   ├── __init__.py
│   ├── base_fetcher.py           # Base class with ethical compliance
│   ├── reddit_fetcher.py         # Reddit content
│   ├── arxiv_fetcher.py          # arXiv papers
│   ├── archive_fetcher.py        # Internet Archive
│   ├── youtube_fetcher.py        # YouTube transcripts
│   └── pdf_fetcher.py            # PDF documents
├── logs/                          # Logging directory
│   └── ingest_trials.jsonl       # Trial logs
├── data/                          # Data directory
│   └── vault_index.json          # Enhanced vault index
└── utils/                         # Utility modules
    ├── trial_logger.py           # Trial logging system
    ├── omai_bridge.py            # OMAi integration
    └── telemetry.py              # WEAN telemetry
```

## ⚙️ Configuration

### Basic Configuration
```json
{
  "max_items_per_source": 20,
  "max_total_items": 50,
  "bullshit_threshold": 0.7,
  "enabled_sources": ["reddit", "arxiv", "archive"],
  "integration": {
    "omai_enabled": true,
    "reflection_cycle_enabled": true,
    "wean_telemetry": true
  }
}
```

### Advanced Configuration
- **Bullshit Scoring**: Customizable weights and thresholds
- **Rate Limiting**: Configurable delays and retry policies
- **Content Filtering**: Length and quality requirements
- **License Filtering**: Allowed/open content licenses
- **Source Selection**: Enable/disable specific sources

## 🔒 Ethical Compliance

### Robots.txt Compliance
- All fetchers respect robots.txt directives
- Configurable user-agent identification
- Automatic crawl-delay enforcement

### Rate Limiting
- Default 1-second delay between requests
- Per-domain rate limiting
- Exponential backoff for failures

### License Detection
- Automatic license detection from content
- Filtering based on allowed licenses
- Support for Creative Commons, academic, and public domain content

### Content Filtering
- Private/draft content detection
- NSFW content filtering (Reddit)
- Duplicate content detection
- Minimum quality thresholds

## 📊 Integration Points

### OMAi Vault Integration
- Automatic vault index updates with credibility scores
- Context enrichment for reflection cycles
- Ledger updates for learning loops

### Reflection Cycle Integration
- Automatic reflection enrichment with ingest results
- Learning opportunity extraction
- Failure pattern analysis

### WEAN Telemetry
- Performance metrics collection
- Provider performance tracking
- System health monitoring

## 📈 Examples

### Academic Research
```bash
python ingest_driver.py \
  --query "quantum computing applications" \
  --sources arxiv \
  --max-items 10 \
  --config academic_config.json
```

### Technical Documentation
```bash
python ingest_driver.py \
  --query "kubernetes best practices" \
  --sources reddit,archive \
  --bullshit-threshold 0.5
```

### Social Discussions
```bash
python ingest_driver.py \
  --query "python programming tips" \
  --sources reddit \
  --max-items 20 \
  --skip-nsfw
```

## 📝 Logging and Monitoring

### Trial Logs
Every fetch attempt is logged to `logs/ingest_trials.jsonl`:
- URL and timestamp
- Success/failure status
- Response times
- Error details
- Bullshit scores
- License information

### Performance Metrics
- Response time tracking
- Success rate monitoring
- Source performance analysis
- Credibility distribution statistics

### WEAN Telemetry
- Automatic performance logging
- Provider monitoring
- System health tracking
- Latency measurements

## 🔧 Troubleshooting

### Common Issues

#### No Content Found
- Check if sources are enabled in configuration
- Verify API keys are configured (YouTube, Reddit)
- Check network connectivity
- Review logs for specific error messages

#### High Bullshit Scores
- Adjust `bullshit_threshold` in configuration
- Enable more credible sources (arxiv, archive)
- Check source-specific settings

#### Rate Limiting Issues
- Increase `rate_limit_delay` in configuration
- Reduce `max_items_per_source`
- Check API quotas and limits

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from ingest_driver import IngestDriver
# ... your code here
"
```

## 🤝 Contributing

### Adding New Sources
1. Inherit from `BaseFetcher` in `fetchers/base_fetcher.py`
2. Implement required methods (`_fetch_impl`, `_process_content`)
3. Add to fetchers in `ingest_driver.py`
4. Add configuration options
5. Update documentation

### Testing
```bash
# Run basic tests
python example_usage.py

# Run with custom configuration
python ingest_driver.py --query "test" --max-items 1 --sources reddit
```

## 📄 License

This ethical content ingestion system is designed to respect:
- Creative Commons licenses
- Academic open access policies
- Platform terms of service
- Copyright and intellectual property rights

## 🔮 Future Enhancements

- Additional source integrations (news sites, blogs)
- Advanced content analysis and clustering
- Machine learning-based bullshit detection
- Real-time content monitoring
- Multilingual content support
- Automated content summarization

---

**Built with ethical principles and responsible AI practices at the core.**