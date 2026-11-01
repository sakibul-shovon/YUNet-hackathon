# ClaimCraft BD — Evaluation and Ablation Benchmark Report

- **Release ID:** `rel_2026_03_active_v1`
- **Manifest Version:** `1.0`
- **Timestamp:** `2026-11-01T09:05:36Z`

---

## 1. Routing & Procedural Assessment Benchmark (96 Families)
| Metric | Full System | Ablation (No Policy Gate) | Delta |
|---|---|---|---|
| **Overall Route Accuracy** | **93.8%** | 85.4% | +8.3% |
| **Appropriate Abstention Rate** | **100.0%** | 0.0% | +100.0% |
| **Safety Hazard Recall** | **100.0%** | 100.0% | 0.0% |
| **Safety Hazard Precision** | **100.0%** | 100.0% | 0.0% |
| **P50 Latency** | `0.0 ms` | `0.0 ms` | — |
| **P95 Latency** | `0.01 ms` | `0.02 ms` | — |

> **Key Takeaway:** The deterministic Kleene policy gate completely eliminates false jurisdiction routing on out-of-scope/speculative cases, raising appropriate abstention from 0.0% to 100.0%.

---

## 2. Evidence Conflict Detection Benchmark (30 Sets)
| Metric | Full System (Gated) | Ablation (No Gate) |
|---|---|---|
| **Conflict Precision** | **100.0%** | 0.0% |
| **Conflict Recall** | **100.0%** | 0.0% |
| **Conflict F1** | **100.0%** | 0.0% |

> **Key Takeaway:** Unchecked evidence ingestion misses 100% of receipt-narration fee discrepancies (T21), risking flawed legal notices.

---

## 3. Statutory Provision Retrieval Benchmark (60 Queries)
| Metric | Full System (Hybrid RRF) | Ablation (Dense-Only) | Delta |
|---|---|---|---|
| **Recall@1** | **100.0%** | 66.7% | +33.3% |
| **Recall@5** | **100.0%** | 100.0% | 0.0% |
| **Recall@10** | **100.0%** | 100.0% | 0.0% |
| **MRR** | **1.0000** | 0.7778 | +0.2222 |

> **Key Takeaway:** Hybrid Reciprocal Rank Fusion (RRF) preserves exact statutory section retrieval in Banglish queries where pure dense embeddings degrade.
