#!/bin/bash
latex_papers="./latex"
pdf="./pdf"
cleanup="./cleanup.sh"

cd ..
cd ${latex_papers}

latexmk -pdf -quiet
cd ..

mkdir -p ${pdf}

mv ${latex_papers}/*.pdf ${pdf}/
cd ./scripts_latex
${cleanup}