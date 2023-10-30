import sys
import regex
import pandas
from thefuzz import fuzz

#Initial empty lists
#The items from the OCR'd text
citeItems = []
#A list to hold the names of processed titles from the GLRRMeta csv
gldl_titles = []
#A list that will hold the eventual "missing titles"
removed_ones = []

#open/read the files (1st arg after the program call)
#first file is the text version of pdf, second is csv
f = open(sys.argv[1],"r")
gldl_contents = pandas.read_csv("GLRRMeta.csv")

#cleaning the google docs reading of the PDF into usable text
#translate it into a string
rawtext = f.read()
#split the text up into lines (each item is a separate line)
items = rawtext.split("\n")
#Each entry in the OCR'd document has periods separating the fields. This regex breaks each line into a list by periods
#citeItems is effectively this list of lists
for x in range(len(items)):
    citeItems.append(regex.split("(?<=[a-z0-9]{4,})\.",items[x]))
    
#This regex checks for special characters and removes digits and special characters from start of strings and
#converts to lowercase. citeSub is the list of titles (the first field in each list in citeItems).
for x in citeItems:
    x[0] = (regex.sub("^.{0,2}[0-9]+\s{1}","",x[0],1).lower())
    
#A dataframe that will hold the split fields from CGLASInterp.txt
citeSub = pandas.DataFrame(citeItems)
citeSub.columns = [str(i) for i in range(0,len(citeSub.columns))]
print(citeSub)
    
#Read the PUBPLACE column of GLRRMeta (title and author names)
glrr_pubplace = gldl_contents["PUBPLACE"].tolist()
#Extract the titles in the PUBPLACE field, remove whitespace from them, convert them to lowercase.
for x in glrr_pubplace:
    gldl_titles.append((x.split(" /")[0]).strip().lower())
   

#How to drop the specific row based on index
for x in gldl_titles:
    if x in citeSub["0"]:
        citeSub.drop(citeSub["0"] == x)
        removed_ones.append(x)
        
#Make a new csv
citeSub.to_csv("missing_titles.csv",index = False)

#Create a list comprehension for titles that have a good chance of matching in token sort
stragglers = [a for a in citeSub["0"] for b in gldl_titles if fuzz.token_sort_ratio(a,b) > 97]
#Write it to a CSV
stragglers_df = pandas.DataFrame(stragglers, columns = ["Titles"])
stragglers_df.to_csv("stragglers.csv",index = False)

#NEXT STEPS:
#Does the order of the titles matter for token sort comparison

#Is it worth it to split up the metadata in the OCR'd text to preserve authors etc (probably)

f.close()

# TO DO:
# CLEAN THE CODE

# Notes:
# Positive lookbehind for periods with four or more alphanumeric characters: (?<=[a-z0-9]{4,})\.
# Maybe use token match as threshold not to check...
# Or play with what is acceptable threshold (> 50? > 20?)

# Leftovers:
    #check matches against csv, remove matches
    #think this checks csv, but I want to note the missing titles from that document
    # for x in citeSub:
        # gldl_contents_lower.drop(gldl_contents_lower[gldl_contents_lower["PUBPLACE"] == x].index, inplace = True)

    # #write missing titles to csv, filename: missingtitles.csv
    # gldl_contents_lower.to_csv("missingtitles.csv", index = False)

    # #create a copy of df
    # gldl_contents_lower = gldl_contents
    # #alter the titles to be appropriate
    # gldl_contents_lower["PUBPLACE"] = gldl_contents["PUBPLACE"].apply(lambda x: (x.split(" /")[0]).strip().lower())
    # #print(gldl_contents_lower["PUBPLACE"].tolist())

    #list overlap
    #Something to point to -- this list has more overlap than the supposedly missing titles
    # print(len(list(set(gldl_titles) & set(citeSub))))
# Leftovers: