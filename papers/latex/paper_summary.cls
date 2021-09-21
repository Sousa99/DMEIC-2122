\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{Paper_Summary}
\LoadClass{article}

\usepackage{graphicx}
\graphicspath{ {resources/} }

\usepackage[a4paper, total={6in, 8in}]{geometry}

% ================================== VARIABLES ================================== 
\newcommand{\varpapertitle}{Default Paper Title}
\newcommand{\vardate}{Default Date}
% ================================== ========= ================================== 

\DeclareRobustCommand{\makepapertitle}[0] {{
    \title{
        \includegraphics[width=2cm]{IST_Logo.png} \\
        \vspace{1cm}  
        \textbf{\varpapertitle} \\ Paper Summary
    }
    \author{Rodrigo Borges Pessoa de Sousa }
    \date{\vardate}

    
    
    \maketitle
}}

\DeclareRobustCommand{\breakline} {{
    \rule{\textwidth}{0.4pt}
}}