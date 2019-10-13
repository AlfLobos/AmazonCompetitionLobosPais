# AmazonCompetitionLobosPais

This github has the following:
1) The report submitted for the Amazon contest 'fORged by Machines'. This file is
2) In the folder `RequiredPrograms' you can find 'PredictNextMonth.py' and 'Simulator.py' which
are python files to be run for the contest. We have left three demand files in the folder to try 
the programs.
3) In the folder 'NotebooksForGraphs' you can find the jupyter-notebooks we used to create the graphs.

Now we comment the python files 'PredictNextMonth.py' and 'Simulator.py' (same as it appears in the report and we recommend
reading it from there).

We were informed that the company wants to use our prediction and inventory prediction system for the years 2006 and 2007 which are data that we do not know. This request is confusing since the lead time is one month, and at each month the company could re-run our system. Our solution to this was to offer the company two programs (callable python files). One would be used to predict the unknown demand for a next month, while the second works more as a simulator. For the second, a user would give a set of years of monthly demand and say take as the first ‘n’ of them are for you to train your system and following years are to test how would your system have worked. The first program is called ‘PredictNextMonth.py’ and the second ‘Simulator.py’. 

Both Python programs receive as an input a .csv or .txt file with three columns exactly with the same format as the file Ten-Year-Demand.csv given to us by the company. In that format, the file is composed of three columns, the first containing year information, the second a list with sorted counts, and the third sorted monthly demands. The rows elements are delimited by commas. Here we assume that the count number is module 12 equivalent, for example, both the count numbers 13 and 1 represent the month of January. This allows for a user to enter a file in which the first month does not necessarily correspond to January of a given year. Both python programs assume that the data is in the same folder as the program. To run the programs the user, need to be able to run Python 3.6 from the console, and having the Python packages Sklearn, Pandas, Numpy, CSV, and Statsmodels installed. 


Guide for PredictNextMonth.py

This Python program assumes that the user wants to predict the next month of demand. The steps to run this program are the following:
1. Run in your computer console 'python RunOneMonth.py' in the folder in which you downloaded the python file (or point to the folder containing the file).
2. Then in the console, the program would ask the user to enter the file to be used for predicting the next month. We assume that the user wants to predict the month immediately after the last monthly data given in the file. To make the program easier, we require the user to have the .csv or .txt file to be used to be in the same folder as the program. 
3. Finally, the program would require the user to enter the remaining inventory of the last month of the data.

Once the previous steps have been followed the computer will return a result through command lines that look as follows:

''
We will use the last three years of data for creating the security deposit. 
This may take a minute to run.
Order Quantity for Next Month: 26.0
''

As you notice, the program which method was used for calculating making the prediction and bias term (see more about this in the small data section \ref {Subsec:InventoryModel})

Guide forSimulator.py

As its name implies, this python program is used to simulate how our program would have behaved under certain demand scenarios. The steps to run this program are the following:
1. Run in your computer console 'python Simulator.py' in the folder in which you downloaded the python file (or point to the folder containing the file).
2. Then, in the console, the program would ask the user for the name of the demand file. To make the program easier, we require the user to have the .csv or .txt file to be used to be in the same folder as the program. 
3. The program would then require the user to enter the remaining inventory of the last month of the data used for training. As the console would say, just pressing enter assumes that 73 units would be used as remaining inventory. 
4. Finally, the program would ask the user to enter how many months of data will be used as unknown data for the simulation. For example, entering 24 would mean to use all data for training up to the last two years. Then, in order, our simulator would calculate an order quantity to make for that month and then compare it to the actual demand experienced in that month. With that, it can calculate the remaining inventory at the end of the month and shortage and holding costs. It would then proceed to calculate an ordering quantity for the following month and so on.

Once the program finish it would create two .csv files in the folder, besides showing on console detailed inventories, cost and order information for the simulated months. The first ‘.csv’ called ‘Results.csv’ has this detailed information, while ‘Summary.csv’ shows the total and average holding, shortage, and the general costs obtained. 