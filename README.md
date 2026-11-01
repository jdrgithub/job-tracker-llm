# Job Tracker LLM

A comprehensive job search tracking tool with AI-powered insights and vector search capabilities.

## Quick Start

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run the application
python3 job-tracker.py
```

That's it! The interactive menu will guide you through all features.

## Usage Examples

### Basic Job Tracking

**Add a new job opportunity:**
```
🤖 Job Tracker LLM
========================================
1. Add job opportunity
2. List opportunities
3. Search opportunities
4. Update opportunity
5. Show statistics
6. Export data
7. AI features
8. Setup AI
9. Exit

Enter your choice (1-9): 1

📝 Add New Job Opportunity
------------------------------
Company: Google
Role/Position: Senior Software Engineer
Recruiter Name (optional): Sarah Johnson
Recruiter Contact (optional): sarah.j@google.com
Notes (optional): Remote position, great benefits
Interest Level (1-5): 5

✅ Opportunity added successfully!
```

**List all opportunities:**
```
📋 Job Opportunities
-------------------------
1. Google - Senior Software Engineer
   Interest: 🔥🔥🔥🔥🔥 (5/5) | 🟢 Active
   Recruiter: Sarah Johnson

2. Microsoft - Backend Developer
   Interest: 🔥🔥🔥 (3/5) | 🟢 Active
```

**Search for opportunities:**
```
🔍 Search Results for: 'software engineer'
----------------------------------------
1. Google - Senior Software Engineer
   Interest: 🔥🔥🔥🔥🔥 (5/5)
   Relevance: 0.95

2. Microsoft - Backend Developer
   Interest: 🔥🔥🔥 (3/5)
   Relevance: 0.87
```

### AI-Powered Features

**Setup AI (one-time):**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run the application and select "8. Setup AI"
python3 job-tracker.py
```

**Get AI insights:**
```
🤖 AI Features
=========================
1. Get job search insights
2. Ask AI about opportunities
3. Get follow-up suggestions
4. Analyze specific opportunity
5. Generate follow-up email
6. Get career advice
7. Back to main menu

Enter your choice (1-7): 1

🤖 Getting AI insights...

Based on your job opportunities, here are my insights:

📊 **Current Status:**
- You have 5 active opportunities
- Average interest level: 4.2/5
- Top companies: Google, Microsoft, Amazon

🎯 **Recommendations:**
- Focus on Google (highest interest)
- Follow up with Microsoft within 3 days
- Consider expanding search to include startups
```

**Generate a follow-up email:**
```
Select opportunity for email:
1. Google - Senior Software Engineer
2. Microsoft - Backend Developer

Enter your choice (1-2): 1

🤖 Generating email for Google...

Subject: Follow-up: Senior Software Engineer Position

Dear Sarah,

I hope this email finds you well. I wanted to follow up on my application for the Senior Software Engineer position at Google.

I remain very interested in this opportunity and am excited about the possibility of contributing to Google's innovative projects. I believe my experience in [your relevant skills] would be a great fit for your team.

Please let me know if you need any additional information or if there are next steps in the process.

Thank you for your time and consideration.

Best regards,
[Your Name]
```

**Extract job details from description:**
```
Select opportunity to add job details to:
1. Google - Senior Software Engineer
2. Microsoft - Backend Developer

Enter your choice (1-2): 1

Enter the job description: [Paste job description here]

🤖 Extracting job details for Google...

✅ Added job details: {
  "salary_range": "$150k-$200k",
  "location": "hybrid",
  "tech_stack": ["Python", "AWS", "Docker"],
  "requirements": ["5+ years experience", "ML background"],
  "benefits": ["health insurance", "401k", "stock options"]
}
```

**Generate follow-up strategy:**
```
Select opportunity for strategy:
1. Google - Senior Software Engineer
2. Microsoft - Backend Developer

Enter your choice (1-2): 1

🤖 Generating follow-up strategy for Google...

**Timeline:**
- Follow up within 3-5 days of initial contact
- Send reminder every 7-10 days if no response

**Communication Channels:**
- Primary: Email to sarah.j@google.com
- Secondary: LinkedIn message

**Key Messages:**
- Emphasize relevant ML experience
- Highlight interest in Google's AI projects
- Reference previous conversation points

**Questions to Ask:**
- What are the next steps in the process?
- What does the team structure look like?
- What are the key challenges for this role?
```

**Ask AI about your opportunities:**
```
What would you like to ask about your opportunities?: Which opportunities should I prioritize?

🤖 AI Response:

Based on your current opportunities, here's my prioritization:

🥇 **High Priority (Follow up within 24 hours):**
- Google (Senior Software Engineer) - Interest: 5/5, Active status

🥈 **Medium Priority (Follow up within 3-5 days):**
- Microsoft (Backend Developer) - Interest: 3/5, Good company fit

🥉 **Low Priority (Keep warm):**
- [Other opportunities with lower interest levels]

**Strategy:** Focus your energy on Google while keeping Microsoft engaged. Consider setting reminders for follow-ups.
```

### Data Export

**Export to CSV for analysis:**
```
📤 Export Data
---------------
Export filename [job_opportunities.csv]: my_jobs_2025.csv

✅ Data exported to my_jobs_2025.csv
```

## Configuration

### OpenAI API Setup (for AI features)
```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-api-key-here"

# Test the setup
python3 job-tracker.py
# Then select "8. Setup AI"
```

### Environment Variables
```bash
# Required for AI features
export OPENAI_API_KEY="your-api-key"

# Optional: Customize data directory
export JOB_TRACKER_DATA_DIR="/path/to/data"
```

## Data Privacy

**Your data stays completely local:**
- ✅ Job opportunities never uploaded to GitHub
- ✅ API keys never exposed
- ✅ Vector database stays private
- ✅ All data stored in local `data/` directory

## Vector Database Features

**Primary Storage with AI Enhancement:**
- ✅ **Automatic Vector Storage**: All job data automatically goes into vector database
- ✅ **Rich Data Accumulation**: AI insights and analysis are stored with each opportunity
- ✅ **Semantic Search**: Find opportunities using natural language queries
- ✅ **Intelligent Analysis**: AI uses accumulated data for better insights over time
- ✅ **JSON Backup**: All data also backed up to JSON files for safety

**Data Accumulation:**
- Job details extracted from descriptions
- AI-generated insights and analysis
- Follow-up strategies and recommendations
- Interaction history with AI annotations
- Salary, tech stack, and requirement data

## Project Architecture

### High-Level Overview
```
job-tracker-llm/
├── job-tracker.py              # Main launcher
├── src/job_tracker_llm/        # Core application
│   ├── unified_cli.py          # Interactive menu interface
│   ├── models.py               # Data structures
│   ├── storage.py              # File operations
│   ├── ai_assistant.py         # AI integration
│   ├── vector_store.py         # Vector search
│   ├── utils.py                # Helper functions
│   └── setup_ai.py             # AI setup and testing
├── data/                       # Private data storage
└── tests/                      # Test suite
```

### File Glossary

**`job-tracker.py`** - Single entry point launcher

**`unified_cli.py`** - Interactive menu system for all features

**`models.py`** - Data schemas (JobOpportunity, Interaction, etc.)

**`storage.py`** - Save/load opportunities, search, statistics

**`ai_assistant.py`** - ChatGPT integration for insights and analysis

**`vector_store.py`** - Semantic search using ChromaDB

**`utils.py`** - Input validation and helper functions

**`setup_ai.py`** - AI setup and testing

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/
flake8 src/
```

## License

MIT License - see LICENSE file for details.
