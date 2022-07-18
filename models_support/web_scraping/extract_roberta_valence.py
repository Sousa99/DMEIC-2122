import os
import sys
import json
import torch
import argparse
import transformers

import pandas   as pd

from tqdm       import tqdm
from typing     import Dict, List, Optional, Tuple

# =============================??????????????????????????????????====== PACKAGES PARAMETERS ============??????????????????????????????????=======================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

COLUMN_METADATA         : str       = 'metadata'
COLUMN_TEXT             : str       = 'text'
COLUMN_VALENCE          : str       = 'valence'

LOAD_METADATA_EXTRACT   : List[str] = ['scraper']
LOAD_DROP_COLUMNS       : List[str] = ['metadata']

PREPROCESS_TEXT         : bool      = True

SEQUENCE_MAX_LENGTH     : int       = 512
SEQUENCE_TRUNCATION     : bool      = True
SEQUENCE_PADDING        : str       = 'max_length'

EXPORTS_DIRECTORY       : str       = '../exports/web_scraping'
FINAL_MODEL_SAVE        : str       = f'{EXPORTS_DIRECTORY}/valence_roberta'
ROBERTA_OUTPUT_DIR      : str       = f'{EXPORTS_DIRECTORY}/valence_roberta_outputs/'
ROBERTA_LOGGING_DIR     : str       = f'{EXPORTS_DIRECTORY}/valence_roberta_logging/'

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-files", nargs='+', required=True, help="paths to extracted valence sets")
# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

def preprocess_datafram(dataframe: pd.DataFrame) -> pd.DataFrame:
    for metadata_key in LOAD_METADATA_EXTRACT:
        dataframe[metadata_key] = dataframe[COLUMN_METADATA].progress_apply(lambda metadata: metadata[metadata_key])
    dataframe.drop(LOAD_DROP_COLUMNS, axis=1, errors='ignore', inplace=True)
    return dataframe

def preprocess_text(text: str) -> str:
    if PREPROCESS_TEXT: text = text.lower()
    # TODO: Remove non alphanumeric characthers
    return text

def get_training_args(output_dir: str, logging_dir: str) -> transformers.TrainingArguments:
    training_args = transformers.TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_strategy='no',
        logging_dir=logging_dir,
        logging_steps=100,
        optim="adamw_torch",
        disable_tqdm=True
    )

    return training_args

def get_xlm_roberta_large() -> Tuple[transformers.AutoTokenizer, transformers.AutoModelForSequenceClassification]:
    tokenizer   : transformers.AutoTokenizer                        = transformers.AutoTokenizer.from_pretrained('xlm-roberta-large')
    model       : transformers.AutoModelForSequenceClassification   = transformers.AutoModelForSequenceClassification.from_pretrained("xlm-roberta-large", num_labels=2)

    return (tokenizer, model)

# ========================================================================= AUX CLASSES =========================================================================

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

    def __del__(self):
        del self.model
        del self.tokenizer

# ======================================================================== MAIN EXECUTION ========================================================================

# Load various extracted information into dataframes
dataframes : List[pd.DataFrame] = []
for path_to_extracted in arguments.files:
    if not os.path.exists(path_to_extracted) or not os.path.isfile(path_to_extracted):
        exit(f"🚨 File '{path_to_extracted}' does not exist, and should exist")

    file = open(path_to_extracted, 'r')
    information_extracted = json.load(file)
    file.close()

    # Deal with dataframe and quick preprocessing
    dataframe : pd.DataFrame = pd.DataFrame(information_extracted)
    dataframe = preprocess_datafram(dataframe)
    dataframes.append(dataframe)

# Get final dataframe with all the information concatenated
final_dataframe : pd.DataFrame = pd.concat(dataframes)
# Preprocess text
final_dataframe[COLUMN_TEXT] = final_dataframe[COLUMN_TEXT].progress_apply(lambda text: preprocess_text(text))

# Get basic structures for model development
training_args           = get_training_args(output_dir, logging_dir)
tokenizer, model_base   = get_xlm_roberta_large()
# Get model
model : TransformerModel = TransformerModel(tokenizer, model_base)
# Develop model
old_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
model.train(final_dataframe[COLUMN_TEXT], final_dataframe[COLUMN_VALENCE], training_args)
sys.stdout = old_stdout