# Authenticating and connecting with our Google Cloud Storage Bucket allowing us to push and create files.
from google.colab import auth
auth.authenticate_user()

!echo "deb http://packages.cloud.google.com/apt gcsfuse-bionic main" > /etc/apt/sources.list.d/gcsfuse.list
!curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
!apt -qq update
!apt -qq install gcsfuse

#Run after authenticating to create a mounted folder
!mkdir data2
!gcsfuse nhanes data2

# Importing the packages needed
import wget
import pandas
import seaborn
import matplotlib.pyplot as plt
import numpy
import os
import sys

# Description: This function purpose is to create a barplot graph with data from the dataframe
# Parameters:
#   data: (dataframe, input, req) (Description: Pandas dataframe with structured data from NHanes)
#   x: (string, input, req) (Description: Column from the Pandas dataframe which is displayed on the x-coordinate of the graph)
#   y: (string, input, req) (Description: Column from the Pandas dataframe which is displayed on the y-coordinate of the graph)
#   hue: (string, input, opt) (Description: Categorical variable to break up barplot)
#   yaxislabels: (string, input, opt) (Description: labels that a displayed on the y-axis of our graphs.)
#   gtype: (string, input, opt) (Description: Variable is used to rename the saved figure after graph is created)
#   ptype: (string, input, opt) (Description: Variable is used to determine what type of graph is being made. (bar or line))
# Returns: nothing
#

def creategraph(data, x, y, hue='', yaxislabels='', gtype='', ptype=''):
    # Determining if they want a bar graph or a line graph
    if ptype == "bar":
      g = seaborn.catplot(data=data, kind="bar", x=x, y=y, hue=hue, aspect=2, legend=None, palette="crest") # Creating graph object
      if yaxislabels != '': # checking if labels exist
        g.set(xlabel="Race", ylabel=yaxislabels) # Setting the labels on the X and Y axis of the graph

      tempdf = data.groupby([x,hue])[y].mean() # Making a temp DataFrame to determine the mean of a said group
      g.set(ylim=(tempdf.min() * 0.9, data[y].mean() * 1.12)) # Setting the Y limit of the graph to better read the data.
      plt.legend(bbox_to_anchor=(1.11, 0.5), loc='upper right', title="Year") # Creating the legend for the graph
      plt.tight_layout() # Formatting the graph object
      plt.show() # Displaying the graph
      g.figure.savefig(f"/content/data2/images/{gtype + ptype}.png") # Saving the figure to a png format
    else:
      g = seaborn.lineplot(data=data, x=hue, y=y, hue=x) # Creating graph object
      if yaxislabels != '': # checking if labels exist
        g.set(xlabel="Years", ylabel=yaxislabels) # Setting the labels on the X and Y axis of the graph

      plt.legend(bbox_to_anchor=(1.45, 0.5), loc='upper right', title="Race") # Creating the legend for the graph
      plt.figure(figsize = (15,8)) # Making the figure size bigger
      plt.tight_layout() # Formatting the graph object
      plt.show() # Displaying the graph
      g.figure.savefig(f"/content/data2/images/{gtype + ptype}.png", bbox_inches='tight') # Saving the figure to a png format


# Description: This function is reading a .XPT file and converting into a dataframe 
# Parameters:
#   filepath: (string, input, req) (Description: File path to the XPT file needed)
# Returns: Dataframe from the .XPT file
#

def pulldata(filepath):
  # Using Pandas to read a .XPT file and put it into a DataFrame
  df = pandas.read_sas(filepath, format="xport")
  df.head(10)
  return df

# Description: This function is using the dataframe and file type to determine what columns are needed
# Parameters:
#   df: (dataframe, input, req) (Description: The dataframe that is being used to get the columns from)
#   filetype: (string, input, req) (Description: Is used to determine which columns we need)
# Returns: Reformatted dataframe
#

def selectdata(df, filetype):
  # Using a specific file type we determine which columns are needed to reformat the dataframe
  if filetype == "DEMO": #Demographic
    columns = ['SEQN', 'SDDSRVYR', 'RIDRETH1', 'RIDAGEYR', 'INDHHIN2']
  elif filetype == "BPX": #Blood pressure
    columns = ['SEQN', 'BPXSY1', 'BPXDI1', 'BPAEN3']
  elif filetype == "CHOL": # Cholesterol
    columns = ['SEQN', 'LBDLDL']
  elif filetype == "GLU": # Glucose
    columns = ['SEQN', 'LBXGLU']
  
  return df[columns]

