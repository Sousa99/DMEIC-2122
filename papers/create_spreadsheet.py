import os
import xlsxwriter
import pandas as pd

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# ==================================== PARAMETERS ====================================
DIR_LATEX_PAPERS = "./latex/"
VALID_EXTENSIONS = ["tex"]
BLACKLIST = ["Template.tex"]

CODE="% $"

FILE_STATS_EXCEL = "./stats/stats_spreadsheet.xlsx"
TICK_MARK = 'X'
# ==================================== ========== ====================================

# ======================================= CLASS PAPER SUMMARY =======================================
@dataclass
class Charactheristic:
    key: str
    value: int

@dataclass
class Technique:
    key: str
    value: int

@dataclass
class Metric:
    key: str

@dataclass
class Problem:
    key: str

@dataclass
class Citation:
    key: str

@dataclass
class PaperSummaryStruct:
    ref: str = ''
    title: str = None
    author: str = None
    date: str = None
    start_date: datetime.date = None
    end_date: datetime.date = None
    charactheristics: List[Charactheristic] = field(default_factory=list)
    techniques: List[Technique] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)
    problems: List[Problem] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)

    def parse_info(self, code: str, values: List[str]):
        
        if code == "REF": self.ref = values[0]
        elif code == "TITLE": self.title = values[0]
        elif code == "AUTHOR": self.author = values[0]
        elif code == "DATE": self.date = values[0]
        elif code == "START-DATE": self.start_date = datetime.strptime(values[0], '%d/%m/%Y')
        elif code == "END-DATE": self.end_date = datetime.strptime(values[0], '%d/%m/%Y')
        elif code == "CHARACTHERISTIC": self.charactheristics.append(Charactheristic(values[0], int(values[1])))
        elif code == "TECHNIQUE": self.techniques.append(Technique(values[0], int(values[1])))
        elif code == "METRIC": self.metrics.append(Metric(values[0]))
        elif code == "PROBLEM": self.problems.append(Problem(values[0]))
        elif code == "CITATION": self.citations.append(Citation(values[0]))
