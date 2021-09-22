#!/bin/bash

PACKAGE_DIR=$(kpsewhich -var-value=TEXMFHOME)
DOWNLOAD_LINK="https://mirrors.ctan.org/macros/latex/contrib/"
declare -a packages=(
    "multirow"
)

cd ${PACKAGE_DIR}
mkdir -p tex/latex
mkdir -p temp
cd temp

for package in "${packages[@]}"
do
    if ! [[ -d ../tex/latex/${package} ]]
    then
        # Geting
        wget "${DOWNLOAD_LINK}${package}.zip"
        # Unziping
        unzip ${package}.zip

        # Compiling
        cd $package
        latex ${package}.ins
        cd ..

        # Moving to appropriate place
        mv ${package} ../tex/latex
    fi  
done

cd ..
rm -rf temp