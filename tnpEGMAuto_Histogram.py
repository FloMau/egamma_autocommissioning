# + Usage:
# *python   tnpEGM_commissioningRun2017BUL_DF.py   &> log2017FUL.txt &

import os
from os import listdir
import time

import ROOT
from ROOT import gStyle
from ROOT import gROOT

import Lib_Python.tool_InfoCollector as collector

ROOT.gROOT.SetBatch(True)
import numpy as np 




# + Import function from file
#============================
list_funcUsrDef = []
list_funcUsrDef = collector . Get_listFunction ("UserDefined")

for function in list_funcUsrDef:
	ROOT . gInterpreter . Declare (str(function))
	#print ("  ******  the function is:")
	#print ("{}\n\n" . format(function))
	



# want to include ID cut and SF?
require_ID = False
ID_name = "passingMVA122Xwp80isoV1"
# available IDs: passingCutBasedLoose122XV1, passingCutBasedMedium122XV1, passingCutBasedTight122XV1, passingCutBasedVeto122XV1, passingMVA122Xwp80isoV1, passingMVA122Xwp80noisoV1, passingMVA122Xwp90isoV1, passingMVA122Xwp90noisoV1
WP = "wp80iso"
apply_ID_SF = False
SF_path = "/afs/cern.ch/work/e/egmcom/SFs/2022FG/electron.json"

# + Loop over the tree
#=====================
def Create_Histogram (path_input, isMC, path_PU, tree_PU, dir_hist, path_hist):
	# + Start mini clock
	#-------------------
	time_histStart = time . time()



	# + Global setting
	#-----------------
	ROOT . TH1 . SetDefaultSumw2 (True)
	ROOT . TH1 . AddDirectory (False)



	# + Information for input
	#------------------------
	usephoid = False

	treename = 'tnpEleIDs/fitter_tree'

	if usephoid:
		treename = 'tnpPhoIDs/fitter_tree'
		



	# + Open input file
	#------------------
	print("     ||")
	print("     || [#] Processing file: [ {} ] ..." . format(path_input))

	file_input = ROOT.TFile . Open (path_input, "read")
	tree_input = file_input . Get (treename)

	#
	# print("FILE: ", file_input)
	# print("N entries:", tree_input.GetEntries())
	#
	#

	# + Get PU tree if required
	#--------------------------
	if (path_PU.lower() != "ignore"):
		friendTreeName = tree_PU
		tree_input . AddFriend (friendTreeName, path_PU)
		

	dataFrame = ROOT.RDataFrame(tree_input)

	column_names = dataFrame.GetColumnNames()

	# # print the list of column names
	# for column_name in column_names:
	# 	print(column_name)
	# exit()



	if (path_PU.lower() != "ignore"):
		print ("     ||  +>> PU weight found, getting weight from: [{}.totWeight]" . format(friendTreeName))
		dataFrame = dataFrame.Define ("ev_weight", "{}.totWeight" . format(friendTreeName))
		
	else:
		print ("     ||  +>> No PU weight required, all weights are set to [1.0]")
		dataFrame = dataFrame.Define ("ev_weight", "1.0")
		



	# + Apply the basic cut to shrink the size of the data frame
	#-----------------------------------------------------------
	dataFrame = dataFrame . Filter ("tag_Ele_pt>40  &&  tag_sc_abseta<1.4442  &&  el_et>20  &&  el_sc_abseta<2.5  &&  pair_mass>80  &&  pair_mass<100")

	# adaptions to analyse / validate impact of certain ID and corresponding SF:
	# set apply_ID_SF to False if you don't want to use this 
	if require_ID:
		print("\tWARNING: Requiring ID {}".format(ID_name))
		dataFrame = dataFrame.Filter(ID_name+"==1")
		if apply_ID_SF and isMC:
			print("\tWARNING: Applying the ID SF for {} to MC".format(ID_name))
			# import here since this requires special environments, e.g. LCG103, source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc12-opt/setup.sh
			import correctionlib 
			evaluator = correctionlib.CorrectionSet.from_file(SF_path)["PromptReco-Electron-ID-SF"]

			# trick taken from https://root-forum.cern.ch/t/adding-data-from-an-external-container-to-a-dataframe/46177
			def add_df_column(df, arr_val, name):
				ran=ROOT.TRandom3(0)
				ran_int=ran.Integer(100000000)

				df_size=df.Count().GetValue()
				if arr_val.size != df_size:
					log.error('Array size is different from dataframe size: {}/{}'.format(arr_val.size, df_size))
					raise

				str_ind='''@ROOT.Numba.Declare(['int'], 'int'  )\ndef get_ind_{}_{}(index):\n    if index + 1 > arr_val.size:\n        return 0\n    return index'''.format(name, ran_int)
				str_eva='''@ROOT.Numba.Declare(['int'], 'float')\ndef get_val_{}_{}(index):\n    if index + 1 > arr_val.size:\n        print('Cannot access array at given index')\n        return -1\n    return arr_val[index]'''.format(name, ran_int)

				exec(str_ind, {'ROOT' : ROOT, 'arr_val' : arr_val})
				exec(str_eva, {'ROOT' : ROOT, 'arr_val' : arr_val})

				ROOT.gInterpreter.ProcessLine('int index_df = -1;')

				ind_eva = 'Numba::get_ind_{}_{}(index_df)'.format(name, ran_int)
				fun_eva = 'Numba::get_val_{}_{}(index_df)'.format(name, ran_int)

				df=df.Define(name, 'index_df++; index_df={}; return {};'.format(ind_eva, fun_eva))

				return df

			sf = evaluator.evaluate("2022FG", "sf", WP, dataFrame.AsNumpy(["el_eta"])["el_eta"], dataFrame.AsNumpy(["el_pt"])["el_pt"])
			weight_SF = dataFrame.AsNumpy(["ev_weight"])["ev_weight"] * sf

			# define a new column "my_array" and fill it with the numpy array using the lambda function
			dataFrame = add_df_column(dataFrame, weight_SF, "ev_weight_SF")
		

	# + Get the user-define variables
	#--------------------------------
	list_varUsrDef = []
	list_varUsrDef = collector . Get_listJson("UserDefined/usrDefVars.json")

	for varUsrDef in list_varUsrDef:
		myVar = str(varUsrDef["variable"])
		myForm = str(varUsrDef["formula"])

		#print ("     || **** {:20} = {}" . format (myVar, myForm))

		dataFrame = dataFrame . Define (myVar, myForm)
		



	# + Create path for output
	#-------------------------
	if not os.path.exists(dir_hist):
		print ("     ||  +>> Output directory [ {0} ] is missing, now creating ..." . format (dir_hist))
		os.makedirs (dir_hist)
		
	else:
		print ("     ||  +>> Output directory [ {0} ] is available" . format (dir_hist))
		



	# + Get the filter for creating histogram
	#----------------------------------------
	list_histAll = []

	for obj in listdir ("UserDefined"):
		if obj . startswith ("usrDefHist"):
			pathJson = "UserDefined/{}" . format (obj)

			print ("     ||  +>> Reading json:  {}" . format(pathJson))

			list_histByCat = []
			list_histByCat = collector . Get_listJson(pathJson)

			list_histAll . append (list_histByCat)
			

	# + Create dataframe & fill histograms for each set
	#--------------------------------------------------
	histList = {}

	for ilist in range(len(list_histAll)):
		print ("     ||  +>> Working on histogram set [ #{:02d} ] ..." . format(ilist+1))
		time_set0 = time . time()

		dataFrameSet = dataFrame
		dfFilter = ""

		for info in list_histAll[ilist][0]:
			if "filter" in info:
				dfFilter = str(list_histAll[ilist][0][info])
				print ("     ||      |-- Adding [ {} ]:  {} " . format(info, dfFilter))
				dataFrameSet = dataFrameSet.Filter (dfFilter)

		print ("     ||     [-] Filling [ {:02d} ] histograms..." . format(len(list_histAll[ilist])-1))
		fillHists (dataFrameSet, histList, list_histAll[ilist], isMC)

		time_set1 = time . time()
		time_set = time_set1 - time_set0
		print ("     ||     [-] Set [ #{:02d} ] done in: [ {:.1f} ] seconds" . format(ilist+1, time_set))
		

	time_histFill = time . time()
	time_allset = time_histFill-time_histStart
	print ("     ||  +>> Filling the histograms from all the set takes [ {:.1f} ] seconds" . format(time_allset))




	# + Create output root file
	#--------------------------
	namefile_isMC = ["DT", "MC"]

	file_output = ROOT.TFile("{}".format (path_hist), "RECREATE")
	file_output . cd()

	for key in histList:
		histList[key] . Write()
		

	file_output . Write()
	file_output . Close()

	print ("     ||  +>> The histograms have been saved to:  {}" . format (path_hist))

	










