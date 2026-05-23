"""
H-Automate — groq_client.py
AI diagnosis engine for Nigerian SME business analysis.

Setup:
  1. Create a .env file in your project root
  2. Add this line: GROQ_API_KEY=your_actual_key_here
  3. Install dependencies: pip install groq python-dotenv
"""

import os
from groq import Groq
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES
# API key is read from .env file — never hardcoded.
# ─────────────────────────────────────────────
load_dotenv()

# Check FIRST, then create client — prevents crash on import
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "Missing GROQ_API_KEY. "
        "Create a .env file and add: GROQ_API_KEY=your_key_here"
    )

client = Groq(api_key=api_key)


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# This is the core intelligence of H-Automate.
# Do not modify unless you are improving diagnosis quality.
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an AI business analyst specializing in Nigerian small and medium enterprises,
particularly small retail shops, mini-marts, pharmacies, POS agents, and informal
market businesses in northern Nigeria.

Your job is to analyze pre-calculated sales summaries and produce structured, specific,
and actionable business diagnoses that reveal patterns the business owner has likely
NOT noticed themselves.

You understand Nigerian market realities:
- Seasonal patterns: post-Sallah spending dips, school fee periods, harvest season
  spending increases
- Payment behaviour: cash-dominant informal markets, gradual POS adoption
- Northern Nigeria consumer habits: staple-focused purchasing, price sensitivity,
  community buying patterns
- Common SME challenges in Borno, Kano, Kaduna: irregular supply chains,
  competition from open markets, limited credit access

STRICT RULES — NEVER VIOLATE THESE:
1. Never say "Your sales dropped because..." — always say "Likely contributing
   factors include..."
2. Never recommend discounting fast-moving or high-margin products (Rice, Oil,
   Indomie, Tomato Paste, Sardines) — these are the client's winners
3. Only recommend discounting or bundling slow-moving and dead stock items
4. Automation workflows must be simple operational habits a shop owner can do
   manually or with a basic phone — never suggest building software systems or
   quote implementation costs
5. Every diagnosis must include at least one insight the owner has likely NOT
   noticed from daily observation
6. Dead stock estimates must always include a Naira (₦) value range (e.g.
   ₦18,000–₦25,000) — never a round single number
7. Weekday vs weekend revenue patterns must always be interpreted — explain what
   the gap means operationally, not just report the number
8. Never use jargon like "KPIs", "synergy", "leverage", "optimize", or
   "implement a system"
9. Always reference specific product names from the data
10. Keep language simple enough for a shop owner in Biu, Borno State to understand
11. Never give generic advice like "improve marketing", "increase sales", or
    "enhance customer experience"

INCOMPLETE DATA RULE (CRITICAL):
- All calculations (weekday/weekend revenue, top product percentages, monthly
  averages, dead stock estimates) are pre-computed and provided in the data summary.
  Do NOT invent or estimate any number not explicitly provided.
- If a required data point is missing from the summary, clearly state:
  "Note: [data point] was not available in the uploaded file and could not be
  calculated." Then continue with what IS available.
- Never hallucinate figures. If you are uncertain, say so.

INSIGHT REQUIREMENTS:
- Use the pre-calculated weekday vs weekend revenue difference provided in the
  summary — interpret what the gap means operationally for the business
- Use the pre-calculated top product revenue percentages provided in the summary
- Use the pre-calculated dead stock Naira range provided in the summary
- At least one finding must be observable only from the data pattern, not from
  daily shop floor experience

AUTOMATION WORKFLOW RULES:
- Each workflow must specify WHEN it happens (daily, every Sunday, every Monday)
- Each workflow must specify WHAT exactly is recorded or reviewed
- Each workflow must be completable in under 10 minutes
- Never say "track sales" — say exactly what to track and when
"""


# ─────────────────────────────────────────────
# USER PROMPT TEMPLATE
# Fills in business type and pre-calculated data summary at runtime.
# All numbers in data_summary must be computed by data_cleaner.py first.
# ─────────────────────────────────────────────
def build_user_prompt(business_type: str, data_summary: str) -> str:
    return f"""
Analyze the following pre-calculated sales summary for a {business_type} in Nigeria.

All numbers below have been calculated from the uploaded data.
Use them directly — do not recalculate or invent figures.

DATA SUMMARY:
{data_summary}

Produce a full business diagnosis in this exact format:

---
BUSINESS HEALTH SNAPSHOT
Revenue Stability: [score]/100 — [status]
Customer Activity: [score]/100 — [status]
Expense Efficiency: [score]/100 — [status]
Inventory Health: [score]/100 — [status]
Overall Business Health: [score]/100 — [status]
Top Risk: [one sentence — must name a specific product or pattern, not a general statement]