# Description: This function cleans data
# Parameters:
#   data: (dataframe, input/output, req) (Description: The dataframe that is being altered)
#   info: (dictionary, input, req) (Description: Dictionaries with the information to alter the dataframe)
# Returns: Cleaned dataframe
#

def cleandata(data, info):
  #Replacing column labels within the dataframe
  data = data.replace({"RIDRETH1": info["race"]})
  data = data.replace({"SDDSRVYR": info["year"]})
  return data

# Description: The beginning which pulls and cleans the data from the files?
# Parameters:
#   filepath: (string, input, req) (Description: The file path that contains the file needed)
#   ftype: (string, input, req) (Description: The type of file we are using (Ex. Blood pressure, Demographic, Cholesterol, Glucose))
# Returns: Cleaned dataframe
#

def main(filepath, ftype):
  # Creating dictionaries to correct the labels from our data
  racevar = {1.0: "Mexican American", 2.0: "Other hispanic", 3.0: "NH White", 4.0: "NH black", 5.0: "Other"}
  year = {1.0: 1999, 2.0: 2001, 3.0: 2003, 4.0: 2005, 5.0: 2007, 6.0: 2009, 7.0: 2011, 8.0: 2013, 9.0: 2015, 10.0: 2017}
  dictionaries = {"race": racevar, "year": year}

  # File directory path and creating dataframe
  direct = filepath
  df = pandas.DataFrame()

  # Looping through the files in the directory set above
  for filename in os.listdir(direct):
    # Only selecting the proper file extentions
    if filename.endswith(".XPT"):
      # Making one dataframe to prepare for cleaning
      df = pandas.concat((df, pulldata(f'{direct}/{filename}')), axis=0)
  
  # Cleaning the main dataframe into csv files seperated by file types
  cleaned = cleandata(df, dictionaries)
  cleaned.to_csv(f'/content/data2/cleaned/{ftype}_cleaned.csv')

# Description: Preparing Blood pressure and Demographic dataframe for use when creating the graph
# Parameters: None
# Returns: Merged dataframe of demographic and blood pressure
#

def merge():
  # Reading the cleaned csv file from directory and selecting specific blood pressure columns from the dataframe
  bp = pandas.read_csv('/content/data2/cleaned/BPX_cleaned.csv')
  bp = selectdata(bp, "BPX")

  # Reading the cleaned csv file from directory and selecting specific demographic columns from the dataframe
  demo = pandas.read_csv('/content/data2/cleaned/DEMO_cleaned.csv')
  demo = selectdata(demo, "DEMO")

  # Reading the cleaned csv file from directory and selecting specific cholesterol columns from the dataframe
  chol = pandas.read_csv('/content/data2/cleaned/CHOL_cleaned.csv')
  chol = selectdata(chol, "CHOL")

  # Reading the cleaned csv file from directory and selecting specific glucose columns from the dataframe
  glu = pandas.read_csv('/content/data2/cleaned/GLU_cleaned.csv')
  glu = selectdata(glu, "GLU")

  # Merging our blood pressure, cholesterol and glucose into 1 data frame
  data = pandas.merge(left = demo, right = bp, how = 'inner', on = 'SEQN')
  data = pandas.merge(left = data, right = chol, how = 'left', on = 'SEQN')
  data = pandas.merge(left= data, right = glu, how = 'left', on = 'SEQN')
  data["SDDSRVYR"] = data["SDDSRVYR"].astype('int64') # Changing a float valued column into integers
  return data
  
# Triggering the main function with the file directory and file type
main('/content/data2/demo', 'DEMO')
main('/content/data2/bp', 'BPX')
main('/content/data2/cholesterol', 'CHOL')
main('/content/data2/glucose', 'GLU')

# Creating parameters in a dictionary for use in creating the graphs 
types = {
    # Blood pressure
  "BPXSY1": {
    "graphlabel": "Blood Pressure",
    "gtype": "BP",
  },
  # Cholesterol 
  "LBDLDL": {
    "graphlabel": "Cholesterol (LDL)",
    "gtype": "CHOL",
  },
  # Glucose 
  "LBXGLU": {
    "graphlabel": "Glucose (Diabetes)",
    "gtype": "GLU",
  }
}

#The different graph types used when looping to create graphs
gtypes = ['line', 'bar']

# Looping through the different types of data to send when creating graphs
for i in types:
  # Looping through the types of graph to create a bar and line graph
  for k in gtypes:
    creategraph(merge(), "RIDRETH1", i, "SDDSRVYR", types[i]["graphlabel"], types[i]["gtype"], k)
