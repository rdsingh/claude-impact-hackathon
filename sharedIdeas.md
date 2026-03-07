# Shared Ideas - Claude Impact Hackathon

## Project Concept

**Budget Transparency + Fraud Detection Tool** for City of San Diego

### Two Core Features

1. **Sustainability Expense Finder**
   - Parse SD budget data
   - Use Claude to categorize sustainability-related expenses (climate, green energy, recycling, EV, water conservation)
   - Show spending trends over time

2. **Benford's Law Auditor**
   - Apply Benford's Law to budget numbers (leading digit distribution)
   - Flag statistical anomalies
   - Visual comparison: expected vs actual distribution

---

## Data Sources

| Dataset | URL | Use Case |
|---------|-----|----------|
| Operating Actuals | data.sandiego.gov/datasets/operating-actuals/ | Benford analysis (actual spending) |
| Operating Budget | data.sandiego.gov/datasets/operating-budget/ | Sustainability categorization |
| CIP Budget | data.sandiego.gov/datasets/capital-budget-fy/ | Green infrastructure |
| Accounts Reference | data.sandiego.gov/datasets/budget-reference-accounts/ | Category lookups |

**Note:** Download links TBD - need to find direct CSV URLs from portal.

---

## Technical Decisions

### Benford's Law Applicability
- **Use Operating Actuals** (real transactions) - spans multiple orders of magnitude
- **Avoid Operating Budget** for Benford - often rounded, politically determined
- Filter out zero/negative values
- Focus on expense amounts, not revenue codes
- Anomalies = flags for review, not proof of fraud

### Suggested Tech Stack
- **Python** - pandas, matplotlib/plotly
- **Claude API** - categorize expenses, explain anomalies
- **Streamlit or Flask** - web UI for demo

---

## Open Questions

- [ ] Direct CSV download URLs from data.sandiego.gov
- [ ] Which sustainability keywords to search for?
- [ ] Threshold for Benford anomaly flagging?
- [ ] Deployment platform (Streamlit Cloud, Vercel, etc.)?

---

## Session Log

**2025-03-07**
- Repo created: github.com/rdsingh/claude-impact-hackathon
- Team: Daman, Rajdeep
- Hackathon ref: github.com/Backland-Labs/city-of-sd-hackathon
- Project idea selected: Budget + Benford's Law