# ======================================= =================== =======================================
# ======================================= STATS =======================================
@dataclass
class PaperStats:
    papers: List[PaperSummaryStruct] = field(default_factory=list)
    # Stats
    charactheristics: Dict[str, Dict[int, int]] = field(default_factory=dict)
    techniques: Dict[str, Dict[int, int]] = field(default_factory=dict)
    metrics: Dict[str, List[int]] = field(default_factory=dict)
    problems: Dict[str, List[int]] = field(default_factory=dict)
    citations: Dict[str, List[int]] = field(default_factory=dict)

    def add_paper_summary(self, paper: PaperSummaryStruct):
        new_index = len(self.papers)
        self.papers.append(paper)

        # Charactheristics
        for charactheristic in paper.charactheristics:
            if charactheristic.key in self.charactheristics: self.charactheristics[charactheristic.key][new_index] = charactheristic.value
            else: self.charactheristics[charactheristic.key] = { new_index: charactheristic.value }

        # Techniques
        for technique in paper.techniques:
            if technique.key in self.techniques: self.techniques[technique.key][new_index] = technique.value
            else: self.techniques[technique.key] = { new_index: technique.value }

        # Metrics
        for metric in paper.metrics:
            if metric.key in self.metrics: self.metrics[metric.key].append(new_index)
            else: self.metrics[metric.key] = [new_index]

        # Problems
        for problem in paper.problems:
            if problem.key in self.problems: self.problems[problem.key].append(new_index)
            else: self.problems[problem.key] = [new_index]

        # Citations
        for citation in paper.citations:
            if citation.key in self.citations: self.citations[citation.key].append(new_index)
            else: self.citations[citation.key] = [new_index]

        return

    def export_to_excel(self):
        writer = pd.ExcelWriter(FILE_STATS_EXCEL, engine='xlsxwriter',
            date_format = 'dd/mm/yyyy', datetime_format='dd/mm/yyyy')
        self.write_summary(writer)
        self.write_sheet_with_score(writer, 'Charactheristics', self.charactheristics)
        self.write_sheet_with_score(writer, 'Techniques', self.techniques)
        self.write_sheet_without_score(writer, 'Metrics', self.metrics)
        self.write_sheet_without_score(writer, 'Problems', self.problems)
        self.write_sheet_without_score(writer, 'Citations', self.citations)

        writer.save()
        print("💾 Excel statistics saved")

    def write_summary(self, writer: pd.ExcelWriter):

        SHEET_NAME = "Summary"
        # ================================== SET TYPES AND WRITE ==================================
        df = pd.DataFrame({
            'Paper Title': pd.Series(dtype=str),
            'Author': pd.Series(dtype=str),
            'Paper Date': pd.Series(dtype=str),
            'Start Date': pd.Series(dtype='datetime64[ns]'),
            'End Date': pd.Series(dtype='datetime64[ns]'),
            'Days Taken': pd.Series(dtype=int)
        })

        for paper in self.papers:
            df = df.append({
                'Paper Title': paper.title,
                'Author': paper.author,
                'Paper Date': paper.date,
                'Start Date': paper.start_date,
                'End Date': paper.end_date,
                'Days Taken': (paper.end_date - paper.start_date).days
            }, ignore_index=True)

        df.to_excel(writer, sheet_name=SHEET_NAME)
        sheet = writer.sheets[SHEET_NAME]
        # ================================== SET TYPES AND WRITE ==================================

        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column)) * 1.10
            col_idx = df.columns.get_loc(column) + 1
            sheet.set_column(col_idx, col_idx, column_length)
        
        sheet.freeze_panes(1, 2)

    def write_sheet_with_score(self, writer: pd.ExcelWriter, sheet_name: str, info_dict: Dict[str, Dict[int, int]]):

        # ================================== SET TYPES AND WRITE ==================================
        df_dictionary = { 'Paper Title': pd.Series(dtype=str) }
        for item_key in info_dict: df_dictionary[item_key] = pd.Series(dtype=int)
        df = pd.DataFrame(df_dictionary)

        for paper_index, paper in enumerate(self.papers):
            paper_dictionary = { 'Paper Title': paper.title }
            for item_key in info_dict:
                item = info_dict[item_key]
                if paper_index in item: paper_dictionary[item_key] = item[paper_index]
                else: paper_dictionary[item_key] = None
            
            df = df.append(paper_dictionary, ignore_index=True)

        df.to_excel(writer, sheet_name=sheet_name)
        workbook = writer.book
        sheet = writer.sheets[sheet_name]
        # ================================== SET TYPES AND WRITE ==================================

        format_center = workbook.add_format({'align': 'center'})

        for column in df:
            format = None
            column_length = max(df[column].astype(str).map(len).max(), len(column)) * 1.10

            if column != 'Paper Title': format = format_center

            col_idx = df.columns.get_loc(column) + 1
            sheet.set_column(col_idx, col_idx, column_length, format)

        sheet.freeze_panes(1, 2)

    def write_sheet_without_score(self, writer: pd.ExcelWriter, sheet_name: str, info_dict: Dict[str, List[int]]):

        # ================================== SET TYPES AND WRITE ==================================
        df_dictionary = { 'Paper Title': pd.Series(dtype=str) }
        for item_key in info_dict: df_dictionary[item_key] = pd.Series(dtype=str)
        df = pd.DataFrame(df_dictionary)

        for paper_index, paper in enumerate(self.papers):
            paper_dictionary = { 'Paper Title': paper.title }
            for item_key in info_dict:
                item = info_dict[item_key]
                if paper_index in item: paper_dictionary[item_key] = TICK_MARK
                else: paper_dictionary[item_key] = None
            
            df = df.append(paper_dictionary, ignore_index=True)

        df.to_excel(writer, sheet_name=sheet_name)
        workbook = writer.book
        sheet = writer.sheets[sheet_name]
        # ================================== SET TYPES AND WRITE ==================================

        format_center = workbook.add_format({'align': 'center'})

        for column in df:
            format = None
            column_length = max(df[column].astype(str).map(len).max(), len(column)) * 1.10

            if column != 'Paper Title': format = format_center

            col_idx = df.columns.get_loc(column) + 1
            sheet.set_column(col_idx, col_idx, column_length, format)

        sheet.freeze_panes(1, 2)

# ======================================= ===== =======================================

print("🚀 Liftoff: analysing papers created ...")
print()

statistics = PaperStats()

directory = os.fsencode(DIR_LATEX_PAPERS)
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     extension = filename.split('.')[-1]
     if extension in VALID_EXTENSIONS and filename not in BLACKLIST:

        print("⚙️  [{0}] Converting file".format(filename))
        file = open(directory + file, 'r')
        lines = file.readlines()

        current_paper_summary = PaperSummaryStruct()

        for line in lines:
            coded = line.strip().startswith(CODE)
            if not coded: continue

            line_corrected = line.strip().replace(CODE, '')
            code = line_corrected.split('{')[0]
            arguments_line = line_corrected.replace(code + '{', '').replace('}', '')
            arguments = list(arguments_line.split("; "))
            current_paper_summary.parse_info(code, arguments)

        statistics.add_paper_summary(current_paper_summary)

        continue

print()
statistics.export_to_excel()