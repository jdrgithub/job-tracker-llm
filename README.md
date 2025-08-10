# Job Tracker LLM

A comprehensive job search tracking tool with AI-powered insights and vector search capabilities.

## Features

- **Job Opportunity Tracking**: Store and manage job opportunities with detailed metadata
- **Interaction History**: Track all interactions with recruiters and companies
- **Interest Level Management**: Rate opportunities on a 1-5 scale
- **Vector Search**: AI-powered search across all your job opportunities
- **Status Tracking**: Monitor active, inactive, and rejected opportunities
- **Follow-up Reminders**: Never miss important follow-ups
- **Data Export**: Export your data for analysis

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd job-tracker-llm

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

```bash
# Run the CLI tool
python src/job_tracker_llm/cli.py

# Or use the installed command
job-tracker
```

## Usage

### Basic Commands

1. **Add New Opportunity**: Track a new job opportunity
2. **Update Existing**: Modify details of existing opportunities
3. **Search Opportunities**: Find opportunities using AI-powered search
4. **Generate Reports**: Get insights about your job search progress

### Data Structure

Each job opportunity is stored as a JSON file with the following structure:

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "company": "Example Corp",
  "role": "Senior Software Engineer",
  "recruiter_name": "John Doe",
  "recruiter_contact": "john@example.com",
  "interest_level": 4,
  "active": true,
  "interactions": [
    {
      "date": "2025-01-15T10:30:00",
      "type": "initial_contact",
      "method": "recruiter_email",
      "notes": "Initial outreach from recruiter"
    }
  ]
}
```

## Configuration

Set up your OpenAI API key for vector search capabilities:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Development

### Project Structure

```
job-tracker-llm/
├── src/job_tracker_llm/
│   ├── cli.py          # Main CLI application
│   ├── models.py       # Data models and validation
│   ├── storage.py      # File operations and data persistence
│   ├── vector_store.py # Vector database operations
│   └── utils.py        # Helper functions
├── data/opportunities/ # Job opportunity JSON files
├── tests/              # Test suite
└── docs/               # Documentation
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
