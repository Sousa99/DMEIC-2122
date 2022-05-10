import abc
import torch
import warnings
import transformers

from typing         import Any, List, Optional, Tuple

import pandas       as pd

# =================================== DOWNLOADS FOR LANGUAGE PROCESSING ===================================



# =================================== IGNORE CERTAIN ERRORS ===================================



# =================================== PRIVATE FUNCTIONS ===================================



# =================================== PUBLIC FUNCTIONS ===================================

def get_training_args(output_dir: str, logging_dir: str) -> transformers.TrainingArguments:
    training_args = transformers.TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=logging_dir,
        logging_steps=100,
    )

    return training_args

def get_xlm_roberta_base() -> Tuple[transformers.AutoTokenizer, transformers.AutoModelForSequenceClassification]:
    tokenizer   : transformers.AutoTokenizer                        = transformers.AutoTokenizer.from_pretrained('xlm-roberta-base')
    model       : transformers.AutoModelForSequenceClassification   = transformers.AutoModelForSequenceClassification.from_pretrained("xlm-roberta-base", num_labels=2)

    return (tokenizer, model)

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class TransformerModel():

    def __init__(self, tokenizer: transformers.PreTrainedTokenizer, model: transformers.PreTrainedModel) -> None:
        self.tokenizer  : transformers.PreTrainedTokenizer  = tokenizer
        self.model      : transformers.PreTrainedModel      = model

    def train(self, train_texts: pd.Series, train_labels: pd.Series, training_args: transformers.TrainingArguments):

        train_texts_lst     : List[str] = train_texts.to_list()
        train_labels_lst    : List[int] = train_labels.replace({ False: 0, True: 1 }, inplace=False).to_list()

        train_encodings : transformers.BatchEncoding    = self.tokenizer(text=train_texts_lst, max_length=200, truncation=True, padding=True, return_tensors='pt')

        train_dataset   : Dataset               = Dataset(train_encodings, train_labels_lst)
        trainer         : transformers.Trainer  = transformers.Trainer(model=self.model, args=training_args, train_dataset=train_dataset)

        trainer.train()