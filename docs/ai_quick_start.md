# AI Integration Quick Start

## 🚀 Get Started with ChatGPT + Your Job Tracker

Transform your job tracker into an intelligent career assistant with ChatGPT integration!

## What You Get

- **🤖 AI Job Search Analysis** - Get insights about your job search progress
- **🔍 Smart Opportunity Search** - Find opportunities using natural language
- **📧 AI Email Generation** - Professional follow-up emails
- **💡 Career Advice** - Personalized guidance based on your data
- **📊 Follow-up Suggestions** - AI-recommended next steps

## Quick Setup (3 Steps)

### 1. Get OpenAI API Key
```bash
# Go to https://platform.openai.com/api-keys
# Create account and get your API key (starts with sk-)
```

### 2. Set Up Environment
```bash
# Set your API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Install dependencies (when available)
pip install -r requirements.txt
```

### 3. Run AI Setup
```bash
# Set up AI features
python3 scripts/setup_ai.py

# Start using AI assistant
python3 src/job_tracker_llm/ai_cli.py
```

## Example AI Interactions

### Get Job Search Insights
```
🤖 AI Assistant Menu:
1. Get job search insights

AI Response:
📊 Overall Progress:
- You have 15 total opportunities with 8 active
- Average interest level is 3.2/5
- 3 opportunities need follow-up

💡 Recommendations:
1. Prioritize follow-ups on overdue opportunities
2. Focus on remote positions (highest interest)
3. Update LinkedIn profile for more visibility
```

### Ask About Opportunities
```
🤖 AI Assistant Menu:
2. Ask AI about opportunities

Your Question: "Which opportunities should I prioritize?"

AI Response:
🔥 High Priority:
1. TechCorp - Senior Software Engineer (Interest: 5/5)
2. StartupXYZ - Full Stack Developer (Interest: 4/5)

⚡ Medium Priority:
3. BigCompany - Software Engineer (needs follow-up)
```

### Generate Follow-up Email
```
🤖 AI Assistant Menu:
5. Generate follow-up email

AI Response:
Subject: Follow-up: Senior Software Engineer Position at TechCorp

Dear [Recruiter Name],

I hope this email finds you well. I wanted to follow up regarding my application for the Senior Software Engineer position at TechCorp.

I remain very interested in this opportunity and am excited about the possibility of contributing to TechCorp's innovative projects...

Best regards,
[Your Name]
```

## Available AI Features

| Feature | Description | Example Use |
|---------|-------------|-------------|
| **Job Search Insights** | Complete analysis of your job search | "How am I doing overall?" |
| **Ask Questions** | Natural language queries about opportunities | "Which companies are most promising?" |
| **Follow-up Suggestions** | AI-recommended follow-up strategies | "What should I do next?" |
| **Opportunity Analysis** | Deep dive into specific opportunities | "Analyze this specific job" |
| **Email Generation** | Professional follow-up emails | "Write a follow-up email" |
| **Career Advice** | Personalized career guidance | "How can I improve my resume?" |

## Cost Estimate

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical analysis**: $0.01-0.05 per request
- **Monthly usage**: $0.10-1.00 (10-20 requests)

## Troubleshooting

### "OpenAI API Key Not Set"
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### "No Opportunities Found"
```bash
# Add opportunities first
python3 src/job_tracker_llm/simple_cli.py
```

### "Vector Database Not Built"
```bash
# Run setup
python3 scripts/setup_ai.py
```

## Next Steps

1. **Start Simple**: Try "Get job search insights" first
2. **Experiment**: Ask different types of questions
3. **Customize**: Modify prompts in `ai_assistant.py`
4. **Automate**: Create scripts for regular analysis

## Full Documentation

For detailed setup and advanced usage, see:
- [AI Integration Guide](ai_integration_guide.md)
- [Implementation Summary](implementation_summary.md)

---

**🎉 Your job tracker is now an intelligent career assistant!** 