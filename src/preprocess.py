import os
import re
from datasets import load_dataset
from transformers import T5Tokenizer
from tqdm import tqdm

# ── Config ─────────────────────────────────────────────
MODEL_NAME   = "t5-small"          # pretrained model we'll fine-tune
MAX_INPUT    = 512                  # max tokens for input article
MAX_TARGET   = 128                  # max tokens for summary
SAVE_DIR     = "data/processed"    # where to save tokenized data
SAMPLE_SIZE  = 10000               # use subset to train faster

# ── Load tokenizer ─────────────────────────────────────
print("Loading T5 tokenizer...")
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

# ── Text cleaning ──────────────────────────────────────
def clean_text(text: str) -> str:
    """Remove noise from lecture/article text."""
    text = re.sub(r'\s+', ' ', text)          # collapse whitespace
    text = re.sub(r'\[.*?\]', '', text)       # remove [brackets]
    text = re.sub(r'http\S+', '', text)       # remove URLs
    text = text.strip()
    return text

# ── Tokenize one example ───────────────────────────────
def tokenize_example(example):
    # T5 needs "summarize: " prefix for summarization task
    input_text  = "summarize: " + clean_text(example["article"])
    target_text = clean_text(example["highlights"])

    model_inputs = tokenizer(
        input_text,
        max_length=MAX_INPUT,
        padding="max_length",
        truncation=True,
    )
    labels = tokenizer(
        target_text,
        max_length=MAX_TARGET,
        padding="max_length",
        truncation=True,
    )

    # Replace padding token id in labels with -100
    # so loss ignores padding positions
    model_inputs["labels"] = [
        (l if l != tokenizer.pad_token_id else -100)
        for l in labels["input_ids"]
    ]
    return model_inputs

# ── Main ───────────────────────────────────────────────
if __name__ == "__main__":

    # 1. Load CNN/DailyMail dataset from HuggingFace
    print("Downloading CNN/DailyMail dataset...")
    dataset = load_dataset("cnn_dailymail", "3.0.0")

    # 2. Take a smaller sample for faster training
    train_data = dataset["train"].select(range(SAMPLE_SIZE))
    val_data   = dataset["validation"].select(range(500))

    print(f"Train samples : {len(train_data)}")
    print(f"Val   samples : {len(val_data)}")

    # 3. Tokenize the dataset
    print("Tokenizing...")
    tokenized_train = train_data.map(tokenize_example, batched=False)
    tokenized_val   = val_data.map(tokenize_example,   batched=False)

    # 4. Save to disk
    os.makedirs(SAVE_DIR, exist_ok=True)
    tokenized_train.save_to_disk(f"{SAVE_DIR}/train")
    tokenized_val.save_to_disk(f"{SAVE_DIR}/val")
    tokenizer.save_pretrained(f"{SAVE_DIR}/tokenizer")

    print("✅ Phase 1 complete! Data saved to data/processed/")

    # 5. Quick sanity check
    sample = tokenized_train[0]
    print("\n── Sample check ──")
    print("Input IDs shape  :", len(sample["input_ids"]))
    print("Labels shape     :", len(sample["labels"]))
    decoded = tokenizer.decode(
        [l for l in sample["labels"] if l != -100],
        skip_special_tokens=True
    )
    print("Sample summary   :", decoded[:120], "...")