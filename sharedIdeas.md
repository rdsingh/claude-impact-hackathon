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

## Data Processing Pipeline

### Step 1: Location Mapping
- Map location attributes to common geo/beats
- Use `pd_beats_datasd` shapefile for beat boundaries
- Standardize all sources to beat-level geography

### Step 2: Date Normalization
- Extract `month`, `quarter`, and `year` from date columns
- Standardize across all data sources
- **311 Data:** Use `date_closed` for closed requests, `date_requested` for open requests

### Step 3: Quality of Life Categorization
- Map event type columns (`dispo`, `service_name_detail`, `description`) to `cat_qual_life`
- Categories: **critical** or **non-critical**
- Use Claude API for intelligent categorization

### Step 4: Time Series Aggregation
- Aggregate counts separately for critical and non-critical events
- Group by beat, year, quarter, month

### Step 5: Quality of Life Scoring
| Weight | Category | Default |
|--------|----------|---------|
| `WEIGHT_CRITICAL` | Critical events | 0.7 |
| `WEIGHT_NON_CRITICAL` | Non-critical events | 0.3 |

**Weights are configurable.**

**QoL Score Calculation:**
- Compare neighborhood weighted counts to **city average weighted counts**
- `score = neighborhood_weighted_count / city_avg_weighted_count`

### Step 6: Final Output Schema

**Single JSON file:** `neighborhood_qol.json`

| Column | Type | Values |
|--------|------|--------|
| `beat` | string | Beat ID |
| `q_o_l_category` | string | `critical` / `non_critical` / `all` |
| `score` | float | QoL score vs city avg |
| `source` | string | Data source or `all_sources_combined` |
| `year` | int | 2018-2025 |
| `quarter` | int | 1-4 |
| `month` | int | 1-12 |

### Output Requirements
- **Time range:** Last 7 years only
- **Format:** JSON (for ArcGIS SDK time series)
- **Filters:** By `source`, `q_o_l_category`, `year`, `quarter`, `month`
- **Temporal analysis:** Supports animation/slider via time columns

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
