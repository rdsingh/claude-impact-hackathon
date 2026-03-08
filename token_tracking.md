# Token Usage Tracking

## Phase 1: Research & Planning
| Model | Tasks | Est. Input Tokens | Est. Output Tokens |
|-------|-------|-------------------|-------------------|
| claude-opus-4-6 | Initial scaffolding, data exploration, requirements docs, CLAUDE.md | ~25,000 | ~8,000 |

---

## Phase 2: Engineering
| Model | Tasks | Est. Input Tokens | Est. Output Tokens |
|-------|-------|-------------------|-------------------|
| claude-sonnet-4-6 | Data pipeline scripts, MCP server, REST API, frontend, ESRI integration | ~80,000 | ~25,000 |

---

## Phase 3: Testing
| Model | Tasks | Est. Input Tokens | Est. Output Tokens |
|-------|-------|-------------------|-------------------|
| claude-opus-4-6 | Test suite creation (30 tests), test execution, test plan documentation | ~40,000 | ~12,000 |

---

## Phase 4: Demo & Presentation
| Model | Tasks | Est. Input Tokens | Est. Output Tokens |
|-------|-------|-------------------|-------------------|
| claude-opus-4-6 | Product metrics, presentation slides, token tracking, context refinement | ~50,000 | ~15,000 |

---

## Grand Total
| Phase | Model | Input Tokens | Output Tokens | Est. Cost |
|-------|-------|-------------|---------------|-----------|
| 1 — Research | claude-opus-4-6 | ~25,000 | ~8,000 | ~$0.60 |
| 2 — Engineering | claude-sonnet-4-6 | ~80,000 | ~25,000 | ~$1.00 |
| 3 — Testing | claude-opus-4-6 | ~40,000 | ~12,000 | ~$1.20 |
| 4 — Demo | claude-opus-4-6 | ~50,000 | ~15,000 | ~$1.50 |
| **Total** | | **~195,000** | **~60,000** | **~$4.30** |

## Sustainability Narrative

This project demonstrates that AI-powered development infrastructure can deliver a full-stack civic data application — data pipeline, MCP server, REST API, interactive map frontend, and comprehensive test suite — for under $5 in AI token costs.

Key efficiency strategies:
- **Phase-appropriate model selection**: Used Opus for research/testing (where accuracy matters most) and Sonnet for engineering (where volume of code generation matters most)
- **Context file discipline**: CLAUDE.md provided persistent project context across sessions, reducing redundant token usage
- **Parallel tool execution**: Concurrent file reads, writes, and agent spawning minimized round-trips
- **Pre-processed data**: Running data pipeline once and caching results eliminated repeated expensive data processing

At ~$4.30 total for a complete application processing 6M+ civic records across 135 neighborhoods over 8 years, this approach is economically viable for civic organizations with limited budgets.