---
AI DIAGNOSIS
[2–3 paragraphs. Must include:
- Specific transaction counts and daily averages by month (from summary)
- Named products from the data
- At least one pattern the owner likely has NOT noticed
- The meaning of the weekday vs weekend revenue gap — not just the number
- If any data was missing, note it clearly without inventing alternatives]

---
LIKELY CONTRIBUTING FACTORS
[3–5 numbered points. Each must:
- Name a specific cause tied to the provided data
- Include Nigerian market context where relevant
- Never start with "Your sales dropped because..."]

---
RECOMMENDED ACTIONS

Immediate (This Week):
- [Must name a specific product. No discounting of fast-moving items.]

Short-Term (Next 30 Days):
- [Specific and practical. Must be something a shop owner can do without technology.]

Medium-Term (Next 90 Days):
- [Must include a Naira (₦) estimate of potential savings or capital recovery,
   using figures from the data summary only.]

---
SUGGESTED AUTOMATION WORKFLOWS
[3 simple operational habits — things the owner can do with a notebook, phone
calculator, or basic WhatsApp. No software systems. No cost estimates.
Each must say WHEN and WHAT exactly.]
1.
2.
3.

---
IMPORTANT NOTE
End with exactly this: "These findings are based on sales transaction patterns
only. Likely contributing factors are identified from data trends and general
market behaviour — they are not absolute causes. Ground-truth validation with
the business owner is recommended before acting on any recommendation."
"""


# ─────────────────────────────────────────────
# MAIN DIAGNOSIS FUNCTION
# Call this from main.py or any route handler.
#
# Parameters:
#   business_type (str) — "mini-mart", "pharmacy", "pos-agent",
#                         "restaurant", or "fashion-store"
#   data_summary  (str) — pre-calculated summary from data_cleaner.py
#
# Returns:
#   str — full structured diagnosis text, or error string on failure
# ─────────────────────────────────────────────
def get_diagnosis(business_type: str, data_summary: str) -> str:
    """
    Send a pre-calculated data summary to Groq and return a structured diagnosis.

    IMPORTANT: data_summary must be prepared by data_cleaner.py before calling
    this function. Do not pass raw CSV content — pass the computed summary only.

    Returns a DIAGNOSIS_ERROR string on failure so the caller can handle it
    gracefully without crashing the app.

    Example usage:
        from groq_client import get_diagnosis
        result = get_diagnosis("mini-mart", summary_text)
        if result.startswith("DIAGNOSIS_ERROR"):
            # show error state in UI
        else:
            # render diagnosis
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2500,          # Increased from 2000 to prevent cutoff
            temperature=0.4,          # Lower = more consistent, structured output
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(
                    business_type, data_summary
                )}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        # Return structured error string — caller decides how to surface it
        return f"DIAGNOSIS_ERROR: {str(e)}"


# ─────────────────────────────────────────────
# QUICK TEST — run this file directly to verify
# your API key and prompt are working correctly.
# Usage: python groq_client.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_summary = """
    Business Type: Mini-Mart
    Total transactions: 1,613 (January 1, 2026 – April 30, 2026)

    Monthly daily revenue averages:
      January: ₦54,000/day (over 26 active days)
      February: ₦49,000/day (over 24 active days)
      March:    ₦41,000/day (over 27 active days)
      April:    ₦38,000/day (over 25 active days)

    Revenue trend: DECLINING (-29.6% from first to last month)

    Weekday vs weekend revenue (pre-calculated):
      Average weekday daily revenue: ₦42,000
      Average weekend daily revenue: ₦58,000
      Daily gap: ₦16,000 (+38.1%)
      Weekend share of total revenue: 38.0%

    Top products by revenue share (pre-calculated):
      Rice: 31.0%
      Vegetable Oil: 22.0%
      Indomie: 14.0%
      Tomato Paste: 9.0%
      Sardines: 7.0%
      Top 3 combined: 67.0% of total revenue

    Slow / dead stock (no sales in 14+ days):
      Biscuits: last sold Mar 12, 2026,
                estimated tied capital ₦18,000–₦23,000 [confidence: medium]
      Tissue Paper: last sold Feb 28, 2026,
                    estimated tied capital ₦9,000–₦12,000 [confidence: medium]

    Payment method breakdown:
      Cash: 55.0%
      POS: 30.0%
      Bank Transfer: 15.0%
    """

    print("Running H-Automate diagnosis test...\n")
    print("=" * 60)
    result = get_diagnosis("mini-mart", test_summary)

    if result.startswith("DIAGNOSIS_ERROR"):
        print(f"ERROR: {result}")
    else:
        print(result)

    print("=" * 60)
    print("\nTest complete.")

# Made with Bob
