# ChatGPT Integration Guide

## Overview

This guide shows you how to integrate ChatGPT with your local job tracker vector database to create an intelligent job search assistant. The AI can analyze your opportunities, provide insights, suggest follow-ups, and even generate emails.

## How It Works

### 1. **Vector Database**
- Your job opportunities are converted into vector embeddings
- Each opportunity becomes a searchable document with metadata
- The vector database enables semantic search across all your data

### 2. **ChatGPT Integration**
- ChatGPT receives context about your job opportunities
- It can analyze patterns, provide insights, and give recommendations
- The AI understands your specific job search situation

### 3. **Intelligent Features**
- **Semantic Search**: Find opportunities using natural language
- **AI Insights**: Get analysis of your job search progress
- **Follow-up Suggestions**: AI-recommended follow-up strategies
- **Email Generation**: Professional follow-up emails
- **Career Advice**: Personalized career guidance

## Setup Instructions

### Step 1: Install Dependencies

```bash
# Install required packages
pip install openai chromadb langchain

# Or install all dependencies
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Copy the key (it starts with `sk-`)

### Step 3: Set Up API Key

```bash
# Set for current session
export OPENAI_API_KEY="sk-your-api-key-here"

# Or save to your shell profile (~/.bashrc, ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Run AI Setup

```bash
# Run the AI setup script
python3 scripts/setup_ai.py
```

This script will:
- Check dependencies
- Validate your API key
- Set up the vector database
- Test AI features

## Using the AI Assistant

### Start the AI CLI

```bash
python3 src/job_tracker_llm/ai_cli.py
```

### Available AI Features

#### 1. **Get Job Search Insights**
```
🤖 AI Assistant Menu:
1. Get job search insights
```

The AI analyzes your entire job search and provides:
- Overall progress assessment
- Pattern analysis (companies, roles, sources)
- Interest level recommendations
- Follow-up strategy suggestions
- Areas for improvement
- Next steps

#### 2. **Ask AI About Opportunities**
```
🤖 AI Assistant Menu:
2. Ask AI about opportunities
```

Ask natural language questions like:
- "Which opportunities should I prioritize?"
- "What patterns do you see in my applications?"
- "How can I improve my response rate?"
- "Which companies are most promising?"

#### 3. **Get Follow-up Suggestions**
```
🤖 AI Assistant Menu:
3. Get follow-up suggestions
```

The AI will:
- Identify opportunities needing follow-up
- Suggest timing and approach
- Recommend communication methods
- Provide talking points

#### 4. **Analyze Specific Opportunity**
```
🤖 AI Assistant Menu:
4. Analyze specific opportunity
```

Get detailed analysis of a specific job opportunity:
- Opportunity assessment and potential
- Interest level analysis
- Follow-up strategy
- Key talking points
- Comparison with similar opportunities
- Risk factors and considerations

#### 5. **Generate Follow-up Email**
```
🤖 AI Assistant Menu:
5. Generate follow-up email
```

The AI creates professional follow-up emails that:
- Reference the specific role and company
- Show continued interest
- Ask about next steps
- Maintain professional tone
- Include clear call to action

#### 6. **Get Career Advice**
```
🤖 AI Assistant Menu:
6. Get career advice
```

Ask for career guidance based on your job search context:
- "How can I improve my interview skills?"
- "What should I focus on in my resume?"
- "How do I negotiate salary?"
- "What career path should I consider?"

## Example AI Interactions

### Example 1: Job Search Analysis

**You:** "Get job search insights"

**AI Response:**
```
Based on your job search data, here's my analysis:

📊 Overall Progress:
- You have 15 total opportunities with 8 active
- Average interest level is 3.2/5, indicating moderate engagement
- 3 opportunities need follow-up (overdue by 7+ days)

🎯 Key Patterns:
- Most opportunities are from LinkedIn (60%)
- You're targeting software engineering roles primarily
- Interest levels are highest for remote positions

💡 Recommendations:
1. Prioritize follow-ups on the 3 overdue opportunities
2. Consider diversifying your application sources
3. Focus on remote opportunities where your interest is highest
4. Update your LinkedIn profile to attract more recruiters

📈 Next Steps:
- Schedule follow-ups for this week
- Apply to 2-3 new opportunities
- Update your resume with recent projects
```

### Example 2: Specific Question

**You:** "Which opportunities should I prioritize?"

**AI Response:**
```
Based on your data, here are the opportunities to prioritize:

🔥 High Priority (Interest Level 4-5):
1. **TechCorp - Senior Software Engineer**
   - Interest: 5/5, Active status
   - Recent interaction: 2 days ago
   - Next step: Technical interview scheduled
   - Action: Prepare for technical interview

2. **StartupXYZ - Full Stack Developer**
   - Interest: 4/5, Active status
   - Source: Referral (stronger than cold applications)
   - Next step: Follow up on application
   - Action: Send follow-up email

⚡ Medium Priority (Interest Level 3):
3. **BigCompany - Software Engineer**
   - Interest: 3/5, Active status
   - Overdue follow-up (8 days)
   - Action: Immediate follow-up needed

💡 Strategy:
- Focus on TechCorp and StartupXYZ as they have highest potential
- Quick follow-up on BigCompany to maintain momentum
- Consider increasing interest level for opportunities with good company culture
```

