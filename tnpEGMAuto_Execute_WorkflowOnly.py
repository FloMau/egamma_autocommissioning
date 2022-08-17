import sys
import ROOT as root
import math
import os
import shutil
import time
from os import listdir
from os.path import isfile, isdir, join

import lib_Python.tool_InfoCollector as collector

#import tnpEGM_AutoComm as tnpAuto

'''
root.gROOT.LoadMacro('tnpEGM_Plotting.C')
root.gROOT.SetBatch(1)
from ROOT import tnpEGM_Plotting
'''










#================
# + Main function
#================
if __name__ == "__main__":
	# + Create and start a clock here
	#--------------------------------
	start_time = time.time()
	
	
	
	
	
	# + Directory containing the list of ntuples
	#-------------------------------------------
	dir_containNtupleList = "/home/longhoa/ROOT_Work/Task_AutoEGCom/Input"
	#dir_containNtupleList = "/home/longhoa/ROOT_Work/Task_AutoEGCom/Input"
	print ("\n")
	print ("  ======================================================================")
	print ("  |                                                                    |")
	print ("  |    EGAMMA - ELECTRON COMMISSIONING AUTOMATION - version 1.0        |")
	print ("  |  ----------------------------------------------------------------  |")
	print ("  |                                                                    |")
	print ("  |    Developer(s):                                                   |")
	print ("  |      1) Shilpi Jain (University of Minnesota)                      |")
	print ("  |         (email: Shilpi.Jain@cern.ch)                               |")
	print ("  |      2) Cao Phuc Long Hoa (National Central University - Taiwan)   |")
	print ("  |         (email: cplhoa89@gmail.com)                                |")
	print ("  |                                                                    |")
	print ("  ======================================================================")
	print ("\n  !!! PROGRAM STARTS !!!\n")
	
	print ("     ====================================================")
	print (" [*] Preparation: Directory to search for list of ntuple:")
	print ("     ====================================================")
	print ("     ||-- \"{:s}\"\n\n\n\n" . format (dir_containNtupleList))
	
	
	
	
	
	# + Collect the list of available lists
	#--------------------------------------
	set_listOfNtuple = []
	
	list_objectFromDir = sorted(listdir(dir_containNtupleList))
	
	for obj_found in list_objectFromDir:
		obj_toCheck = "{:s}/{:s}" . format (dir_containNtupleList, obj_found)
		
		if (isfile(obj_toCheck) and obj_found.startswith("ntupleList")):
			set_listOfNtuple . append (obj_toCheck)
			pass
		pass
	
	print ("     =================================================")
	print (" [*] Preparation: Found [ {:02d} ] lists in the directory:" . format (len(set_listOfNtuple)))
	print ("     =================================================")
	for list_ntuple in set_listOfNtuple:
		print ("     || -- {:s}" . format (list_ntuple))
		pass
	print ("\n\n\n")
	
	
	
	
	
	# + Check the status of the lists
	#--------------------------------
	path_listToIgnore = "/home/longhoa/ROOT_Work/Task_AutoEGCom/Input/info_processedNtupleLists.txt"
	print ("     ================================================")
	print (" [*] Preparation: Searching for processed lists from:")
	print ("     ================================================")
	print ("     ||-- \"{:s}\"\n". format (path_listToIgnore))
	
	# * Collecting processed lists of ntuples
	do_createIgnoreList = False
	
	set_listToIgnore = []
	
	if (isfile(path_listToIgnore)):
		print ("     || -- Ignore list is available, collecting ...")
		
		file_listToIgnore = open (path_listToIgnore, "r")
		lines_toIgnore = file_listToIgnore . readlines()
		
		for line in lines_toIgnore:
			line = line . replace ('\n', '')
			set_listToIgnore . append (line)
			pass
		
		file_listToIgnore . close()
		pass
	else:
		print ("     || -- Ignore list is not available, creating one")
		
		do_createIgnoreList = True
		pass
	
	# * Print notification
	if (len(set_listToIgnore) > 0):
		print ("     || -- Found [ {:02d} ] lists that have already been processed:" . format (len(set_listToIgnore)))
		for list_toIgnore in set_listToIgnore:
			print ("     || -->-- {:s}" . format (list_toIgnore))
			pass
		print ("\n\n\n")
		pass
	else:
		print ("     || -- Skipping information is empty.\n\n\n\n")
		pass
	
	
	
	
	
	# + Remove the lists that has already been processed from the set of lists of ntuples
	#------------------------------------------------------------------------------------
	print ("     ===============================================")
	print (" [*] Preparation: Skimming for unprocessed lists ...")
	print ("     ===============================================")
	
	idx_line = 0
	
	while idx_line < len(set_listOfNtuple):
		do_remove = False
		
		for list_toIgnore in set_listToIgnore:
			if (set_listOfNtuple[idx_line] == list_toIgnore):
				do_remove = True
				break
			pass
		
		if do_remove:
			set_listOfNtuple . remove (set_listOfNtuple[idx_line])
			pass
		else:
			idx_line += 1
			pass
		
		pass
	
	doSkipToTheEnd = True
	if (len(set_listOfNtuple) > 0):
		doSkipToTheEnd = False
		print ("     || -- There are [ {:02d} ] lists to process:" . format (len(set_listOfNtuple)))
		for list_ntuple in set_listOfNtuple:
			print ("     || -->-- {:s}" . format (list_ntuple))
			pass
		print ("\n\n\n")
		pass
	else:
		print ("     || -- All lists are processed\n\n\n\n")
		pass
	
	
	
	if not doSkipToTheEnd:
		# + Get the list of ntuple
		#-------------------------
		print ("     ==============================================")
		print (" [*] Preparation: Collecting ntuple information ...")
		print ("     ==============================================")
		set_targetNtuple    = []
		set_referenceNtuple = []
		
		for list_ntuple in set_listOfNtuple:
			dict_target    = {}
			dict_reference = {}
			
			file_listNtuple = open (list_ntuple, "r")
			lines_listNtuple = file_listNtuple . readlines()
			
			dict_target    = collector . Get_NtuplesInfo (lines_listNtuple, False)
			dict_reference = collector . Get_NtuplesInfo (lines_listNtuple, True)
			
			set_targetNtuple    . append (dict_target)
			set_referenceNtuple . append (dict_reference)
			
			dict_reference = {}
			dict_target = {}
			
			pass
		print ("\n\n\n")
		
		
		
		
		
		# + Process the ntuples
		#----------------------
		# * Target ntuples
		print ("     ==============================")
		print (" [*] Processing: Target ntuples ...")
		print ("     ==============================")
		
		itarget = 0
		for block in set_targetNtuple:
			print ("     || -- Target block: #{:02d} ..." . format (itarget+1))
			print ("     ||-----------------------------")
			for infolist in block:
				if not isinstance (block[infolist], list):
					val = block[infolist]
					content = str(val)
					
					if isinstance(val, int) or isinstance(val, float) or isinstance(val, bool):
						content = "< {} >" . format(val)
						pass
					
					print ("     || -->-- {:10s}: {}" . format (infolist, content))
					pass
				else:
					print ("     || -->-- {:s}:" . format (infolist))
					for info in block[infolist]:
						val = info
						content = str(val)
						
						if isinstance(val, int) or isinstance(val, float) or isinstance(val, bool):
							content = "< {} >" . format (val)
							pass
						
						print ("     || -->-- {:5s}{}".format ("", content))
						pass
					pass
				pass
			
			print ("")
			itarget += 1
			pass
		print ("\n")
		
		
		# * Reference ntuples
		print ("     =================================")
		print (" [*] Processing: Reference ntuples ...")
		print ("     =================================")
		
		iref = 0
		for block in set_referenceNtuple:
			print ("     || -- Reference block: #{:02d} ..." . format (iref+1))
			print ("     ||--------------------------------")
			for infolist in block:
				if not isinstance (block[infolist], list):
					val = block[infolist]
					content = str(val)
					
					if isinstance(val, int) or isinstance(val, float) or isinstance(val, bool):
						content = "< {} >" . format(val)
						pass
					
					print ("     || -->-- {:10s}: {}" . format (infolist, content))
					pass
				else:
					print ("     || -->-- {:s}:" . format (infolist))
					for info in block[infolist]:
						val = info
						content = str(val)
						
						if isinstance(val, int) or isinstance(val, float) or isinstance(val, bool):
							content = "< {} >" . format (val)
							pass
						
						print ("     || -->-- {:5s}{}".format ("", content))
						pass
					pass
				pass
			
			print ("")
			iref += 1
			pass
		print ("\n\n\n")
		
		
		
		
		
		# + Process the plot
		#-------------------
		set_plotsInfo = []
		
		print ("     ==============================")
		print (" [*] Processing: Creating plots ...")
		print ("     ==============================")
		set_plotsInfo = collector . Get_PlotsInfo (set_referenceNtuple, set_targetNtuple)
		
		iblock = 0
		size_plotsInfo = len (set_plotsInfo)
		
		for block in set_plotsInfo:
			iblock += 1
			print ("     || -- Plots block: #{:02d} ..." . format (iblock))
			print ("     ||----------------------------")
			
			for infolist in block:
				print ("     || -->-- {:10s} :" . format (infolist))
				
				for info in block[infolist]:
					val = info
					content = str(val)
					
					if isinstance(val, int) or isinstance(val, float) or isinstance(val, bool):
						content = "< {} >" . format (val)
						pass
					
					print ("     || -->-- {:5s}{}" . format ("", content))
					pass
				pass
			print ("")
			
			pass
		print ("\n\n\n")
		
		# * End of the main condition block
		pass
	
	
	
	
	# + Add the processed lists to the ignore list
	#---------------------------------------------
	if do_createIgnoreList:
		print ("     ==========================================================================")
		print (" [*] Finalizing: New ignoring set is created, adding [ {:02d} ] processed lists ..." . format (len(set_listOfNtuple)))
		print ("     ==========================================================================")
		file_listToIgnore = open (path_listToIgnore, "w")
		
		for list_ntuple in set_listOfNtuple:
			file_listToIgnore . write ("{}\n".format (list_ntuple))
			pass
		file_listToIgnore . close()
		
		pass
	else:
		print ("     =================================================================")
		print (" [*] Finalizing: Adding [ {:02d} ] processed lists to the ignoring set ..." . format (len(set_listOfNtuple)))
		print ("     =================================================================")
		file_listToIgnore = open (path_listToIgnore, "a")
		
		for list_ntuple in set_listOfNtuple:
			file_listToIgnore . write ("{}\n".format (list_ntuple))
			pass
		file_listToIgnore . close()
		
		pass
	pass