# + Fill histograms using RDataFrame
#===================================
def fillHists (dataFrame, histList, list_histByCat, isMC):
	nHistInCat = len(list_histByCat)

	regECAL = list_histByCat[0]["regECAL"]

	for idict in range(1, nHistInCat):
		# * Get histogram info
		name_hist  = "{}_{}" . format (list_histByCat[idict]["histogram"], regECAL)
		title_hist = "{} ({})" . format (list_histByCat[idict]["titleX"], regECAL.replace("_","-"))
		name_var   = "{}" . format (list_histByCat[idict]["variable"])
		nBins      = int(list_histByCat[idict]["nBins"])
		binMin     = float(list_histByCat[idict]["binMin"])
		binMax     = float(list_histByCat[idict]["binMax"])

		time_beg = time.time()
		# print("\n\n", name_hist, title_hist, nBins, binMin,  binMax, name_var, "\n\n")
		if require_ID and apply_ID_SF and isMC:
			histList[name_hist] = dataFrame.Histo1D ((name_hist, title_hist, nBins, binMin,  binMax),  name_var, "ev_weight_SF")
		else:
			histList[name_hist] = dataFrame.Histo1D ((name_hist, title_hist, nBins, binMin,  binMax),  name_var, "ev_weight")
		time_end = time.time()
		time_proc = time_end - time_beg
		print ("     ||      |-- Spent [ {:.1f} ] seconds to fill:  {}" . format(time_proc, name_hist))
		

	










# + Merge the histograms
#=======================
def Merge_Histogram (dict_listHist):
	time_merge0 = time.time()
	print("     ||")
	print ("     || [#] Combining activated, merging files ...")

	nHist = len(dict_listHist["pathHist"])

	merger = ROOT.TFileMerger ()

	for ihist in range(nHist-1):
		path_hist = "{}" . format (dict_listHist["pathHist"][ihist])
		print ("     ||  +>> Adding to merger: [ {} ]".format(path_hist))
		merger . AddFile (path_hist, False)
		

	path_histtarget = "{}" . format (dict_listHist["pathHist"][nHist-1])
	print ("     ||  +>> Output is set to: [ {} ]".format(path_histtarget))
	merger . OutputFile (path_histtarget, "recreate")

	merger . Merge()

	time_merge1 = time.time()
	time_merge = time_merge1 - time_merge0
	print ("     ||  +>> Files have been merged in: [ {} ] seconds".format(time_merge))
	



######end of the function
