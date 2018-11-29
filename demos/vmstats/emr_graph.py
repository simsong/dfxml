#!/usr/bin/env python3
# -*- mode: python; -*-

# 
# Graph the emr_stats object
#

import ctools.latex_tools
from emr_stats import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

latex_header=r"""
\documentclass[10pt,twoside,openright]{article}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{pdfpages}
\usepackage{xcolor}
\usepackage{transparent}
\usepackage[margin=0.5in]{geometry}
\usepackage{longtable}
\usepackage{amsfonts}
\usepackage{listings}

\definecolor{numb}{rgb}{0,0.6,0}
\definecolor{delim}{rgb}{0.5,0.5,0.5}
\definecolor{punct}{rgb}{0.58,0,0.82}

\lstdefinelanguage{json}{
    basicstyle=\ttfamily\fontsize{7}{8}\selectfont,
    numbers=left,
    numberstyle=\scriptsize,
    stepnumber=1,
    numbersep=8pt,
    showstringspaces=false,
    breaklines=true,
    frame=lines,
    backgroundcolor=\color{white},
    literate=
     *{:}{{{\color{punct}{:}}}}{1}
      {,}{{{\color{punct}{,}}}}{1}
      {\{}{{{\color{delim}{\{}}}}{1}
      {\}}{{{\color{delim}{\}}}}}{1}
      {[}{{{\color{delim}{[}}}}{1}
      {]}{{{\color{delim}{[}}}}{1}
      {'}{{{\color{delim}{[}}}}{1}
      {"}{{{\color{delim}{]}}}}{1},
}

\definecolor{mygreen}{rgb}{0,0.6,0}
\definecolor{mygray}{rgb}{0.5,0.5,0.5}
\definecolor{mymauve}{rgb}{0.58,0,0.82}
\lstset{ 
  backgroundcolor=\color{white},   % choose the background color; you must add \usepackage{color} or \usepackage{xcolor}; should come as last argument
  basicstyle=\ttfamily\fontsize{8}{9}\selectfont,        % the size of the fonts that are used for the code
  breakatwhitespace=false,         % sets if automatic breaks should only happen at whitespace
  breaklines=true,                 % sets automatic line breaking
  captionpos=t,                    % sets the caption-position to bottom
  commentstyle=\color{mygreen},    % comment style
  extendedchars=true,              % lets you use non-ASCII characters; for 8-bits encodings only, does not work with UTF-8
  frame=single,                    % adds a frame around the code
  keepspaces=true,                 % keeps spaces in text, useful for keeping indentation of code (possibly needs columns=flexible)
  keywordstyle=\color{blue},       % keyword style
  language=json,                   % the language of the code
  numbers=left,                    % where to put the line-numbers; possible values are (none, left, right)
  numbersep=5pt,                   % how far the line-numbers are from the code
  numberstyle=\tiny\color{mygray}, % the style that is used for the line-numbers
  rulecolor=\color{black},         % if not set, the frame-color may be changed on line-breaks within not-black text (e.g. comments (green here))
  showspaces=false,                % show spaces everywhere adding particular underscores; it overrides 'showstringspaces'
  showstringspaces=false,          % underline spaces within strings only
  showtabs=false,                  % show tabs within strings adding particular underscores
  stepnumber=2,                    % the step between two line-numbers. If it's 1, each line will be numbered
  stringstyle=\color{mymauve},     % string literal style
  tabsize=4,                       % sets default tabsize to 2 spaces
  title=\lstname                   % show the filename of files included with \lstinputlisting; also try caption instead of title
}

\begin{document}
"""

latex_footer="""
\end{document}
"""

class EMR_Graph:
    def __init__(self,ci):
        self.ci = ci            # cluster info structure
        self.tf = None          # LaTeX file

    def sorted_nodes(self):
        return sorted(self.ci.nodes.values(), key=lambda node:node.instanceID)

    CLUSTER_LOAD_FILENAME="cluster_load.pdf"
    def graph_cluster_load(self):
        fig,(ax1,ax2) = plt.subplots(nrows=2, ncols=1)
        fig.set_size_inches(6,8)
        for ax in [ax1,ax2]:
            ax.xaxis_date()
            ax.set_axisbelow(True)
            plt.setp( ax.xaxis.get_majorticklabels(), rotation=70, fontsize=6)
        ax1.set_ylabel('System Load')
        ax2.set_ylabel('Normalized System Load')
        for node in self.sorted_nodes():
            dates  = [stat[DATETIME] for stat in node.stats]
            avgs   = [stat[LOAD_AVERAGE][0] for stat in node.stats]
            navgs  = [stat[LOAD_AVERAGE][0]/stat[CORES] for stat in node.stats]
            ax1.plot( dates, avgs, label=node.instanceID + " " + self.ci.instance_type(node.instanceID), alpha=0.7)
            ax2.plot( dates, navgs, label=node.instanceID + " " + self.ci.instance_type(node.instanceID), alpha=0.7)
        for ax in [ax1,ax2]:
            ax.legend(loc='best',fontsize=4)
        fig.subplots_adjust(bottom=0.2)
        fig.savefig( self.CLUSTER_LOAD_FILENAME )
        self.tf.write(r"\includegraphics[width=\textwidth]{%s}" % (self.CLUSTER_LOAD_FILENAME))
        self.tf.write("\n")

    CLUSTER_MEM_FILENAME="cluster_mem.pdf"
    def graph_cluster_memory(self):
        fig,ax, = plt.subplots(nrows=1, ncols=1)
        ax.xaxis_date()
        ax.set_axisbelow(True)
        ax.set_ylabel('% Free Memory per node')
        ax.set_ylim(bottom=0,top=1.0)
        for node in self.sorted_nodes():
            dates = [stat[DATETIME] for stat in node.stats]
            mems  = [stat[MEM_STATS]['free']/stat[MEM_STATS]['total'] for stat in node.stats]

            ax.plot( dates, mems, label=node.instanceID + " " + self.ci.instance_type(node.instanceID))
        ax.legend(loc='best',fontsize=4)
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=70, fontsize=6)
        fig.subplots_adjust(bottom=0.2)
        fig.savefig( self.CLUSTER_MEM_FILENAME )
        self.tf.write(r"\includegraphics[width=\textwidth]{%s}" % (self.CLUSTER_MEM_FILENAME))
        self.tf.write("\n")

    def write_cluster_info(self):
        self.tf.write("\\begin{lstlisting}\n")
        self.tf.write( json.dumps(self.ci.describe_cluster, sort_keys=True, indent=4))
        self.tf.write("\\end{lstlisting}\n")
        for node in self.sorted_nodes():
            self.tf.write("\\begin{lstlisting}[caption=%s]\n" % node.instanceID)
            self.tf.write( json.dumps(node.instanceInfo, sort_keys=True, indent=4))
            self.tf.write("\\end{lstlisting}\n")
            
    def graph(self,outfilename):
        self.texdir  = os.path.dirname(outfilename)
        self.texfile = os.path.splitext(outfilename)[0] + ".tex"
        with open(self.texfile,"w") as tf:
            self.tf = tf
            self.tf.write(latex_header)
            self.graph_cluster_load()
            self.graph_cluster_memory()
            self.write_cluster_info()
            self.tf.write(latex_footer)
            self.tf.flush()
            (pdffile,pages) = ctools.latex_tools.run_latex(self.texfile,delete_tempfiles=True,)
            print(f"Created {pdffile} with {pages} pages")
            
            
