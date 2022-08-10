import os
import sys
import json
import torch
import pandas
import stanza
import argparse
import warnings
import transformers

import numpy                as np
import pandas               as pd
import seaborn              as sns
import matplotlib           as mpl
import matplotlib.pyplot    as plt

from tqdm       import tqdm
from typing     import Any, Dict, List, Optional, Tuple
from langdetect import detect

# ============================================================== PACKAGES PARAMETERS AND VARIABLES ==============================================================

tqdm.pandas(desc='🐼 Pandas DataFrame apply', mininterval=0.1, maxinterval=10.0, leave=False)
stanza_pipeline = stanza.Pipeline('pt', processors='tokenize,mwt,pos', verbose=False)

# ======================================================================= NLTK DOWNLOADS  =======================================================================

'''
stanza.download('pt')
print()
'''

# ===================================================================== OMMIT SOME WARNINGS =====================================================================

mpl.set_loglevel("error")
warnings.filterwarnings('ignore', module = 'stanza')

# ======================================================== CONSTANTS DEFINITION AND ASSOCIATED FUNCTIONS ========================================================

COLUMN_METADATA                 : str                       = 'metadata'
COLUMN_TEXT                     : str                       = 'text'
COLUMN_VALENCE                  : str                       = 'valence'

LOAD_METADATA_EXTRACT           : Dict[str, List[str]]      = { 'scraper': ['scraper'], 'review_date': ['review_date'], 'reviewer': ['reviewer'],
                                                                'title': ['hotel_name', 'movie_title', 'clothe_title', 'company_name']}
LOAD_DROP_COLUMNS               : List[str]                 = ['metadata']
DROP_COLUMNS                    : List[str]                 = ['review_date', 'reviewer', 'title']

PREPROCESS_TEXT                 : bool                      = True

SEQUENCE_MAX_LENGTH             : int                       = 512
SEQUENCE_TRUNCATION             : bool                      = True
SEQUENCE_PADDING                : str                       = 'max_length'

EXPORTS_DIRECTORY               : str                       = '../exports/web_scraping/results'
GRAPHS_DIRECTORY                : str                       = f'{EXPORTS_DIRECTORY}/graphs'

FINAL_DATAFRAME_SAVE            : str                       = f'{EXPORTS_DIRECTORY}/extracted_full.csv'
FINAL_FILTERED_DATAFRAME_SAVE   : str                       = f'{EXPORTS_DIRECTORY}/extracted_full_filtered.csv'

FINAL_MODEL_SAVE                : str                       = f'{EXPORTS_DIRECTORY}/valence_roberta'
ROBERTA_OUTPUT_DIR              : str                       = f'{EXPORTS_DIRECTORY}/valence_roberta_outputs/'
ROBERTA_LOGGING_DIR             : str                       = f'{EXPORTS_DIRECTORY}/valence_roberta_logging/'

# ======================================================================== GET ARGUMENTS ========================================================================

# Define Parser
parser = argparse.ArgumentParser()
# Define Arguments
parser.add_argument("-files", nargs='+', required=True, help="paths to extracted valence sets")
# Get Arguments and Map to Requirements
arguments = parser.parse_args()

# ========================================================================= AUX FUNCTIONS =========================================================================

def preprocess_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:

    def get_if_any(metadata: Dict[str, Any], check_attributes: List[str]) -> str:
        current_value : str = ''
        for attribute in check_attributes:
            if attribute in metadata:
                current_value = metadata[attribute]
        return current_value

    for metadata_save in LOAD_METADATA_EXTRACT:
        metadata_columns = LOAD_METADATA_EXTRACT[metadata_save]
        dataframe[metadata_save] = dataframe[COLUMN_METADATA].progress_apply(lambda metadata: get_if_any(metadata, metadata_columns))
    
    dataframe.drop(LOAD_DROP_COLUMNS, axis=1, errors='ignore', inplace=True)
    return dataframe

def is_portuguese(text: str) -> str:
    try:
        if detect(text) == 'pt': return 'Yes'
        else: return 'No'
    except: return 'Inconclusive'

def preprocess_text(text: str) -> str:

    preprocessed_text = stanza_pipeline(text)
    text_without_ponctuation = []
    for sentence in preprocessed_text.sentences:
        for token in sentence.words:
            if token.upos != 'PUNCT':
                text_without_ponctuation.append(token.text)

    text_lowered = ' '.join(text_without_ponctuation).lower()
    return text_lowered

def export_count_plot(path: str, dataframe: pd.DataFrame, x_key: str, hue_key: Optional[str] = None,
    x_label: Optional[str] = None, y_label: Optional[str] = None, font_scale: float = 1.0):

    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=font_scale)

    plt.figure()
    plot = sns.countplot(data=dataframe, x=x_key, hue=hue_key)
    for container in plot.containers: plot.bar_label(container)
    
    if x_label is not None: plt.xlabel(x_label)
    if y_label is not None: plt.ylabel(y_label)
    
    plt.tight_layout()
    plt.savefig(path)
    plt.close('all')

def export_kde_plot(path: str, dataframe: pd.DataFrame, x_key: str, hue_key: Optional[str] = None,
    x_label: Optional[str] = None, y_label: Optional[str] = None, font_scale: float = 1.0):

    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=font_scale)

    plt.figure()
    sns.kdeplot(data=dataframe, x=x_key, hue=hue_key)
    
    if x_label is not None: plt.xlabel(x_label)
    if y_label is not None: plt.ylabel(y_label)
    
    plt.tight_layout()
    plt.savefig(path)
    plt.close('all')

