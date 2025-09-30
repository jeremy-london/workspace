# Knowledge Base Tool - Technical Interview

## Overview
This is an interactive CLI tool for managing semantic knowledge using ChromaDB vector databases. It enables RAG (Retrieval-Augmented Generation) style lookups on business data, allowing you to find similar accounts, identify patterns, and query customer information semantically.

## Setup (Already Done in Codespace!)
The environment is pre-configured with:
- Python 3.12
- ChromaDB
- Sentence Transformers (BGE and E5 models)

## Quick Start

### 1. Load sample data
```bash
python ingest_knowledge_interactive.py
```

Then in the interactive prompt:
```
> r sample_data.json
✅ Imported 20 records to all 3 collections for 'semantic_knowledge'.
```

### 2. Try searching
```
> ? threat detection
[1] 📄 Account: Federal Defense Logistics Agency. Industry: Government/Federal...

> ? keeper security products
[1] 📄 Account: MegaBank Financial Group. Industry: Banking & Finance...

> ? government fedramp
[1] 📄 Account: Federal Defense Logistics Agency...
[2] 📄 Account: Department of Veterans Affairs - Regional...
```

### 3. List all entries
```
> ?

===  📚 Stored Entries ===

[1] 📝 Account: Acme Financial Services. Industry: Banking & Finance...
📄 source: salesforce_account_export
📄 timestamp: 2025-09-30 08:00:00
📄 account_id: SF-001-ACME-FIN

[2] 📝 Account: TechCorp Industries. Industry: Technology & SaaS...
📄 source: salesforce_account_export
📄 timestamp: 2025-09-30 08:00:00
📄 account_id: SF-002-TECH-IND
...
```

### 4. View with details
```
> ?? high churn risk

===  🔍 Top Matches for 'high churn risk': ===

[1] 📄 Account: RetailMax Corporation. Industry: Retail...
   source: salesforce_account_export
   timestamp: 2025-09-30 08:00:00
   account_id: SF-008-RETAIL-MAX
   industry: retail
   health_score: 41
   churn_risk: critical
```

## Interview Tasks (1hr - 2hr)

>Add more time on questions - get more breadth of modeling - questions about why you pick a model, what about quantization, limitations for each/pros for each - mixed precision, scale and new model adjustments

>CLI or webapp, which is easier and how can you find a solution that is flexiable for both

>Get a guage of GenAI skills vs Data Science skills - ask questions to guide both paths and see where he is more comfortable in

>Is sentance transformers the only way to do this? Are there other systems/soluitions that can be leveraged. Should we explore more GenAI/SQL generation, EDA type of processing

> Find a way to influence LLM skills - can we make this be LLM driven, LLM generated data, Agentic system?

>Business Alignment - What does keeper need ... 

### Phase 1: Understanding (20 min)
**Questions to consider:**
- Explain what the code does at a high level
- How do embedding models work in this context?
- What are BGE vs E5 models and why use both?
- Why does the tool maintain 3 parallel collections? / or do a single one
- What is the `format_for_embedding` function doing?

### Phase 2: Analysis (30 min)
**Improvement opportunities:**
- What improvements would you make to this codebase?
- Why those specific improvements?
- What's the priority order?
- What are the current pain points or risks?

### Phase 3: Implementation (45 min)
**Coding challenge:**
- Implement 1-2 improvements from your analysis
- Test with sample data
- Demonstrate the changes work correctly
- Explain your implementation choices

## Sample Data Overview

The `sample_data.json` contains 20 Salesforce account records including:

### Healthy Accounts (Low Churn Risk)
- **Acme Financial Services** - 85/100 health, 92% adoption, strong SIEM integration
- **Federal Defense Logistics Agency** - 92/100 health, FedRAMP certified, 95% adoption
- **MegaBank Financial Group** - 91/100 health, enterprise deployment with full product suite

### At-Risk Accounts (High/Critical Churn Risk)
- **TechCorp Industries** - 45/100 health, only 38% adoption, 18 support tickets
- **RetailMax Corporation** - 41/100 health, 33% adoption, executive sponsor left
- **Digital Media Studios** - 38/100 health, 29% adoption, renewal in 2 weeks, no QBR

### Key Data Points Per Account
- Contract value ($18K - $680K ARR)
- Deployment dates and health scores
- Product adoption (KeeperPAM, Secrets Manager, RBI, EPM)
- Usage metrics (gateway connections, session recordings, ARAM events)
- Support ticket volume and resolution times
- NPS scores and risk factors
- SIEM integrations (Splunk, QRadar, Sentinel, etc.)
- Compliance requirements (FedRAMP, HIPAA, NIST, etc.)

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `?` | List all entries | `?` |
| `? query` | Search semantically | `? high adoption banking` |
| `?? query` | Search with full metadata | `?? critical churn risk` |
| `?! query` | Table names only (metadata collections) | `?! customer` |
| `-N` | Delete entry N | `-5` |
| `-all` | Clear entire collection | `-all` |
| `w file.json` | Export collection | `w backup.json` |
| `r file.json` | Import collection | `r sample_data.json` |
| `exit` or `quit` | Exit program | `exit` |

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--load-file FILE` | Load data from a specific JSON file on startup (default: `data/sample_data.json`) | `--load-file data/churn_prediction.json` |
| `--dont-clear` | Do **not** clear ChromaDB collections on startup (by default, collections are cleared) | `--dont-clear` |


## Sample Query Examples

### Business Intelligence Queries
```bash
# Find accounts with churn risk
> ? critical churn risk accounts
> ? low adoption high support tickets

