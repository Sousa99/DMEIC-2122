#!/bin/bash

PACKAGE_DIR=$(kpsewhich -var-value=TEXMFHOME)
declare -a DOWNLOAD_LINK=(
    "https://mirrors.ctan.org/macros/latex/contrib/"
    "https://mirrors.ctan.org/macros/generic/"
)
declare -a packages=(
    "multirow"
    "hyperref"
    "pdftexcmds"
    "infwarerr"
    "pdfescape"
    "letltxmacro"
    "bitset"
)

mkdir -p ${PACKAGE_DIR}
cd ${PACKAGE_DIR}

mkdir -p tex/latex
mkdir -p temp
cd temp

for package in "${packages[@]}"
do
    if ! [[ -d ../tex/latex/${package} ]]
    then
        # Geting
        for download_link in "${DOWNLOAD_LINK[@]}"
        do
            if wget --spider "${download_link}${package}.zip"
            then
                wget "${download_link}${package}.zip"
            fi
        done
        # Unziping
        unzip ${package}.zip

        # Compiling
        cd $package
        if test -f "${package}.ins"; then
            latex "${package}.ins"
        else
            tex "${package}.dtx"
        fi

        cd ..
        # Moving to appropriate place
        mv ${package} ../tex/latex
    fi  
done

cd ..
rm -rf temp