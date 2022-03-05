# DMEIC-2122

This repository was created with the intent to host everything that has been worked on during the master's thesis of **Computer Sciences and Engineering**. Important to note that **no** **data** or important **documentation** is stored in this repository, merely the work in terms of code or literature done for the thesis.

---

## Literature Review 📖
**Directory:** `./papers/`

In the mentioned directory a review of literature for the thesis has been done. For each paper/study a **resume** and **critique** has been done, as well as a **stats spreadsheet**, which is automatically generated from the resumes through commmands hidden in the comments. This spreadsheet identifies, for each study:
- Summary: title, authors, and publication date
- Start and end day of the analysis
- Symptoms of psychosis
- Thecniques for the identification of psychosis
- Metrics for the identification of psychosis
- Problems identified in the study
- Pottentially usefull citations

Scripts were also developed for the automatization of certain tasks such as:
- Exportation of all the latex files developed as PDFs ➡️ `./papers/scripts_latex/export.sh`
- Cleanup of temporary files for the exportation previously mentioned ➡️ `./papers/scripts_latex/cleanup.sh`
- Automatic generation of a new summary and critique from a given template for each (in `./papers/latex/templates`) ➡️ `./papers/scripts_latex/start_new.sh`
- Installing of packages for latex ➡️ `./papers/scripts_latex/install_packages.sh`
- Creation of the previously mentioned spreadsheet ➡️ `./papers/create_spreadsheet.py`
- Automatic uploading of the pertinent documents to a shared Google Drive for the thesis ➡️ `./papers/upload_to_shared_drive.py`

---

## Data Acquisition and Treatment 💾
**Directory:** `./data/`

Although the data itself is not available in the repository, it is still important to mention its structure, in the eventuality that the entire repository needs to be replicated in another computer.

| relevant paths                                                    | objective                                                                                                                             |
| :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| control_info.xlsx                                                 | excel file with the demogrpahic information for each control                                                                          |
| psychosis_info.xlsx                                               | excel file with the demogrpahic information for each patient with psychosis                                                           |
| recordings/*                                                      | folder where the initial recordings, in *WAV* format, are placed                                                                      |
| recordings/controls/*                                             | folder with the recordings, in *WAV* format, from the controls already splitted by subject and task                                   |
| recordings/psychosis/*                                            | folder with the recordings, in *WAV* format, from the patients with psychosis already splitted by subject and task                    |
| recordings/psychosis_uncut/*                                      | folder with the recordings, in *WAV* format, from the patients with psychosis splitted uniquely according to the subject              |
| recordings/psychosis_cutting_times.json                           | JSON file with the timestamps for each task and subject in order to split the uncut version into cut                                  |
| recordings_converted/*                                            | folder where the recordings converted from *WAV* into *wav* format are placed, one track for each subject and task                    |
| recordings_converted/controls_converted/*                         | folder where the recordings, in *wav* format, from the controls for each subject and task                                             |
| recordings_converted/psychosis_converted/*                        | folder where the recordings, in *wav* format, from the patients with psychosis for each subject and task                              |
| recordings_transcribed_results/*                                  | folder with the result from the transcriber, for each subject and task, a *.ctm*, *pctm*, and a *.trs*                                |
| recordings_transcribed_results/controls_transcribed_results/*     | folder with the result from the transcriber, for the controls                                                                         |
| recordings_transcribed_results/psychosis_transcribed_results/*    | folder with the result from the transcriber, for the patients with psychosis                                                          |
| fixed_transcriptions/*                                            | folder with transcriptions mannually corrected, it includes both the fixed version of the transcription and the originals as *.ctm*   |
| fixed_transcriptions/controls/*                                   | folder with transcriptions mannually corrected for each control                                                                       |
| fixed_transcriptions/psychosis/*                                  | folder with transcriptions mannually corrected for each patient with psychosis                                                        |
| exports/*                                                         | folder with exports from the various data folders, used as either backup or to send or recive from the secured servers                |

---

## Data Analysis 📊
**Directory:** `./analysis/`

General profilling of the corpus.

---

## Results 🎉
**Directory:** `./results/`

Results achieved with classifiers on the existent corpus.