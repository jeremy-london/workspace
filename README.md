# Knowledge Base Tool - Technical Interview

## Overview

This is an interactive CLI tool for managing semantic knowledge using ChromaDB vector databases. It enables RAG (Retrieval-Augmented Generation) style lookups on business data, allowing you to find similar accounts, identify patterns, and query customer information semantically.

This technical interview evaluates candidates by providing a comprehensive semantic search system with multiple datasets and letting candidates demonstrate their technical depth, system design skills, and business understanding through self-guided exploration and improvements.

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

```bash
> r data/sample_data.json
✅ Imported records to all 3 collections for 'imported_data'.
```

### 2. Try searching

```bash
> ? threat detection
> ? customer churn risk  
> ? government fedramp
```

### 3. List all entries
```
> ?
```

## Available Data Samples

The repository includes three distinct datasets for comprehensive evaluation:

### 📊 `data/sample_data.json` - Keeper Product Knowledge
**Purpose**: General semantic search testing with Keeper Security domain knowledge

**Content**: 
- Company descriptions (Keeper Security, KeeperAI, zero-knowledge platform)
- Product capabilities (password management, PAM, threat detection)
- Technical details (ARAM events, session recordings, behavioral analysis)
- Compliance information (FedRAMP authorization, government customers)

**Sample Entry**:
```json
{
   "id": "fact_1704153600000", 
   "text": "KeeperAI uses machine learning to detect insider threats by analyzing privileged session commands in real-time.",
   "metadata": {"source": "product_info", "timestamp": "2024-01-02 00:00:00"}
}
```

### 🏢 `data/account_data.json` - Customer Account Intelligence
**Purpose**: Real-world customer data for business intelligence and analytics workflows

**Content**: 20 detailed Salesforce customer accounts including:
- **Account Profiles**: Names, industries, employee counts, contract values ($18K-$680K ARR)
- **Product Usage**: KeeperPAM versions (Enterprise/Business/GovCloud), Secrets Manager, RBI, EPM
- **Health Metrics**: Health scores (41-94/100), adoption rates (33-95%), NPS scores (4-10)
- **Usage Data**: Gateway connections, session recordings, ARAM events generated
- **Risk Indicators**: Support tickets, churn risk levels, executive sponsors, renewal dates
- **Compliance**: FedRAMP requirements, SIEM integrations (Splunk, QRadar, Sentinel)

**Sample Entries**:
- **Healthy Account**: Acme Financial Services - 85/100 health, 92% adoption, strong Splunk integration
- **At-Risk Account**: TechCorp Industries - 45/100 health, 38% adoption, 18 support tickets, no SIEM
- **Critical Account**: RetailMax Corporation - 41/100 health, 33% adoption, executive sponsor left
- **Enterprise**: Federal Defense Logistics Agency - 92/100 health, FedRAMP certified, $450K ARR

```json
{
   "id": "acct_001_profile",
   "text": "Account: Acme Financial Services. Industry: Banking & Finance. Employees: 2500. Contract Value: $125K ARR. Products: KeeperPAM Enterprise, Secrets Manager. Deployment Date: 2024-03-15. Health Score: 85/100. Gateway Connections Last 30d: 45,230. Privileged Users: 340. Active Users: 312 (92% adoption). Session Recordings: 8,420. ARAM Events Generated: 1,250. SIEM Integration: Splunk. Primary Contact: Sarah Chen, CISO. Last QBR: 2025-08-15. Renewal Date: 2026-03-15. Expansion Opportunity: Remote Browser Isolation. Support Tickets Last Quarter: 3 (avg resolution 2.5hrs). NPS Score: 9. Risk Factors: None. FedRAMP Required: No.",
   "metadata": {"source": "salesforce_account_export", "timestamp": "2025-09-30 08:00:00", "account_id": "SF-001-ACME-FIN", "industry": "financial_services", "health_score": "85", "churn_risk": "low"}
}
```

### 📈 `data/churn_prediction.json` - Customer Success Analytics  
**Purpose**: Analytics insights and patterns for predictive modeling and business intelligence

