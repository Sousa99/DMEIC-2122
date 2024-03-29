\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{Paper_Summary}
\LoadClass{article}

\usepackage{graphicx}
\graphicspath{ {resources/} }

\usepackage[a4paper, total={6in, 8in}]{geometry}
\usepackage{multirow}

\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
}

\setlength{\parindent}{0em}
\setlength{\parskip}{1em}

% ================================== VARIABLES ================================== 
\newcommand{\varpapertitle}{Default Paper Title}
\newcommand{\varpaperauthor}{Default Paper Author}
\newcommand{\vardate}{Default Date}
% ================================== ========= ================================== 

\DeclareRobustCommand{\makepapertitle}[0] {{
    \title{
        \vspace{-5em}
        \includegraphics[width=2cm]{IST_Logo.png} \\
        \vspace{1cm}  
        \textbf{\varpapertitle} \\
        \Large{by \varpaperauthor} \\
        \vspace{0.5cm}
        \Large{Paper Summary}
    }
    \author{Rodrigo Borges Pessoa de Sousa }
    \date{\vardate}

    \maketitle
}}

\DeclareRobustCommand{\breakline} {{
    \rule{\textwidth}{0.4pt}
}}