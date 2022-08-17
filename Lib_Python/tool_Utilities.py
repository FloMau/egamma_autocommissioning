import sys
import math
import os
import json
import shutil






#========================================
# + Selective combination of split string
#========================================
#   Join multiple parts of a string splitted by multiple delimiters
def Join_SplittedString (text_toSplit = "", list_delimiter="", indices_toJoin = [], char_connectWord = []):
	# + Return the original string if the delimiter is empty
	#-------------------------------------------------------
	if list_delimiter == "":
		return ""
	
	
	
	# + If you don't have enough joining characters, the last character in your list will be reused
	#----------------------------------------------------------------------------------------------
	if len(char_connectWord) < len(indices_toJoin)-1:
		char_toAppend = ""
		if len(char_connectWord)>0:
			char_toAppend = char_connectWord[-1]
			pass
		
		for idx in range(len(indices_toJoin)-1 - len(char_connectWord)):
			char_connectWord . append (char_toAppend)
			pass
		
		pass
	
	
	
	# + Split the string
	#-------------------
	# * First replace the different delimiters by a common one
	for deli in list_delimiter:
		text_toSplit = text_toSplit . replace (deli, "<deli>")
		#print (" text after replace: {}" . format(text_toSplit))
		pass
	
	# * Second, split the string
	list_splittedStr = text_toSplit . split ("<deli>")
	
	
	
	# + Combine the required parts
	#-----------------------------
	result = list_splittedStr[indices_toJoin[0]]
	
	for idx in range(1, len(indices_toJoin)):
		result += char_connectWord[idx-1]
		result += list_splittedStr[indices_toJoin[idx]]
		pass
	
	return result
