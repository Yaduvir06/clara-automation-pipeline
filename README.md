# Clara AI Automation Pipeline

Automated system to convert demo and onboarding call transcripts into production-ready Retell AI voice agent configurations.

## Overview

This pipeline processes call transcripts through two stages:

1. **Demo Call → v1 Agent**: Extracts preliminary configuration from exploratory demo calls
2. **Onboarding Call/Form → v2 Agent**: Updates configuration with confirmed operational details

### Architecture
```
Demo Transcript → Extract Data → Account Memo v1 → Generate Agent Prompt → Agent Spec v1
                                        ↓
Onboarding Input → Extract Updates → Merge with v1 → Account Memo v2 → Agent Spec v2
                                                              ↓
                                                        Changelog
```

## Tech Stack

- **LLM**: Ollama (llama3.2:3b) - local, zero-cost
- **Automation**: n8n - visual workflow orchestration
- **Storage**: Local JSON files with versioning
- **Language**: Python 3.8+

## Project Structure
```
clara-automation/
├── data/
│   ├── demo/              # Demo call transcripts (.txt)
│   └── onboarding/        # Onboarding transcripts (.txt) or forms (.json)
├── outputs/
│   └── accounts/
│       └── ACC001/
│           ├── v1/        # Demo-derived outputs
│           │   ├── account_memo.json
│           │   └── agent_spec.json
│           └── v2/        # Onboarding-updated outputs
│               ├── account_memo.json
│               ├── agent_spec.json
│               ├── changelog.json
│               └── onboarding_form.json (if form input)
├── prompts/               # LLM prompt templates
│   ├── extract_account_memo_prompt.txt
│   └── generate_agent_prompt.txt
├── schemas/               # JSON schemas for data validation
│   ├── account_memo_schema.json
│   └── agent_spec_schema.json
├── scripts/               # Processing scripts
│   ├── pipeline.py        # Main orchestration
│   ├── merge_account_updates.py
│   └── process_onboarding_form.py
└── workflows/             # n8n workflow exports
    ├── demo_pipeline.json
    └── onboarding_pipeline.json
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+ (for n8n)
- 4GB+ RAM (for Ollama)

### Installation

1. **Clone repository**
```bash
   git clone <your-repo-url>
   cd clara-automation
```

2. **Install Python dependencies**
```bash
   pip install -r requirements.txt
```

3. **Install Ollama**
   
   Windows:
   - Download from https://ollama.com/download
   - Run installer
   
   Mac/Linux:
```bash
   curl -fsSL https://ollama.com/install.sh | sh
```

4. **Download LLM model**
```bash
   ollama pull llama3.2:3b
```

5. **Start Ollama** (if not auto-started)
```bash
   ollama serve
```

6. **Install n8n**
```bash
   npx n8n
```
   - Opens at http://localhost:5678
   - Create local account (free)

### Import n8n Workflows

1. Open http://localhost:5678
2. Go to "Workflows" menu
3. Click "Import from File"
4. Import both workflows:
   - `workflows/demo_pipeline.json`
   - `workflows/onboarding_pipeline.json`

## Usage

### Method 1: n8n Visual Workflows (Recommended)

**Process Demo Calls:**
1. Place transcript files in `data/demo/` (e.g., `demo1.txt`)
2. Open "Clara Demo Call Processor" workflow in n8n
3. Click "Test workflow"
4. Check `outputs/accounts/ACC001/v1/` for results

**Process Onboarding:**
1. Place transcripts/forms in `data/onboarding/`
2. Open "Clara Onboarding Call Processor" workflow
3. Click "Test workflow"
4. Check `outputs/accounts/ACC001/v2/` for results

### Method 2: Command Line

**Single demo call:**
```bash
python scripts/pipeline.py demo data/demo/transcript1.txt ACC001
```

**Single onboarding call:**
```bash
python scripts/pipeline.py onboard data/onboarding/transcript1.txt ACC001
```

**Onboarding form (JSON):**
```bash
python scripts/process_onboarding_form.py data/onboarding/form.json ACC001
```

### Method 3: Batch Processing

**Process all demos:**
```bash
python run_all_demos.py
```

**Process all onboarding:**
```bash
python run_all_onboarding.py
```

## Output Files

### Account Memo (account_memo.json)
Structured business configuration:
```json
{
  "account_id": "ACC001",
  "company_name": "Springfield Fire Protection",
  "business_hours": {...},
  "emergency_definition": [...],
  "emergency_routing_rules": {...},
  "questions_or_unknowns": [...],
  "version": "v1"
}
```

### Agent Spec (agent_spec.json)
Retell agent configuration:
```json
{
  "agent_name": "Springfield Fire Protection - Clara Voice Agent",
  "system_prompt": "You are a voice agent answering calls for...",
  "configuration": {...},
  "metadata": {...}
}
```

### Changelog (changelog.json)
Version differences:
```json
{
  "from_version": "v1",
  "to_version": "v2",
  "summary": [
    "Updated timezone: null → 'America/Chicago'",
    "Updated emergency_routing_rules.transfer_timeout_seconds: 60 → 45"
  ]
}
```

## Key Features

### ✅ No Hallucination
- Extracts ONLY explicitly stated information
- Flags missing data in `questions_or_unknowns`
- Never invents details

### ✅ Smart Merging
- Updates v1 with onboarding data without overwriting unrelated fields
- Generates detailed changelogs

### ✅ Dual Input Support
- Handles onboarding transcripts (unstructured)
- Handles onboarding forms (structured JSON)

### ✅ Idempotent & Versioned
- Running twice produces same results
- Clear v1 → v2 progression
- Complete audit trail

## Testing

Run extraction on sample data:
```bash
python test_extraction.py
```

Expected output: `test_output.json` with structured data

## Known Limitations

- **Local LLM quality**: Ollama 3B model may miss nuanced details. Upgrade to llama3.1:8b for better accuracy.
- **No authentication**: n8n workflows are local-only. For production, add auth.
- **File naming**: Batch processing assumes sequential naming. Real implementation should use metadata mapping.
- **Error handling**: Limited retry logic. Production needs robust error recovery.

## Future Improvements

With production access:
- Use Claude/GPT-4 API for higher quality extraction
- Add Retell API integration for automatic agent deployment
- Implement Asana/task tracker integration
- Add validation layer (schema checking, business rule enforcement)
- Build web dashboard for monitoring
- Add support for audio transcription (Whisper integration)

## License

MIT

## Contact

