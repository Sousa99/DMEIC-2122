#!/bin/bash
latex_papers="./latex/"
template_papers="./latex/templates/"

cd ..
find ${template_papers} -name \*.tex -exec cp {} ${latex_papers} \;