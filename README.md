Detecting hot news from twitter feeds

Dependencies:
Tweepy
Numpy
NLTK
Scikit-Learn

Main.py is the main file to run:
Every ten minutes after downloading latest tweets and storing them in the storage, 
Event clusters are updated and the two most important events are printed to the screen 
(printing to the screen is just to show that the program works). 

Based on the importance of these events (IMPORTANCE_THRESHOLD), we decide if we should 
write the results to the "Results.txt" file or not. IMPORTANCE_THRESHOLD is used to detect 
hot news. If we decrease this value the chance of detecting a hot news in begining of the 
day increases. If we increase this value, the chance decreases so the two hot news are 
recommended to the user right before the end of 24 hours.

Each class has its own __main__ to test its functionalities.

Every 24 hours right after the midnight the the results file is deleted. During the next 24 hours 
if a new hot news is detected it is written to the file (result.txt). By the end of 24 hours if 
we couldn't find any hot news the two most important news are written to the results.txt file.

Please read the wikipage for explanation of the clustering algorithm.
