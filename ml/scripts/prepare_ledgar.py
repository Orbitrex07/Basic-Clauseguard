import os
import json
import yaml
import re
from datasets import load_dataset


def map_source_label_to_canonical(source_label: str) -> str:
    lbl = source_label.lower()
    
    # 1. Termination
    if any(k in lbl for k in ["terminat", "cancellation", "end of term", "expiration"]):
        return "Termination"
    
    # 2. Payment
    if any(k in lbl for k in ["payment", "fee", "expense", "compensation", "billing", "invoic", "tax", "price"]):
        return "Payment"
    
    # 3. Limitation of Liability
    if any(k in lbl for k in ["liabilit", "remed", "warrant", "damages"]):
        return "Limitation of Liability"
    
    # 4. Confidentiality
    if any(k in lbl for k in ["confident", "non-disclosure", "nondisclosure", "proprietary", "secrecy"]):
        return "Confidentiality"
    
    # 5. Indemnification
    if any(k in lbl for k in ["indemnif", "indemnity", "defend", "hold harmless"]):
        return "Indemnification"
    
    # 6. Auto-Renewal
    if any(k in lbl for k in ["renew", "extension of term", "automatic"]):
        return "Auto-Renewal"
    
    # 7. Dispute Resolution
    if any(k in lbl for k in ["governing law", "law", "jurisdiction", "arbitrat", "venue", "dispute", "litigat", "court"]):
        return "Dispute Resolution"
    
    # 8. Remaining labels
    return "Other"


def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "classifier_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"==================================================")
    print(f"ClauseGuard — LEDGAR Dataset Discovery & Preparation")
    print(f"Loading dataset: {config['dataset_name']} ({config['dataset_config']})...")
    print(f"==================================================")

    dataset = load_dataset(config["dataset_name"], config["dataset_config"])

    print("\n--- Discovered Splits ---")
    splits = list(dataset.keys())
    for s in splits:
        print(f"Split '{s}': {len(dataset[s])} samples")

    print("\n--- Discovered Features ---")
    features = dataset[splits[0]].features
    print(features)

    label_feature = features["label"]
    names = label_feature.names if hasattr(label_feature, "names") else []
    print(f"\nDiscovered {len(names)} unique source labels in LEDGAR.")

    label2id = {name: idx for idx, name in enumerate(names)}
    id2label = {idx: name for idx, name in enumerate(names)}

    taxonomy_mapping = {}
    canonical_counts = {}
    for name in names:
        canon = map_source_label_to_canonical(name)
        taxonomy_mapping[name] = canon
        canonical_counts[canon] = canonical_counts.get(canon, 0) + 1

    print("\n--- Generated Canonical Taxonomy Distribution ---")
    for cat, count in sorted(canonical_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} source labels mapped")

    # Ensure output directories exist
    mappings_dir = os.path.join(os.path.dirname(__file__), "..", "mappings")
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(mappings_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # Save mappings
    with open(os.path.join(mappings_dir, "label2id.json"), "w", encoding="utf-8") as f:
        json.dump(label2id, f, indent=2)

    with open(os.path.join(mappings_dir, "id2label.json"), "w", encoding="utf-8") as f:
        json.dump(id2label, f, indent=2)

    with open(os.path.join(mappings_dir, "taxonomy_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(taxonomy_mapping, f, indent=2)

    # Save discovery report
    report = {
        "dataset_name": config["dataset_name"],
        "dataset_config": config["dataset_config"],
        "splits": {s: len(dataset[s]) for s in splits},
        "num_source_labels": len(names),
        "canonical_distribution": canonical_counts,
        "sample_text": dataset["train"][0]["text"][:200]
    }
    with open(os.path.join(reports_dir, "ledgar_discovery_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nSuccessfully saved mappings to '{mappings_dir}' and discovery report to '{reports_dir}'!")


if __name__ == "__main__":
    main()
