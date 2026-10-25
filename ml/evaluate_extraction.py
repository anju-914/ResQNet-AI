import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.api.app.services.extraction_service import extract_sos_entities

def run_evaluation():
    eval_file = BASE_DIR / "ml" / "extraction" / "eval_dataset.json"
    if not eval_file.exists():
        print(f"Error: {eval_file} not found")
        return

    with open(eval_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    print(f"--- Running ResQNet AI NLP Extraction Benchmark on {total} Samples ---")

    correct_lang = 0
    correct_need = 0
    correct_people = 0
    people_evaluated = 0
    correct_location = 0
    location_evaluated = 0
    correct_spam = 0

    latencies = []

    for item in dataset:
        text = item["text"]
        expected = item["expected"]

        start_time = time.perf_counter()
        result = extract_sos_entities(text)
        duration_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(duration_ms)

        # Check language
        if result.language.lower() == expected["language"].lower():
            correct_lang += 1

        # Check spam classification
        is_spam_predicted = result.spam_score >= 0.8
        if is_spam_predicted == expected["is_spam"]:
            correct_spam += 1

        # Only evaluate need, people, location if not expected spam
        if not expected["is_spam"]:
            # Need type
            if result.need_type.lower() == expected["need_type"].lower():
                correct_need += 1

            # People count
            people_evaluated += 1
            if result.people_count == expected["people_count"]:
                correct_people += 1

            # Location text
            location_evaluated += 1
            exp_loc = (expected["location_text"] or "").lower()
            pred_loc = (result.location_text or "").lower()
            if exp_loc in pred_loc or pred_loc in exp_loc:
                correct_location += 1

    valid_non_spam = total - sum(1 for d in dataset if d["expected"]["is_spam"])
    
    lang_acc = (correct_lang / total) * 100
    spam_acc = (correct_spam / total) * 100
    need_acc = (correct_need / valid_non_spam) * 100 if valid_non_spam else 0
    people_acc = (correct_people / people_evaluated) * 100 if people_evaluated else 0
    loc_acc = (correct_location / location_evaluated) * 100 if location_evaluated else 0
    avg_latency = sum(latencies) / len(latencies)

    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Test Messages:        {total}")
    print(f"Average Extraction Latency: {avg_latency:.2f} ms")
    print(f"Language Detection Acc:     {lang_acc:.1f}% ({correct_lang}/{total})")
    print(f"Spam Filter Precision:      {spam_acc:.1f}% ({correct_spam}/{total})")
    print(f"Need Type Accuracy:         {need_acc:.1f}% ({correct_need}/{valid_non_spam})")
    print(f"People Count Accuracy:      {people_acc:.1f}% ({correct_people}/{people_evaluated})")
    print(f"Location Extraction Acc:    {loc_acc:.1f}% ({correct_location}/{location_evaluated})")
    print("===================================================\n")

    if "--verbose" in sys.argv:
        for item in dataset:
            text = item["text"]
            exp = item["expected"]
            res = extract_sos_entities(text)
            if not exp["is_spam"]:
                exp_loc = (exp["location_text"] or "").lower()
                pred_loc = (res.location_text or "").lower()
                if exp_loc not in pred_loc and pred_loc not in exp_loc:
                    print(f"[LOC FAIL] ID={item['id']} Expected='{exp['location_text']}' Got='{res.location_text}' Text='{text}'")
                if res.people_count != exp["people_count"]:
                    print(f"[PEOPLE FAIL] ID={item['id']} Expected={exp['people_count']} Got={res.people_count} Text='{text}'")

    return {
        "total": total,
        "avg_latency_ms": round(avg_latency, 2),
        "language_acc": round(lang_acc, 1),
        "spam_acc": round(spam_acc, 1),
        "need_acc": round(need_acc, 1),
        "people_acc": round(people_acc, 1),
        "location_acc": round(loc_acc, 1)
    }

if __name__ == "__main__":
    run_evaluation()
