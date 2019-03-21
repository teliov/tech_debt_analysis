# Description

`issue_close_time_analysis.py` analysis the 2000 most recent closed issues of a repository on github and creates a histogram like data set which can be used to visualize how soon issues were closed

`commit_analysis.py` analyses all the commits from a repository with the aim to extract contributors and number of commits. The idea is to use this to analyze the [truck factor](http://www.agileadvice.com/2005/05/15/agilemanagement/truck-factor/) for  a project. In this implementation a contributor is counted towards the truck factor if said contributor has 20 commits or more consistently across a period under consideration.

`analysis.ipynb` contains code which is used to generate images and perform further analysis on the data generated by the scripts above.