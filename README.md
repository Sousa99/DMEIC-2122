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
- Exportation of all the latex files developed as PDFs ➡️ [`./papers/scripts_latex/export.sh`](./papers/scripts_latex/export.sh)
- Cleanup of temporary files for the exportation previously mentioned ➡️ [`./papers/scripts_latex/cleanup.sh`](./papers/scripts_latex/cleanup.sh)
- Automatic generation of a new summary and critique from a given template for each (in [`./papers/latex/templates`](./papers/latex/templates)) ➡️ [`./papers/scripts_latex/start_new.sh`](./papers/scripts_latex/start_new.sh)
- Installing of packages for latex ➡️ [`./papers/scripts_latex/install_packages.sh`](./papers/scripts_latex/install_packages.sh)
- Creation of the previously mentioned spreadsheet ➡️ [`./papers/create_spreadsheet.py`](./papers/create_spreadsheet.py)
- Automatic uploading of the pertinent documents to a shared Google Drive for the thesis ➡️ [`./papers/upload_to_shared_drive.py`](./papers/upload_to_shared_drive.py)

---

## Data Acquisition and Treatment 💾
**Directory:** `./data/`

Although the data itself is not available in the repository, it is still important to mention its structure, in the eventuality that the entire repository needs to be replicated in another computer.