def export_violin_scatter_plot(path: str, dataframe: pd.DataFrame, x_key: str, y_key: str, hue_key: Optional[str] = None,
    x_label: Optional[str] = None, y_label: Optional[str] = None, font_scale: float = 1.0):

    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=font_scale)

    plt.figure()
    violin_plot = sns.violinplot(data=dataframe, x=x_key, y=y_key, hue=hue_key, inner=None, color=".8")
    strip_plot = sns.stripplot(data=dataframe, x=x_key, y=y_key, hue=hue_key, jitter=False, alpha=0.15)
    
    if x_label is not None: plt.xlabel(x_label)
    if y_label is not None: plt.ylabel(y_label)
    
    plt.tight_layout()
    plt.savefig(path)
    plt.close('all')

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

# Create directory if it does not exist
if not os.path.exists(EXPORTS_DIRECTORY) or not os.path.isdir(EXPORTS_DIRECTORY): os.makedirs(EXPORTS_DIRECTORY)
if not os.path.exists(GRAPHS_DIRECTORY) or not os.path.isdir(GRAPHS_DIRECTORY): os.makedirs(GRAPHS_DIRECTORY)

# Check if dataframe already exists (if you wanna recompute it then you must delete it first or change its name)
already_developed_final_dataframe = os.path.exists(FINAL_DATAFRAME_SAVE) and os.path.isfile(FINAL_DATAFRAME_SAVE)
already_developed_final_filtered_dataframe = os.path.exists(FINAL_FILTERED_DATAFRAME_SAVE) and os.path.isfile(FINAL_FILTERED_DATAFRAME_SAVE)

if already_developed_final_dataframe and already_developed_final_filtered_dataframe:
    print("✅  Dataframe loaded fomr folder")
    final_dataframe = pd.read_csv(FINAL_DATAFRAME_SAVE)
    filtered_dataframe = pd.read_csv(FINAL_FILTERED_DATAFRAME_SAVE)
else:
    print("❌  Dataframe not loaded and in development")
    # Load various extracted information into dataframes
    dataframes : List[pd.DataFrame] = []
    for path_to_extracted in arguments.files:
        if not os.path.exists(path_to_extracted) or not os.path.isfile(path_to_extracted):
            exit(f"🚨 File '{path_to_extracted}' does not exist, and should exist")

        file = open(path_to_extracted, 'r', encoding='utf-8')
        information_extracted = json.load(file)
        file.close()

        # Deal with dataframe and quick preprocessing
        dataframe : pd.DataFrame = pd.DataFrame(information_extracted)
        dataframe = preprocess_dataframe(dataframe)
        dataframes.append(dataframe)

    # Get final dataframe with all the information concatenated
    final_dataframe : pd.DataFrame = pd.concat(dataframes)
    final_dataframe = final_dataframe.reset_index(drop=True)
    # Process Dataframe
    final_dataframe['repeated information'] = final_dataframe.duplicated().map({True: 'Yes', False: 'No'})
    final_dataframe['is portuguese'] = final_dataframe[COLUMN_TEXT].progress_apply(lambda text: is_portuguese(text))
    if PREPROCESS_TEXT: final_dataframe[COLUMN_TEXT] = final_dataframe[COLUMN_TEXT].progress_apply(lambda text: preprocess_text(text))
    final_dataframe.drop(DROP_COLUMNS, axis=1, errors='ignore', inplace=True)
    # Save dataframe
    final_dataframe.to_csv(FINAL_DATAFRAME_SAVE, index=False, encoding='utf-8-sig')

    # Filter dataframe
    filtered_dataframe = final_dataframe[(final_dataframe['repeated information'] == 'No') & (final_dataframe['is portuguese'] == 'Yes')]
    filtered_dataframe.to_csv(FINAL_FILTERED_DATAFRAME_SAVE, index=False, encoding='utf-8-sig')
    print("✅  Dataframe developed and saved")

# Graphs to be Exported
export_count_plot(f'{GRAPHS_DIRECTORY}/counts per scraper - unfiltered.svg', final_dataframe, 'scraper', x_label='Scraper', y_label='# Reviews', font_scale=1.15)
export_count_plot(f'{GRAPHS_DIRECTORY}/counts per scraper - unfiltered - repeated information.svg', final_dataframe, 'scraper', hue_key='repeated information', x_label='Scraper', y_label='# Reviews', font_scale=1.15)
export_count_plot(f'{GRAPHS_DIRECTORY}/counts per scraper - unfiltered - is portuguese.svg', final_dataframe, 'scraper', hue_key='is portuguese', x_label='Scraper', y_label='# Reviews', font_scale=1.15)
export_count_plot(f'{GRAPHS_DIRECTORY}/counts per scraper - filtered.svg', filtered_dataframe, 'scraper', x_label='Scraper', y_label='# Reviews', font_scale=1.15)
export_kde_plot(f'{GRAPHS_DIRECTORY}/kde per scraper - filtered - scores.svg', filtered_dataframe, 'valence', hue_key='scraper', x_label='Valence Score', y_label='% Reviews', font_scale=1.15)
export_violin_scatter_plot(f'{GRAPHS_DIRECTORY}/violin scattered per scraper - filtered - scores.svg', filtered_dataframe, 'scraper', 'valence', x_label='Scraper', y_label='# Reviews', font_scale=1.15)

'''
# Get basic structures for model development
training_args           = get_training_args(ROBERTA_OUTPUT_DIR, ROBERTA_LOGGING_DIR)
tokenizer, model_base   = get_xlm_roberta_large()
# Get model
model : TransformerModel = TransformerModel(tokenizer, model_base)
# Develop model
old_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
model.train(final_dataframe[COLUMN_TEXT], final_dataframe[COLUMN_VALENCE], training_args)
sys.stdout = old_stdout
'''