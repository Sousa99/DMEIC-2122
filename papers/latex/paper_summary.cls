\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{Paper_Summary}
\LoadClass{article}

\DeclareRobustCommand{\papertitle}[1] {{
    \title{ \textbf{#1} \\ Paper Summary}
    \author{Rodrigo Borges Pessoa de Sousa }
    \date{September 2021}
}}

\DeclareRobustCommand{\breakline} {{
    \rule{\textwidth}{0.4pt}
}}