| relevant paths                                                    | objective                                                                                                                             |
| :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| control_info.xlsx                                                 | excel file with the demographic information for each control                                                                          |
| psychosis_info.xlsx                                               | excel file with the demographic information for each patient with psychosis                                                           |
| bipolar_info.xlsx                                                 | excel file with the demographic information for each patient with bipolar disorder                                                    |
| to_identify_info.xlsx                                             | excel file with the demographic information for each patient with diagnosis yet to confirm with doctor                                |
| recordings/*                                                      | folder where the initial recordings, in *WAV* format, are placed                                                                      |
| recordings/bipolars/*                                             | folder with the recordings, in *WAV* format, from the patients with bipolar disorder already splitted by subject and task             |
| recordings/bipolars_uncut/*                                       | folder with the recordings, in *WAV* format, from the patients with bipolar disorder splitted uniquely according to the subject       |
| recordings/controls/*                                             | folder with the recordings, in *WAV* format, from the controls already splitted by subject and task                                   |
| recordings/controls_uncut/*                                       | folder with the recordings, in *WAV* format, from the controls splitted uniquely according to the subject                             |
| recordings/psychosis/*                                            | folder with the recordings, in *WAV* format, from the patients with psychosis already splitted by subject and task                    |
| recordings/psychosis_uncut/*                                      | folder with the recordings, in *WAV* format, from the patients with psychosis splitted uniquely according to the subject              |
| recordings/to_identify/*                                          | folder with the recordings, in *WAV* format, from the patients which diagnosis is still unknonwn                                      |
| recordings/bipolars_cutting_times.json                            | JSON file with the timestamps for each task and patient, with bipolar disorder, in order to split the uncut version into cut          |
| recordings/controls_cutting_times.json                            | JSON file with the timestamps for each task and control subject in order to split the uncut version into cut                          |
| recordings/psychosis_cutting_times.json                           | JSON file with the timestamps for each task and patients, with psychosis, in order to split the uncut version into cut                |
| recordings/to_identify_cutting_times.json                         | JSON file with the timestamps for each task and patient, without confirmed diagnosis, in order to split the uncut version into cut    |
| recordings_converted/*                                            | folder where the recordings converted from *WAV* into *wav* format are placed, one track for each subject and task                    |
| recordings_transcribed/*                                          | folder created by the transcriber with everything that it outputs or develops in order to develop said output                         |
| recordings_transcribed_results/*                                  | folder with the result from the transcriber, for each subject and task, a *.ctm*, *pctm*, and a *.trs*                                |
| fixed_transcriptions/*                                            | folder with transcriptions mannually corrected, it includes both the fixed version of the transcription and the originals as *.ctm*   |
| exports/*                                                         | folder with exports from the various data folders, used as either backup or to send or recive from the secured servers                |

---

## Data Analysis 📊
**Directory:** `./analysis/`

General profilling of the corpus.

---

## Results 🎉
**Directory:** `./results/`

Results achieved with classifiers on the existent corpus.

---

## General Pipeline Execution 🏃

1.  Data is first acquired by recording a subject appropriately, during the entirety of the execution of the protocol. Then the recording is imediatelly placed on the folder [recordings/to_identify](./data/recordings/to_identify/).

<br/>

2.  Each recording is listened to in order to propperly identify the timestamps at which the subject is executing each task, as to propperly segment the original recording. This timestamps are then placed on [recordings/to_identify_cutting_times.json](./data/recordings/to_identify_cutting_times.json).

<br/>

3.  Information (id for anonimity and socio-demographic information) is saved on [to_identify_info.xlsx](./data/to_identify_info.xlsx). If the group to which the recording pertains is already known, it is also writen on this spreadsheet for later separation.

<br/>

4.  Now the uniqueness of the ids must be checked. For this the script [scripts/check_conflicts_ids.sh](./data/scripts/check_conflicts_ids.sh) must be executed. In fact this script checks for the uniqueness of the id on the entire corpus, although the uniqueness could be exclusive for the group where the patient is inserted since each id will be appended to a tag (*c_*, *p_*, and *b_*, for controls, patients with psychosis, and patients with bipolar disorder respectively).

<br/>

5.  At some point the diagnoses of the various patients with unknown diagnoses will be known, and at that point the recordings, the timestamps and the information will need to be moved from the various files and folder associated with **to_identify** into **controls**, **psychosis** or **bipolars**.

<br/>

6.  After the various recordings have been propperly sorted out and correctly placed in their individual folders they need now to be split up, as to have one recording for each subject and task. For this purpose, the script [scripts/cut_audios.py](./data/scripts/cut_audios.py), must be executed, one time for each one of the groups of subjects.
```bash
python3 ./cut_audios.py -data ../recordings/controls_uncut/ -times ../recordings/controls_cutting_times.json -output ../recordings/controls/ -tag "c"
python3 ./cut_audios.py -data ../recordings/bipolars_uncut/ -times ../recordings/bipolars_cutting_times.json -output ../recordings/bipolars/ -tag "b"
python3 ./cut_audios.py -data ../recordings/psychosis_uncut/ -times ../recordings/psychosis_cutting_times.json -output ../recordings/psychosis/ -tag "p"
```

<br/>

7.  The recordings must now be exported, for this purpose, you can now execute the script [scripts/export.sh](./data/scripts/export.sh), which will create a new zip file with the recordings and pertinent subjects' information into the exports folder.

<br/>

8.  Send the exported recordings and information to the secured INESC-ID servers. Unpack the contents of the compressed folder and correctly merge the already existent information with these new information. In this very specific case you may delete the recordings that exist already in the servers, and simply move this new information.

<br/>

9.  While connected to the INESC-ID servers, execute the script [scripts/convert.sh](./data/scripts/convert.sh), which will convert the various *.WAV* recordings, for each subject and task, into *.wav* recordings. The script was developed in a way that it will not convert already converted tracks.

<br/>

10. While connected to the INESC-ID servers, execute the script [scripts/transcribe.sh](./data/scripts/transcribe.sh), which will transcribe, usicng *TRIBUS*, the various audio tracks, one for each subject and task. The script was developed in a way that it will not transcribe already transcribed tracks. Since this process can sometimes be lengthy, it iss advisable that the user creates a *TMUX* session for its execution.

<br/>

11. While connected to the INESC-ID servers, execute the script [scripts/transcribe_results.sh](./data/scripts/transcribe_results.sh), which will copy all the relevant exports from *TRIBUS* execution. Meaning that it will copy all of the transcriptions and correctly place them in hierarchy of folders, first by group, then subject, and finally task. The script was developed in a way that it will not copy transcriptions from tracks which had already been copied before.

<br/>

12. All of the information generated in the server must now be exported. For this purpose, while connected to the INESC-ID servers, execute the script [scripts/exportHLT.sh](./data/scripts/exportHLT.sh), which will export the converted recordings, the *TRIBUS* exports, and the transcription results into three diferent zip files in the exports folder.

<br/>

13. You must now send the relevant compressed folders back to your local machine, the only crucial one would be the transcription results. Once you have received the intented files you must now merge this new information with the local one in your computer. Once again, the way the project is structured allpows you to simply delete the results which you have in your machine and move the new results into its place.

<br/>

14. You are now free to run any analysis or models with the obtained information. 🥳