### Example 3: Generated Email

**You:** Generate follow-up email for "TechCorp - Senior Software Engineer"

**AI Response:**
```
Subject: Follow-up: Senior Software Engineer Position at TechCorp

Dear [Recruiter Name],

I hope this email finds you well. I wanted to follow up regarding my application for the Senior Software Engineer position at TechCorp.

I remain very interested in this opportunity and am excited about the possibility of contributing to TechCorp's innovative projects. I believe my experience in [relevant skills] aligns well with the role requirements.

Could you please provide an update on the status of my application and the next steps in the hiring process? I'm available for any additional interviews or discussions at your convenience.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
[Your Name]
[Your Contact Information]
```

## Advanced Usage

### Custom AI Prompts

You can modify the AI prompts in `src/job_tracker_llm/ai_assistant.py` to customize the AI's behavior:

```python
# Example: Modify the system prompt for job search insights
system_prompt = f"""You are an expert job search coach specializing in tech careers. 
Analyze this job search data and provide insights:

{stats_context}

Recent Opportunities:
{context}

Provide a comprehensive analysis including:
1. Overall job search health and progress
2. Patterns in the opportunities (companies, roles, sources)
3. Interest level analysis and recommendations
4. Follow-up strategy suggestions
5. Areas for improvement
6. Next steps to take

Be encouraging but honest. Provide specific, actionable advice."""
```

### Vector Search Customization

Customize the vector search behavior:

```python
# Search with different parameters
results = ai_assistant.vector_store.semantic_search(
    query="software engineer remote",
    k=10,  # Number of results
    filters={"active": True}  # Only active opportunities
)
```

### Batch AI Analysis

Create scripts for batch analysis:

```python
from job_tracker_llm.ai_assistant import JobTrackerAI
from job_tracker_llm.storage import JobStorage
from job_tracker_llm.vector_store import JobVectorStore

# Initialize
storage = JobStorage()
vector_store = JobVectorStore(storage)
ai = JobTrackerAI(storage, vector_store)

# Batch analysis
insights = ai.get_job_search_insights()
print(insights)

# Analyze all active opportunities
active_opps = [opp for opp in storage.list_opportunities() if opp['active']]
for opp in active_opps:
    analysis = ai.analyze_opportunity(opp['company'], opp['role'])
    print(f"\nAnalysis for {opp['company']}:")
    print(analysis)
```

## Troubleshooting

### Common Issues

#### 1. **OpenAI API Key Not Set**
```
Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable.
```
**Solution:** Set your API key:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

#### 2. **Vector Database Not Built**
```
Error: Vector store not available. Run build_index() first.
```
**Solution:** Build the vector index:
```bash
python3 scripts/setup_vector_db.py
```

#### 3. **No Opportunities Found**
```
Warning: No job opportunities found to index.
```
**Solution:** Add opportunities first:
```bash
python3 src/job_tracker_llm/simple_cli.py
```

#### 4. **API Rate Limits**
```
Error: Rate limit exceeded.
```
**Solution:** Wait a moment and try again, or upgrade your OpenAI plan.

### Performance Tips

1. **Limit Results**: Use smaller `k` values for faster responses
2. **Cache Responses**: Store AI responses for repeated questions
3. **Batch Operations**: Process multiple opportunities together
4. **Optimize Prompts**: Keep prompts concise for faster responses

## Security Considerations

1. **API Key Security**: Never commit your API key to version control
2. **Data Privacy**: Your job data stays local; only summaries are sent to OpenAI
3. **Rate Limiting**: Be mindful of API usage and costs
4. **Data Validation**: Always review AI-generated content before using

## Cost Management

OpenAI API costs depend on:
- **Model used**: GPT-3.5-turbo is cheaper than GPT-4
- **Token usage**: Longer prompts cost more
- **Number of requests**: More interactions = higher costs

**Estimated costs:**
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- Typical job search analysis: $0.01-0.05 per request
- Monthly usage (10-20 requests): $0.10-1.00

## Next Steps

1. **Start Simple**: Begin with basic insights and questions
2. **Experiment**: Try different types of questions and prompts
3. **Customize**: Modify prompts to match your specific needs
4. **Integrate**: Use AI insights in your job search strategy
5. **Automate**: Create scripts for regular AI analysis

The AI integration transforms your job tracker from a simple data storage tool into an intelligent career assistant that can provide personalized insights and recommendations based on your actual job search data! 