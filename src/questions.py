"""
Pre-defined questions for the J.P. Morgan RAG analysis.
"""

QUESTIONS = {
    "Q1": {
        "id": "Q1",
        "title": "Forecasted Equity Themes",
        "question": """According to J.P. Morgan's Outlook 2025 (the forecast document):
1. Which equity market themes were expected to perform well in 2025?
2. Which specific stocks or groups of stocks (e.g., Apple, Microsoft, Magnificent 7, AI-related equities) were highlighted as investment opportunities or focal points?

Please provide specific names and details with page citations.""",
    },
    "Q2": {
        "id": "Q2",
        "title": "Mid-Year Reality Check",
        "question": """According to J.P. Morgan's Mid-Year Outlook 2025:
1. Which forecasted themes from the 2025 Outlook played out as expected?
2. Which themes or expectations underperformed or disappointed?

Please be specific about what was expected vs what actually happened, with page citations.""",
    },
    "Q3": {
        "id": "Q3",
        "title": "Stock-Level Comparison",
        "question": """Identify at least two named stocks (such as Apple, Microsoft, NVIDIA, or other major companies) and for each:
1. What was implied or stated about them in the 2025 forecast (Outlook 2025)?
2. How is their performance or outlook described at mid-year 2025?

Focus on specific company names mentioned in both documents. Provide citations for each claim.""",
    },
    "Q4": {
        "id": "Q4",
        "title": "Valuation and Risk",
        "question": """Answer the following:
1. What valuation concerns or risk factors were highlighted at the start of 2025 in the Outlook 2025 document?
2. Which of those specific risks materialized by mid-year 2025, according to the Mid-Year Outlook?
3. Were there any new risks that emerged that weren't anticipated in the original forecast?

Provide specific details and citations from both documents.""",
    },
    "Q5": {
        "id": "Q5",
        "title": "Structured Comparison Table",
        "question": """Create a comprehensive comparison of stocks and investment themes between the 2025 Forecast and Mid-Year Reality.

For each stock or theme you can identify in both documents, provide:
- Stock/Theme name
- What the 2025 Forecast said (predictions, expectations)
- What the Mid-Year 2025 shows (actual results, current outlook)
- Whether the forecast was supported (Yes/No/Partially)
- Citations from both documents

Focus on: individual stocks (Apple, Microsoft, NVIDIA, etc.), the Magnificent 7, AI investments, sector allocations, and any other major themes discussed in both documents.""",
    },
}
