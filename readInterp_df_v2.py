import sys
import regex
import pandas
import os
import datetime
from thefuzz import fuzz

#Initial empty lists
#The items from the OCR'd text
citeItems = []
#A list to hold the names of processed titles from the metadata csv
gldl_titles = []
#A list that will hold the eventual "missing titles"
removed_ones = []

#Use command line arguments to get filename
txt_file = sys.argv[1];

#open/read the files (1st arg after the program call)
#first file is the text version of pdf, second is csv
f = open(txt_file,"r")
gldl_contents = pandas.read_csv("GLRRMeta.csv")

#Clean docs reading of the PDF into usable text
#translate it into a string
rawtext = f.read()
#split the text up into lines (each item is a separate line)
items = rawtext.split("\n")
#Each entry in the OCR'd document has periods separating the fields. This regex breaks each line into a list by periods
#citeItems is a list of lists, each item separated by a period
for x in range(len(items)):
    citeItems.append(regex.split("(?<=[a-z0-9]{2,})\.",items[x]))  
    
#This regex checks for special characters and removes digits and special characters from start of strings and
#converts them to lowercase. citeSub is the list of titles (the first field in each list in citeItems).
for x in citeItems:
    x[0] = regex.split("(?<=.{0,2}[0-9]{1})\s",x[0],1)
    temp = x[0]
    #break off the new list of items from the split
    x.pop(0)
    #insert the items at the appropriate location
    for index,y in enumerate(temp):
        x.insert(index,y)
    #remove whitespace
    for z in x:
        z = z.strip()
    
#A dataframe that will hold the split fields from the read text
citeSub = pandas.DataFrame(citeItems)
citeSub.columns = [str(i) for i in range(0,len(citeSub.columns))]
    
#Read the PUBPLACE column of GLRRMeta (title and author names)
glrr_pubplace = gldl_contents["PUBPLACE"].tolist()
#Extract the titles in the PUBPLACE field, remove whitespace from them, convert them to lowercase.
for x in glrr_pubplace:
    gldl_titles.append((x.split(" /")[0]).strip().lower())

#Check the items in the dataframe (from the metadata file) against the items from the OCR document
#Note the removed titles
for x in gldl_titles:
    if x in citeSub["1"].apply(lambda x: x.lower()):
        citeSub.drop(citeSub["1"].apply(lambda x: x.lower() == x))
        removed_ones.append(x)

#Make a new csv using the filename as a generated term
citeSub.to_csv("missing_titles_" + os.path.splitext(str(txt_file))[0] + ".csv",index = False)

# #Create a list comprehension for titles that have a good chance of matching in token sort
# stragglers = [a for a in citeSub["0"] for b in gldl_titles if fuzz.token_sort_ratio(a,b) > 97]
# #Write it to a CSV
# stragglers_df = pandas.DataFrame(stragglers, columns = ["Titles"])
# stragglers_df.to_csv("stragglers" + os.path.splitext(str(txt_file))[0] + ".csv",index = False)

f.close()