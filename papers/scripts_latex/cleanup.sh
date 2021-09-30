#!/bin/bash
latex_papers="./latex"

cd ..

rm -f ${latex_papers}/*.aux
rm -f ${latex_papers}/*.fdb_latexmk
rm -f ${latex_papers}/*.fls
rm -f ${latex_papers}/*.log
rm -f ${latex_papers}/*.synctex.gz
rm -f ${latex_papers}/*.dvi
rm -f ${latex_papers}/*.out
rm -f ${latex_papers}/*.pdf