# Identify expansion opportunities
> ? high health score banking financial
> ? government fedramp ready for keeper ai

# Product adoption patterns
> ? secrets manager splunk integration
> ? remote browser isolation enterprise

# Support and health analysis
> ? poor nps score retail
> ? high support volume no siem
```

### Customer Segmentation
```bash
# By industry
> ? healthcare hipaa compliance
> ? federal government defense
> ? technology saas startups

# By product suite
> ? full product suite enterprise
> ? keeperpam only basic

# By size/scale
> ? large enterprise 10000 employees
> ? small business under 500
```

### Risk & Retention Analysis
```bash
# Early warning signals
> ? low adoption no qbr
> ? declining gateway connections
> ? executive sponsor left

# Success patterns
> ? high nps strong adoption
> ? siem integration automated rotation
> ? fedramp compliant government
```

## Expected Output Examples

### Successful Search
```
> ?federal government high security

===  🔍 Top Matches for 'federal government high security': ===

[1] 📄 Account: Department of Veterans Affairs - Regional. Industry: Government/Federal. Employees: 22000. Contract Value: $680K ARR. Products: KeeperPAM GovCloud, Secrets Manager, EPM, RBI. Health Score: 94/100...

[2] 📄 Account: Federal Defense Logistics Agency. Industry: Government/Federal. Employees: 15000. Contract Value: $450K ARR. Products: KeeperPAM GovCloud, Secrets Manager, EPM. Health Score: 92/100...
```

### Empty Results
```
> ? blockchain cryptocurrency

🔍 No matching results found.
```

### Export Operation
```
> w my_backup.json
📤 Exported collection to 'my_backup.json' (20 records).
```

### Delete Operation
```
> -5
🗑️ Deleted fact #5 from all model variants of 'semantic_knowledge'
```

## Expected Improvement Areas

Consider exploring these areas:

### Code Quality
- Error handling for malformed JSON data
- Input validation and sanitization
- Edge case handling (empty queries, special characters)
- Type hints and documentation

### Performance
- Query result caching
- Batch operations optimization
- Collection switching efficiency
- Memory usage for large datasets

### User Experience
- Search relevance scoring display
- Colored output improvements
- Better error messages
- Query suggestions/autocomplete
- Progress indicators for long operations

### Features
- Filtering by metadata (industry, health_score, etc.)
- Advanced search operators (AND, OR, NOT)
- Fuzzy matching threshold configuration
- Result ranking explanations
- Export/import format options (CSV, JSONL)

### Testing
- Unit tests for core functions
- Integration tests for ChromaDB operations
- Sample data validation tests
- Performance benchmarks

### Architecture
- Separation of concerns (CLI, DB operations, formatting)
- Configuration management
- Plugin system for different embedding models
- API wrapper for programmatic access

## Common Issues & Debugging

### Models not downloading
```bash
# Check disk space
df -h

# Manually trigger download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-base-en-v1.5')"
```

### ChromaDB permissions
```bash
# Check permissions
ls -la ~/chroma_index

# Reset if needed
rm -rf ~/chroma_index
```

### Search returns no results
- Try broader queries first, then narrow down
- Check that data was imported successfully with `?`
- Verify the collection name matches (`semantic_knowledge`)

## Advanced Usage

### Working with Multiple Collections
```bash
# Switch to metadata collection
python ingest_knowledge_interactive.py -cn dbt_metadata -em bge-large

# Use different embedding model
python ingest_knowledge_interactive.py -em e5-large

# Custom persistence directory
python ingest_knowledge_interactive.py -pd /tmp/my_index
```

### Schema Filtering (for dbt_metadata collection)
```bash
# Only search specific schemas
python ingest_knowledge_interactive.py -cn dbt_metadata -s data_mart reporting

# Search all schemas
python ingest_knowledge_interactive.py -cn dbt_metadata -s all
```

## Tips for Success

1. **Start with broad queries** - Semantic search works best when you describe concepts rather than exact keywords
2. **Use metadata wisely** - The `??` command shows all metadata which helps refine searches
3. **Experiment with models** - Different embedding models may surface different results
4. **Think like a business user** - Query as if you're asking a question to a colleague
5. **Consider the use case** - This tool is for finding similar accounts/patterns, not exact matches

## Architecture Notes

### Why Three Collections?
The tool maintains three parallel collections (one per embedding model: bge-base, bge-large, e5-large) to:
- Allow model comparison without re-indexing
- Support future model selection features
- Enable ensemble search strategies

### Embedding Model Differences
- **BGE-base**: Faster, smaller (768-dim), good general performance
- **BGE-large**: Slower, larger (1024-dim), better accuracy
- **E5-large**: Different training approach, may excel at specific query types

### Format Prefixes
Models require specific query/document prefixes:
- **BGE**: "Represent this sentence for searching relevant passages: {query}"
- **E5**: "query: {query}" for queries, "passage: {text}" for documents

Good luck with the interview! 🚀