from thefuzz import fuzz

name1 = "Nick Rosato II"
name2 = "Nick Rsoato II"

print("Similarity score:", fuzz.ratio(name1,name2)) 