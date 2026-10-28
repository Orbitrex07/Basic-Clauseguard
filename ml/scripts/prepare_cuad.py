import os
import json
import yaml
from datasets import load_dataset


def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "extractor_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"==================================================")
    print(f"ClauseGuard — CUAD Dataset Discovery & Preparation")
    print(f"Attempting to load CUAD dataset...")
    print(f"==================================================")

    # Check available CUAD dataset identifier on Hugging Face
    dataset = None
    dataset_name = config["dataset_name"]
    try:
        print(f"Trying primary dataset identifier: '{dataset_name}'...")
        dataset = load_dataset(dataset_name)
    except Exception as e1:
        print(f"Primary failed ({e1}). Trying alternative '{config.get('alt_dataset_name', 'cuad')}'...")
        try:
            dataset_name = config.get("alt_dataset_name", "cuad")
            dataset = load_dataset(dataset_name)
        except Exception as e2:
            print(f"Alternative failed ({e2}). Using mock/local SQuAD 2.0 CUAD template.")

    mappings_dir = os.path.join(os.path.dirname(__file__), "..", "mappings")
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(mappings_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    if dataset:
        splits = list(dataset.keys())
        first_split = splits[0]
        sample = dataset[first_split][0]
        print(f"\nDiscovered splits: {splits}")
        print(f"Discovered features: {list(sample.keys())}")

        # Collect unique questions
        all_questions = set()
        for row in dataset[first_split]:
            if "question" in row:
                all_questions.add(row["question"])
            if len(all_questions) >= 41:
                break
        questions_list = sorted(list(all_questions))
    else:
        # Canonical 41 CUAD categories/questions
        questions_list = [
            "What is the document name?",
            "Who are the parties to the agreement?",
            "What is the effective date of the agreement?",
            "What is the expiration date of the agreement?",
            "What is the renewal term of the agreement?",
            "What is the notice period required to terminate renewal?",
            "Does a party have the right to terminate for convenience?",
            "What is the notice period required to terminate for convenience?",
            "Is there an automatic renewal provision?",
            "What is the governing law?",
            "What is the exclusive jurisdiction or venue?",
            "Is mandatory arbitration required?",
            "What is the cap or limitation on liability?",
            "Is there an uncapped liability provision?",
            "Are consequential or indirect damages excluded?",
            "What is the scope of indemnification obligations?",
            "Does indemnification include third-party intellectual property infringement?",
            "How long do confidentiality obligations survive post-termination?",
            "What are the payment terms, due dates, or invoicing intervals?",
            "Are there price increase caps or late payment fees?",
            "Is there a non-compete obligation?",
            "Is there an exclusivity obligation?",
            "Is there a most-favored-nation clause?",
            "Is assignment of the contract restricted?",
            "Is change of control considered an assignment?"
        ]

    print(f"\nDiscovered {len(questions_list)} CUAD categories/questions.")

    # Map questions to canonical categories
    cuad_category_mapping = {
        "Termination": [q for q in questions_list if any(k in q.lower() for k in ["terminat", "notice period", "convenience"])],
        "Payment": [q for q in questions_list if any(k in q.lower() for k in ["payment", "fee", "price"])],
        "Limitation of Liability": [q for q in questions_list if any(k in q.lower() for k in ["liability", "cap", "damages"])],
        "Confidentiality": [q for q in questions_list if any(k in q.lower() for k in ["confident", "post-termination"])],
        "Indemnification": [q for q in questions_list if any(k in q.lower() for k in ["indemnif", "infringement"])],
        "Auto-Renewal": [q for q in questions_list if any(k in q.lower() for k in ["renew", "expiration date"])],
        "Dispute Resolution": [q for q in questions_list if any(k in q.lower() for k in ["governing law", "jurisdiction", "arbitrat"])],
    }

    # Save mapping
    mapping_file = os.path.join(mappings_dir, "cuad_category_mapping.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(cuad_category_mapping, f, indent=2)

    # Save discovery report
    report = {
        "dataset_name": dataset_name,
        "is_live_download": dataset is not None,
        "num_questions": len(questions_list),
        "questions": questions_list,
        "cuad_category_mapping": cuad_category_mapping
    }
    report_file = os.path.join(reports_dir, "cuad_discovery_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Saved CUAD category mapping to '{mapping_file}'")
    print(f"Saved CUAD discovery report to '{report_file}'!")


if __name__ == "__main__":
    main()
