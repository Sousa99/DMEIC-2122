import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# ==================================== PARAMETERS ====================================
DIR_LATEX_PAPERS = "./latex/"
VALID_EXTENSIONS = ["tex"]
BLACKLIST = ["Template.tex"]

CODE="% $"
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
    charactheristics: Dict[str, List[Tuple[int, int]]] = field(default_factory=dict)
    techniques: Dict[str, List[Tuple[int, int]]] = field(default_factory=dict)
    metrics: Dict[str, List[int]] = field(default_factory=dict)
    problems: Dict[str, List[int]] = field(default_factory=dict)
    citations: Dict[str, List[int]] = field(default_factory=dict)

    def add_paper_summary(self, paper: PaperSummaryStruct):
        new_index = len(self.papers)
        self.papers.append(paper)

        # Charactheristics
        for charactheristic in paper.charactheristics:
            tmp_charactheristic = tuple([new_index, charactheristic.value])
            if charactheristic.key in self.charactheristics: self.charactheristics[charactheristic.key].append(tmp_charactheristic)
            else: self.charactheristics[charactheristic.key] = [tmp_charactheristic]

        # Techniques
        for technique in paper.techniques:
            tmp_technique = tuple([new_index, technique.value])
            if technique.key in self.techniques: self.techniques[technique.key].append(tmp_technique)
            else: self.techniques[technique.key] = [tmp_technique]

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
            arguments = list(arguments_line.split(","))
            current_paper_summary.parse_info(code, arguments)

        statistics.add_paper_summary(current_paper_summary)

        continue