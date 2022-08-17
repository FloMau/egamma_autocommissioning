import sys
import math
import os
import json
import shutil
from os import listdir
from os.path import isfile, isdir, join










#=============================
# + Check if a string is float
#=============================
def isFloat (value):
	try:
		float(value)
		return True
	except ValueError:
		return False
	pass










#=============================
# + Check if a string is float
#=============================
def isInt (value):
	try:
		int(value)
		return True
	except ValueError:
		return False
	pass










#============================================
# + Extract ntuple information from the block
#============================================
def Get_NtuplesInfo (lines, isRef):
	# + The variable for storing information
	#---------------------------------------
	# * Variable name and value
	var_name  = ""
	var_value = ""
	var_array = []

	# * The dict
	dict_listInfo = {}



	# + Sufix to select reference or target
	#--------------------------------------
	sufix = "target"
	if isRef:
		sufix = "reference"
		pass

	print ("     || -- Searching for <ntupe_{}>". format (sufix))



	# + Loop through the lines
	#-------------------------
	# * Decision: read block
	doReadBlock = False
	doAddInfo   = False
	stopLoop    = False

	iline = 0

	#while (iline < len(lines)):
	for line in lines:
		#line = lines[iline] . strip ()
		line = line . strip ()

		blockstart = "<ntuple_{}>"  . format (sufix)
		blockend   = "</ntuple_{}>" . format (sufix)

		if (blockstart in line):
			doReadBlock = True
			continue

		if (blockend in line):
			if (len(var_array) > 0):
				dict_listInfo[var_name] = var_array
				var_array = []
				pass

			break

		if len(line.split(":")) > 1:
			if (len(var_array) > 0):
				dict_listInfo[var_name] = var_array
				var_array = []
				pass

			var_name  = line.split(":")[0].strip()
			var_value = line.split(":")[1].strip()

			if isInt (var_value):
				var_value = int(var_value)
				pass
			elif isFloat (var_value):
				var_value = float(var_value)
				pass
			elif "{:s}".format(str(var_value)).lower() == "true":
				var_value = True
				pass
			elif "{:s}".format(str(var_value)).lower() == "false":
				var_value = False
				pass

			if var_value != "":
				dict_listInfo[var_name] = var_value
				continue
			else:
				continue

			pass

		if line.startswith("$"):
			content = line.split("$")[1].strip()

			if isInt (content):
				content = int(content)
				pass
			elif isFloat (content):
				content = float(content)
				pass
			elif "{:s}".format(str(content)).lower() == "true":
				content = True
				pass
			elif "{:s}".format(str(content)).lower() == "false":
				content = False
				pass

			var_array . append (content)
			continue

		iline += 1

		pass

	# * Add directory for histograms
	dir_hist = "Output/EGM_Commissioning_Electron/"
	dir_hist += "Hist_{}{}/" . format (dict_listInfo["reproc"], dict_listInfo["year"])
	dir_hist += "{}/" . format (dict_listInfo["version"])
	dict_listInfo["dirHist"] = dir_hist

	# * Add path to histograms
	list_pathHist = []

	for run in dict_listInfo["runPeriod"]:
		path_hist = dir_hist

		#if (dict_listInfo["isMC"] == "false"):
		if not (dict_listInfo["isMC"]):
			path_hist += "histDT_{}run{}.root" . format (dict_listInfo["year"], run)
			pass
		else:
			path_hist += "histMC_{}run{}.root" . format (dict_listInfo["year"], run)
			pass

		list_pathHist . append (path_hist)
		pass

	# * Add the combine histogram if required
	if (dict_listInfo["doCombine"]):
		# * Histograms
		name_run = dict_listInfo["runPeriod"][0]

		for run in dict_listInfo["runPeriod"]:
			if run == name_run:
				continue

			name_run += "-{}" . format (run)
			pass

		path_hist = dir_hist

		#if (dict_listInfo["isMC"] == "false"):
		if not (dict_listInfo["isMC"]):
			path_hist += "histDT_{}run{}.root" . format (dict_listInfo["year"], name_run)
			pass
		else:
			path_hist += "histMC_{}run{}.root" . format (dict_listInfo["year"], name_run)
			pass

		list_pathHist . append (path_hist)

		# * Luminosity
		list_lumi = []
		lumiTot = 0.0

		for lumi in dict_listInfo["luminosity"]:
			lumiTot += lumi
			list_lumi . append(lumi)
			pass

		list_lumi . append (lumiTot)

		dict_listInfo["luminosity"] = list_lumi

		pass

	dict_listInfo["pathHist"] = list_pathHist


	return dict_listInfo