**Content**: Customer success analytics including:
- **Churn Prediction Patterns**: Onboarding timelines, adoption patterns, retention correlations
- **Product Impact Analysis**: KeeperAI adoption → 65% higher renewal rates, feature usage correlations
- **Support Analytics**: Ticket resolution patterns, onboarding delays → churn risk
- **Compliance Insights**: FedRAMP documentation requirements, deployment timelines
- **Behavioral Patterns**: Session activity correlations, threat detection effectiveness

**Sample Entry**:

```json
{
   "id": "fact_1727894531002",
   "text": "Customers who adopt KeeperAI threat detection within 90 days show 65% higher renewal rates compared to those using only password management features",
   "metadata": {"source": "Product Analytics", "timestamp": "2025-09-20 09:15:33"}
}
```

**Pro tip for candidates**: Load multiple datasets sequentially to see how the system handles different data structures and scales.

## Interview Timeline (2 hours total)

### Phase 1: Understanding & Technical Analysis

**Explore the system and demonstrate deep ML understanding**

**Areas to investigate:**
- How embedding models work (BGE vs E5 differences)  
- Model architecture tradeoffs (speed vs accuracy vs memory)
- Optimization opportunities (quantization, mixed precision)
- Scale considerations (1M documents, high QPS requirements, updates to embedding models)

**Questions candidates might explore:**
- What are the quantization vs accuracy tradeoffs for semantic search?
- How would you architect this for production scale?
- What alternatives to sentence-transformers exist?

### Phase 2: Deep Dive & Business Fit

**Explore LLM integration possibilities**
- Could this be enhanced with query expansion?
- How might answer synthesis improve over raw document retrieval?
- What about synthetic data generation for testing?
- Design agentic systems that can reason and act on search results

**Transform into analytics and business intelligence system**  
- Design data warehouse schemas for the account data
- Implement EDA workflows and correlation analysis
- Traditional feature engineering vs embedding-based approaches

### Phase 3: System Design & Implementation
**Demonstrate architectural thinking and practical implementation**

- Explore bugs and address quality/functionality issues
- Multi-interface architecture (CLI, REST API, Web UI, Python SDK)
- Production considerations (monitoring, caching, testing, error handling)
- Privacy and compliance (FedRAMP, audit trails, explainable AI)

**Implementation focus:**
- Pick specific areas for enhancement and implement them
- Show understanding of production constraints
- Demonstrate business alignment with Keeper's needs

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
| `--load-file FILE` | Load data from a specific JSON file on startup | `--load-file data/churn_prediction.json` |
| `--dont-clear` | Do **not** clear ChromaDB collections on startup | `--dont-clear` |


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
- Export/Import format options (CSV, JSONL)

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

### Advanced Capabilities
- Hybrid search (semantic + keyword retrieval)
- Metadata filtering with complex queries
- Cross-encoder reranking for relevance
- Query-by-example functionality
- Multi-modal search across different data types

## Business Context & Applications

### Keeper Security Domain Applications
- **Threat Detection**: Use account behavior patterns to identify insider threats
- **Customer Success**: Early warning systems for churn risk and expansion opportunities  
- **Compliance**: Automated FedRAMP documentation and audit trail generation
- **Product Analytics**: Understanding feature adoption patterns and usage correlations

### Real-World Integration Possibilities
- **Session Recording Analysis**: Search across behavioral patterns in video/text transcripts
- **ARAM Event Processing**: Real-time threat scoring based on command analysis
- **Support Ticket Intelligence**: Pattern analysis for automated routing and resolution
- **Compliance Automation**: Regulatory document generation and validation

## Advanced Usage

### Working with Different Datasets
```bash
# Load product knowledge
python ingest_knowledge_interactive.py --load-file data/sample_data.json

# Load customer accounts  
python ingest_knowledge_interactive.py --load-file data/account_data.json

# Load analytics data
python ingest_knowledge_interactive.py --load-file data/churn_prediction.json
```

### Working with Multiple Models
```bash
# Switch to larger model
python ingest_knowledge_interactive.py -em bge-large

# Try E5 model
python ingest_knowledge_interactive.py -em e5-large
```

Good luck with the interview! 🚀