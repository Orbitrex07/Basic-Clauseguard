import os
import json
import yaml
import argparse
import numpy as np
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    EarlyStoppingCallback
)
import evaluate


def compute_metrics_fn(eval_pred):
    accuracy_metric = evaluate.load("accuracy")
    f1_metric = evaluate.load("f1")

    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    acc = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
    micro_f1 = f1_metric.compute(predictions=preds, references=labels, average="micro")["f1"]
    macro_f1 = f1_metric.compute(predictions=preds, references=labels, average="macro")["f1"]

    return {
        "accuracy": acc,
        "micro_f1": micro_f1,
        "macro_f1": macro_f1
    }


def main():
    parser = argparse.ArgumentParser(description="Train Legal-BERT Classifier on LEDGAR")
    parser.add_argument("--epochs", type=int, default=None, help="Override epochs")
    parser.add_argument("--subset", type=int, default=None, help="Train on smaller subset for quick benchmark")
    parser.add_argument("--dry_run", action="store_true", help="Perform 1-step validation run")
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "classifier_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    epochs = args.epochs or config["num_train_epochs"]
    mappings_dir = os.path.join(os.path.dirname(__file__), "..", "mappings")
    label2id_path = os.path.join(mappings_dir, "label2id.json")
    id2label_path = os.path.join(mappings_dir, "id2label.json")

    with open(label2id_path, "r", encoding="utf-8") as f:
        label2id = json.load(f)
    with open(id2label_path, "r", encoding="utf-8") as f:
        id2label = {int(k): v for k, v in json.load(f).items()}

    num_labels = len(label2id)
    print(f"Loaded {num_labels} labels dynamically from label2id.json.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device} (CUDA available: {torch.cuda.is_available()})")

    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])

    print(f"Loading dataset {config['dataset_name']} ({config['dataset_config']})...")
    raw_datasets = load_dataset(config["dataset_name"], config["dataset_config"])

    def tokenize_fn(examples):
        return tokenizer(examples["text"], truncation=True, max_length=config["max_seq_length"])

    if args.subset:
        train_ds = raw_datasets["train"].select(range(args.subset))
        val_ds = raw_datasets["validation"].select(range(min(len(raw_datasets["validation"]), args.subset // 2)))
        test_ds = raw_datasets["test"].select(range(min(len(raw_datasets["test"]), args.subset // 2)))
    else:
        train_ds = raw_datasets["train"]
        val_ds = raw_datasets["validation"]
        test_ds = raw_datasets["test"]

    print("Tokenizing datasets...")
    tokenized_train = train_ds.map(tokenize_fn, batched=True)
    tokenized_val = val_ds.map(tokenize_fn, batched=True)
    tokenized_test = test_ds.map(tokenize_fn, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        config["model_name"],
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )

    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", config["output_dir"])
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=float(config["learning_rate"]),
        per_device_train_batch_size=config["batch_size"],
        per_device_eval_batch_size=config["eval_batch_size"],
        num_train_epochs=epochs if not args.dry_run else 1,
        weight_decay=float(config["weight_decay"]),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        warmup_ratio=float(config["warmup_ratio"]),
        fp16=torch.cuda.is_available() and config.get("use_fp16", True),
        logging_steps=50,
        max_steps=5 if args.dry_run else -1,
        save_total_limit=2,
        seed=config["seed"]
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics_fn,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    print("Starting classifier fine-tuning...")
    trainer.train()

    print("\nEvaluating on test split...")
    eval_results = trainer.evaluate(eval_dataset=tokenized_test)
    print("Test split evaluation metrics:")
    for k, v in eval_results.items():
        print(f"  {k}: {v}")

    # Save model and tokenizer
    print(f"\nSaving fine-tuned classifier to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    with open(os.path.join(output_dir, "label2id.json"), "w", encoding="utf-8") as f:
        json.dump(label2id, f, indent=2)
    with open(os.path.join(output_dir, "id2label.json"), "w", encoding="utf-8") as f:
        json.dump(id2label, f, indent=2)

    # Save evaluation report
    report_file = os.path.join(reports_dir, "classifier_eval_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print(f"Classifier saved successfully to {output_dir} and report to {report_file}!")


if __name__ == "__main__":
    main()