#============================
# + Collect plots information
#============================
def Get_PlotsInfo (set_referenceNtuple, set_targetNtuple):
	set_plotsInfo = []

	size_reference = len (set_referenceNtuple)
	size_target    = len (set_targetNtuple)

	# * Check if the 2 set have the same size
	if (size_reference != size_target):
		return set_plotsInfo

	# * Loop over the sets
	idict = 0

	while (idict < size_reference):
		dict_plotsInfo = {}

		nameRef_DTorMC = "MC" if set_referenceNtuple[idict]["isMC"] else "DT"
		nameTar_DTorMC = "MC" if set_targetNtuple[idict]["isMC"] else "DT"

		path_ref = []
		lumi_ref = []
		isMC_ref = []
		leg_ref  = []
		year_ref = []

		path_tar = []
		lumi_tar = []
		isMC_tar = []
		leg_tar  = []
		year_tar = []

		dir_plot   = []
		path_plot  = []
		name_ratio = []

		nTarget    = len (set_targetNtuple[idict]["pathHist"])
		nReference = len (set_referenceNtuple[idict]["pathHist"])
		# + Ignore the block if the number of histograms is not equal
		#------------------------------------------------------------
		if (nTarget != nReference):
			idict += 1
			dict_plotsInfo["pathRef"]   = path_ref
			dict_plotsInfo["lumiRef"]   = lumi_ref
			dict_plotsInfo["isMCRef"]   = isMC_ref
			dict_plotsInfo["legRef"]    = leg_ref
			dict_plotsInfo["yearRef"]   = year_ref

			dict_plotsInfo["pathTar"]   = path_tar
			dict_plotsInfo["lumiTar"]   = lumi_tar
			dict_plotsInfo["isMCTar"]   = isMC_tar
			dict_plotsInfo["legTar"]    = leg_tar
			dict_plotsInfo["yearTar"]   = year_tar

			dict_plotsInfo["dirPlot"]   = dir_plot
			dict_plotsInfo["pathPlot"]  = path_plot
			dict_plotsInfo["nameRatio"] = name_ratio

			set_plotsInfo . append (dict_plotsInfo)
			continue



		# + Process the information otherwise
		#------------------------------------
		# * Add the path of the histogram
		ihist = 0
		nHist = len (set_referenceNtuple[idict]["pathHist"])

		while (ihist < nHist):
			# * Get the path to the histogram
			path_ref . append (set_referenceNtuple[idict]["pathHist"][ihist])
			lumi_ref . append (set_referenceNtuple[idict]["luminosity"][ihist])
			isMC_ref . append (set_referenceNtuple[idict]["isMC"])
			year_ref . append (set_referenceNtuple[idict]["year"])
			path_tar . append (set_targetNtuple[idict]["pathHist"][ihist])
			lumi_tar . append (set_targetNtuple[idict]["luminosity"][ihist])
			isMC_tar . append (set_targetNtuple[idict]["isMC"])
			year_tar . append (set_targetNtuple[idict]["year"])


			# * Get the dirs to the plots
			dirtmp = "Output/EGM_Commissioning_Electron/"
			dirtmp += "Plot_"
			dirtmp += "{}-{}-{}" . format (
					set_targetNtuple[idict]["reproc"],
					set_targetNtuple[idict]["year"],
					set_targetNtuple[idict]["version"])
			dirtmp += "_vs_"
			dirtmp += "{}-{}-{}/" . format (
					set_referenceNtuple[idict]["reproc"],
					set_referenceNtuple[idict]["year"],
					set_referenceNtuple[idict]["version"])
			dirtmp += "VariableName/"

			# Get the paths to the plots
			pathtmp = dirtmp

			#if (set_referenceNtuple[idict]["doCombine"]=="true") and (ihist==nHist-1):
			if (set_referenceNtuple[idict]["doCombine"]) and (ihist==nHist-1):
				name_run = "runCombine{}-" . format (nameTar_DTorMC)
				for run in set_targetNtuple[idict]["runPeriod"]:
					name_run += "{}" . format (run)
					pass

				name_run += "_vs_"
				pathtmp += "plot_{}" . format (name_run)

				name_run = "runCombine{}-" . format (nameRef_DTorMC)
				for run in set_referenceNtuple[idict]["runPeriod"]:
					name_run += "{}" . format (run)
					pass

				pathtmp += "{}_*.png" . format (name_run)

				pass
			else:
				name_run = "run{}-{}" . format (
						nameTar_DTorMC,
						set_targetNtuple[idict]["runPeriod"][ihist])
				name_run += "_vs_"
				name_run += "run{}-{}" . format (
						nameRef_DTorMC,
						set_referenceNtuple[idict]["runPeriod"][ihist])

				pathtmp += "plot_{}_*.png" . format (name_run)

				pass

			dir_plot . append (dirtmp)
			path_plot . append (pathtmp)

			# * Get the legend for each histogram
			legend_ref = set_referenceNtuple[idict]["legend"]
			legend_tar = set_targetNtuple[idict]["legend"]
			leg_ref . append (legend_ref)
			leg_tar . append (legend_tar)

			# * Get the axis name
			nameratio = ""
			if (set_referenceNtuple[idict]["isMC"] != set_targetNtuple[idict]["isMC"]):
				#nameratio = "MC" if (set_targetNtuple[idict]["isMC"]=="true") else "Data"
				nameratio = "MC" if (set_targetNtuple[idict]["isMC"]) else "Data"
				nameratio += "/"
				#nameratio += "MC" if (set_referenceNtuple[idict]["isMC"]=="true") else "Data"
				nameratio += "MC" if (set_referenceNtuple[idict]["isMC"]) else "Data"

				pass
			else:
				nameratio = "{:s}" . format (set_targetNtuple[idict]["reproc"])
				nameratio += "/"
				nameratio += "{:s}" . format (set_referenceNtuple[idict]["reproc"])

				pass

			name_ratio . append (nameratio)

			ihist += 1
			pass

		dict_plotsInfo["pathRef"] = path_ref
		dict_plotsInfo["lumiRef"] = lumi_ref
		dict_plotsInfo["isMCRef"] = isMC_ref
		dict_plotsInfo["legRef"]  = leg_ref
		dict_plotsInfo["yearRef"] = year_ref

		dict_plotsInfo["pathTar"] = path_tar
		dict_plotsInfo["lumiTar"] = lumi_tar
		dict_plotsInfo["isMCTar"] = isMC_tar
		dict_plotsInfo["legTar"]  = leg_tar
		dict_plotsInfo["yearTar"] = year_tar

		dict_plotsInfo["dirPlot"]   = dir_plot
		dict_plotsInfo["pathPlot"]  = path_plot
		dict_plotsInfo["nameRatio"] = name_ratio

		set_plotsInfo . append (dict_plotsInfo)

		idict += 1
		pass

	return set_plotsInfo











