import os
import abc
import torch
import logging
import warnings
import transformers

from typing         import Any, Dict, List, Optional, Tuple

import pandas       as pd

# =================================== DOWNLOADS FOR LANGUAGE PROCESSING ===================================



# =================================== IGNORE CERTAIN ERRORS ===================================

transformers.logging.set_verbosity_error()
transformers.utils.logging.enable_progress_bar()

logging.disable(logging.WARNING)

# ================================= CONSTANTS DEFINITIONS =================================

SEQUENCE_MAX_LENGTH : int   = 512
SEQUENCE_TRUNCATION : bool  = True
SEQUENCE_PADDING    : str   = 'max_length'

FINAL_MODEL_SAVE    : str   = 'checkpoint-final'

# =================================== PRIVATE FUNCTIONS ===================================



# =================================== PUBLIC FUNCTIONS ===================================

def get_training_args(output_dir: str, logging_dir: str) -> transformers.TrainingArguments:
    training_args = transformers.TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        warmup_steps=500,
        weight_decay=0.01,
        logging_strategy='no',
        logging_dir=logging_dir,
        logging_steps=100,
        optim="adamw_torch",
        disable_tqdm=False
    )

    return training_args

def get_xlm_roberta_base() -> Tuple[transformers.AutoTokenizer, transformers.AutoModelForSequenceClassification]:
    tokenizer   : transformers.AutoTokenizer                        = transformers.AutoTokenizer.from_pretrained('xlm-roberta-base')
    model       : transformers.AutoModelForSequenceClassification   = transformers.AutoModelForSequenceClassification.from_pretrained("xlm-roberta-base", num_labels=2)

    return (tokenizer, model)

def get_xlm_roberta_large() -> Tuple[transformers.AutoTokenizer, transformers.AutoModelForSequenceClassification]:
    tokenizer   : transformers.AutoTokenizer                        = transformers.AutoTokenizer.from_pretrained('xlm-roberta-large')
    model       : transformers.AutoModelForSequenceClassification   = transformers.AutoModelForSequenceClassification.from_pretrained("xlm-roberta-large", num_labels=2)

    return (tokenizer, model)

# =================================== PRIVATE CLASS DEFINITIONS ===================================

class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class TransformerModel():

    def __init__(self, tokenizer: transformers.PreTrainedTokenizer, model: transformers.PreTrainedModel) -> None:
        self.tokenizer          : transformers.PreTrainedTokenizer  = tokenizer
        self.model              : transformers.PreTrainedModel      = model
        self.model_saved_path   : Optional[str]                     = None

    def train(self, train_texts: pd.Series, train_labels: pd.Series, training_args: transformers.TrainingArguments) -> transformers.Trainer:

        train_texts_lst     : List[str] = train_texts.to_list()
        train_labels_lst    : List[int] = train_labels.replace({ False: 0, True: 1 }, inplace=False).to_list()

        train_encodings : transformers.BatchEncoding    = self.tokenizer(text=train_texts_lst, max_length=SEQUENCE_MAX_LENGTH,
            truncation=SEQUENCE_TRUNCATION, padding=SEQUENCE_PADDING, return_tensors='pt')

        train_dataset   : Dataset               = Dataset(train_encodings, train_labels_lst)
        trainer         : transformers.Trainer  = transformers.Trainer(model=self.model, args=training_args, train_dataset=train_dataset)

        trainer.train()
        self.model_saved_path = os.path.join(training_args.output_dir, FINAL_MODEL_SAVE)
        trainer.save_model(self.model_saved_path)

    def load_saved_model(self):
        if self.model_saved_path is not None:
            self.model = transformers.AutoModelForSequenceClassification.from_pretrained(self.model_saved_path)

    def predict(self, test_texts: pd.Series) -> pd.DataFrame:

        test_texts_lst  : List[str] = test_texts.to_list()

        pipe = transformers.TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, return_all_scores=True,
            max_length=SEQUENCE_MAX_LENGTH, truncation=SEQUENCE_TRUNCATION, padding=SEQUENCE_PADDING)
        predictions = pipe(test_texts_lst)

        predictions_dict : Dict[str, Dict[str, float]] = {}
        for index, prediction in zip(test_texts.index.to_list(), predictions):
            predictions_dict[index] = {}

            for item in prediction:
                label   : str   = item['label']
                score   : float = item['score']

                predictions_dict[index][label] = score

        predictions_df  : pd.DataFrame  = pd.DataFrame.from_dict(predictions_dict, orient='index')
        columns         : List[str]     = predictions_df.columns.to_list()
        columns_fixed   : List[str]     = list(map(lambda column: column.replace('_', ' ').title(), columns))
        
        predictions_df.columns = columns_fixed

        return predictions_df

    def __del__(self):
        del self.model
        del self.tokenizer
