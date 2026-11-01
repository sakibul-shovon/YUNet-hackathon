"""Evaluation Metrics and Benchmark Calculators for ClaimCraft BD.

Calculates:
- Routing accuracy, multi-label precision/recall, and appropriate abstention
- Urgent safety hazard alert precision and recall
- Conflict detection precision and recall
- Retrieval Recall@1, Recall@5, Recall@10, and MRR
- Failure case collector for reproducible error analysis
"""

from typing import Any

class EvaluationMetrics:
    @staticmethod
    def calculate_routing_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {}

        correct_routes = 0
        abstentions_expected = 0
        abstentions_correct = 0
        safety_expected = 0
        safety_detected = 0
        safety_false_alarms = 0
        failures = []

        for r in results:
            gold_routes = {ar["route_id"] for ar in r["expected_acceptable_routes"]}
            pred_routes = {pr["route_id"] for pr in r.get("predicted_routes", []) if pr.get("status") in ("supported", "needs_facts")}
            
            is_unsupported = len(gold_routes) == 0
            if is_unsupported:
                abstentions_expected += 1
                if len(pred_routes) == 0 or r.get("abstained", False):
                    abstentions_correct += 1
                    correct_routes += 1
                else:
                    failures.append({
                        "case_id": r["case_id"],
                        "issue": "Failed to abstain on unsupported scenario",
                        "predicted_routes": list(pred_routes)
                    })
            else:
                if gold_routes.intersection(pred_routes) or (len(gold_routes) == 0 and len(pred_routes) == 0):
                    correct_routes += 1
                else:
                    failures.append({
                        "case_id": r["case_id"],
                        "issue": "Route mismatch",
                        "gold": list(gold_routes),
                        "predicted": list(pred_routes)
                    })

            # Safety check
            if r.get("is_safety_hazard"):
                safety_expected += 1
                if r.get("safety_alert_triggered"):
                    safety_detected += 1
                else:
                    failures.append({
                        "case_id": r["case_id"],
                        "issue": "Safety alert missed on hazardous scenario"
                    })
            else:
                if r.get("safety_alert_triggered"):
                    safety_false_alarms += 1

        route_accuracy = correct_routes / total
        abstention_rate = abstentions_correct / max(1, abstentions_expected)
        safety_recall = safety_detected / max(1, safety_expected)
        safety_precision = safety_detected / max(1, safety_detected + safety_false_alarms)

        return {
            "total_evaluated": total,
            "overall_route_accuracy": round(route_accuracy, 4),
            "appropriate_abstention_rate": round(abstention_rate, 4),
            "safety_hazard_recall": round(safety_recall, 4),
            "safety_hazard_precision": round(safety_precision, 4),
            "failure_count": len(failures),
            "sample_failures": failures[:5]
        }

    @staticmethod
    def calculate_conflict_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {}

        tp = 0
        fp = 0
        fn = 0
        tn = 0
        failures = []

        for r in results:
            expected = r["is_conflict_present"]
            predicted = r["conflict_detected"]
            if expected and predicted:
                tp += 1
            elif not expected and predicted:
                fp += 1
                failures.append({"id": r["id"], "type": "False Positive Conflict"})
            elif expected and not predicted:
                fn += 1
                failures.append({"id": r["id"], "type": "False Negative Missed Conflict"})
            else:
                tn += 1

        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * (precision * recall) / max(1e-6, precision + recall)

        return {
            "total_evaluated": total,
            "conflict_precision": round(precision, 4),
            "conflict_recall": round(recall, 4),
            "conflict_f1": round(f1, 4),
            "failures": failures
        }

    @staticmethod
    def calculate_retrieval_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {}

        recalls_at_1 = 0
        recalls_at_5 = 0
        recalls_at_10 = 0
        rr_sum = 0.0

        for r in results:
            target = r["target_provision_id"]
            ranked_ids = r["ranked_provision_ids"]
            
            if target in ranked_ids[:1]:
                recalls_at_1 += 1
            if target in ranked_ids[:5]:
                recalls_at_5 += 1
            if target in ranked_ids[:10]:
                recalls_at_10 += 1

            if target in ranked_ids:
                rank = ranked_ids.index(target) + 1
                rr_sum += 1.0 / rank

        return {
            "total_queries": total,
            "recall_at_1": round(recalls_at_1 / total, 4),
            "recall_at_5": round(recalls_at_5 / total, 4),
            "recall_at_10": round(recalls_at_10 / total, 4),
            "mrr": round(rr_sum / total, 4)
        }