#=========================
# + Get function from file
#=========================
def Get_listFunction (dir_toFunctions):
	list_function = []

	list_objectFromDir = listdir(dir_toFunctions)

	# + Serach for the files defining the functions
	#----------------------------------------------
	for obj in list_objectFromDir:
		# * The file name must start with "func"
		if not (obj.startswith("usrDefFunc")):
			continue

		# * The string for storing the function
		func = ""

		path_func = "{:s}/{:s}" . format (dir_toFunctions, obj)
		file_func = open (path_func, "r")
		lines = file_func . readlines()

		for line in lines:
			if line . startswith ("//"):
				continue

			func += line
			pass

		list_function . append (func)

		pass

	return list_function











#=========================
# + Get variable from file
#=========================
def Get_listJson (path_toJson):
	list_jsonObj = []

	file_json = open (path_toJson, "r")

	lines_json = file_json . readlines()


	# + Read line to get the blocks
	#------------------------------
	block_json = ""

	for line in lines_json:
		#line = line . replace ("\n", "")

		if line . endswith("}\n"):
			block_json += line
			list_jsonObj . append (block_json)
			block_json = ""
			continue

		block_json += line

		pass


	# + Get the dict from the json block
	#-----------------------------------
	list_dictObj = []

	for jsonObj in list_jsonObj:
		#print (" *** < {} > ***\n\n" . format (jsonObj))
		dicttmp = json . loads (jsonObj)
		list_dictObj . append (dicttmp)
		pass

	return list_dictObj










#=========================
# + Get list of histograms
#=========================
def Get_listHist (file_hist, myClass):
	list_nameHist = []

	list_key = file_hist.GetListOfKeys()

	for key in list_key:
		name_class = str(key.GetClassName())
		name_obj   = str(key.GetName())

		if str(myClass) in name_class:
			list_nameHist . append (name_obj)
			pass
		pass

	return list_nameHist
