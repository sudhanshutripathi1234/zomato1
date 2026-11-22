# AI-Powered Restaurant Recommendation System (Zomato Use Case)

## Project overview

Build an AI-powered restaurant recommendation service inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining structured restaurant data with a Large Language Model (LLM).

## Objective

Design and implement an application that:

- Takes user preferences (such as location, budget, cuisine, and ratings)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

## Dataset

- **Source:** [Zomato Restaurant Recommendation dataset on Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Ingestion:** Load and preprocess the dataset
- **Relevant fields (examples):** restaurant name, location, cuisine, cost, rating, and related attributes needed for filtering and prompting

## System workflow

### 1. Data ingestion

- Load the Zomato dataset from Hugging Face
- Preprocess and extract relevant fields (name, location, cuisine, cost, rating, etc.)

### 2. User input

Collect user preferences:

| Preference | Examples / notes |
|---|---|
| Location | e.g. Bangalore |
| Budget | low, medium, high |
| Cuisine | e.g. Italian, Chinese |
| Minimum rating | numeric threshold |
| Additional preferences | e.g. family-friendly, quick service |

### 3. Integration layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason about and rank options

### 4. Recommendation engine

Use the LLM to:

- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output display

Present top recommendations in a user-friendly format:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation

## Architecture (logical)

```
User preferences
       │
       ▼
┌──────────────────┐
│ Data ingestion   │  ← Hugging Face Zomato dataset
│ + preprocessing  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Filter / prepare │  ← match location, budget, cuisine, rating, etc.
│ candidate set    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM prompt       │  ← structured candidates + user prefs
│ + ranking        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ UI / output      │  ← name, cuisine, rating, cost, explanation
└──────────────────┘
```

## Success criteria

- Users can submit preferences and receive ranked restaurant suggestions
- Recommendations are grounded in the real dataset (not invented listings)
- Each suggestion includes a clear LLM-generated explanation of fit
- Output is readable and useful for decision-making

## Current project status

- Problem statement, architecture, implementation plan, and edge-case docs defined
- **Phase 1 complete:** project scaffold, HF dataset load/preprocess, in-memory store + parquet cache
- **Phase 2 complete:** preference models, hard/soft filters, candidate capping + unit tests
- **Phase 3 complete:** Groq LLM ranking + explanations, mock client, orchestrator, grounded parsing
- **Phase 4 complete:** Streamlit UI, friendly edge handling, logging, polished README — **v1 demo-ready**

Run the app: `streamlit run src/app.py`
