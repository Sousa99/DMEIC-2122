#!/bin/bash
latex_papers="./latex"
pdf="./pdf"
cleanup="./cleanup.sh"

cd ..
cd ${latex_papers}

for file_tex in *.tex; do
    filename=$( echo ${file_tex} | cut -f 1 -d '.' )
    file_pdf=$( echo "${pdf}/${filename}.pdf")

    if (! [ -f "../$file_pdf" ]) | [ "$file_tex" -nt "../$file_pdf" ]; then

        echo "⚙️    ${filename}"
        latexmk -pdf -quiet "$file_tex"
        mv "./${filename}.pdf" "../${file_pdf}"
        echo

    fi

done

cd ..
cd ./scripts_latex

${cleanup}