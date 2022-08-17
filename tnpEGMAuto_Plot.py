import sys
import math
import shutil
import time

import os
from os import listdir
from os.path import isfile, isdir, join

import ROOT as myroot
from ROOT import gStyle
from ROOT import gROOT

import Lib_Python.tool_InfoCollector as collector




# + Global value
#===============
percentDist = 0.70
percentRate = 0.30

ratioPad = (percentDist/percentRate)





# + Visualization setup for distribution histogram
#=================================================
def Characterize_histDist (hist, colour_fill, style_fill, colour_mark, style_mark, nameXaxis):
	# + Global visual setting
	#------------------------
	hist . SetTitle ("")
	hist . SetLineColor (colour_mark)
	hist . SetLineWidth (1)
	hist . SetMarkerColor (colour_mark)
	hist . SetMarkerStyle (style_mark)
	hist . SetMarkerSize (0.75)
	hist . SetFillColor (colour_fill)
	hist . SetFillStyle (style_fill)


	# + Get the title for Y axis
	#---------------------------
	nameYaxis = ""
	widthBinX = float((hist.GetXaxis().GetXmax() - hist.GetXaxis().GetXmin()) / hist.GetNbinsX())
	tmp = widthBinX

	nPow = 0
	while (tmp < 1.0):
		tmp *= 10
		nPow += 1
		pass

	widthBinX = round (widthBinX, nPow)
	unitY = ""

	if "GeV" in nameXaxis:
		unitY = " GeV"
		pass
	if "rad" in nameYaxis:
		unitY = " rad"
		pass

	nameYaxis = "Events / {}{:s}" . format (widthBinX, unitY)


	# + Axes settings
	#----------------
	hist . GetXaxis() . SetTitle       ("")
	hist . GetXaxis() . SetTitleFont   (42)
	hist . GetXaxis() . SetTitleSize   (0.0)
	hist . GetXaxis() . SetTitleOffset (0.4)
	hist . GetXaxis() . SetLabelSize   (0.0)
	hist . GetXaxis() . SetLabelOffset (0.0)

	hist . GetYaxis() . SetTitle       (nameYaxis)
	hist . GetYaxis() . SetMaxDigits   (4)
	hist . GetYaxis() . SetTitleFont   (42)
	hist . GetYaxis() . SetTitleSize   (0.055)
	hist . GetYaxis() . SetTitleOffset (0.480*ratioPad)
	hist . GetYaxis() . SetLabelSize   (0.045)
	hist . GetYaxis() . SetLabelOffset (0.003)

	pass





# + Visualization setup for ratio histogram
#==========================================
def Characterize_histRatio (hist, colour_fill, style_fill, colour_mark, style_mark, nameXaxis, nameYaxis):
	# + Global visual setting
	#------------------------
	hist . SetTitle ("")
	hist . SetLineColor (colour_mark)
	hist . SetLineWidth (1)
	hist . SetMarkerColor (colour_mark)
	hist . SetMarkerStyle (style_mark)
	hist . SetMarkerSize (0.75)
	hist . SetFillColor (colour_fill)
	hist . SetFillStyle (style_fill)


	# + Axes settings
	#----------------
	hist . GetXaxis() . SetTitle       (nameXaxis)
	hist . GetXaxis() . SetTitleFont   (42)
	hist . GetXaxis() . SetTitleSize   (0.055*ratioPad)
	hist . GetXaxis() . SetTitleOffset (0.900)
	hist . GetXaxis() . SetLabelSize   (0.045*ratioPad)
	hist . GetXaxis() . SetLabelOffset (0.007*ratioPad)

	hist . GetYaxis() . SetTitle       (nameYaxis)
	hist . GetYaxis() . SetTitleFont   (42)
	hist . GetYaxis() . SetTitleSize   (0.055*ratioPad)
	hist . GetYaxis() . SetTitleOffset (0.480)
	hist . GetYaxis() . SetLabelSize   (0.045*ratioPad)
	hist . GetYaxis() . SetLabelOffset (0.003*ratioPad)
	hist . GetYaxis() . SetNdivisions  (505)
	hist . GetYaxis() . SetRangeUser   (-0.2, 2.2)

	pass





# + Get the ratio histogram
#==========================
def Get_histRatio (hist_tar, hist_ref):
	hist_ratio = hist_tar . Clone()
	hist_ratio . Divide(hist_tar, hist_ref)

	return hist_ratio






# + Main script to create plots
#==============================
def Create_Plot (dict_plotBlock):
	myroot.gErrorIgnoreLevel = myroot.kError
	myroot.gErrorIgnoreLevel += myroot.kBreak
	myroot.gErrorIgnoreLevel += myroot.kSysError
	myroot.gErrorIgnoreLevel += myroot.kFatal

	myroot . gStyle . SetOptStat (0)




	# + Loop over the input histograms to create plots
	#-------------------------------------------------
	nHist = len(dict_plotBlock["pathTar"])

	for ihist in range(nHist):
		# + Get the basic info
		#---------------------
		path_histTar = dict_plotBlock["pathTar"][ihist]
		isMC_tar     = dict_plotBlock["isMCTar"][ihist]
		lumi_tar     = dict_plotBlock["lumiTar"][ihist]
		leg_tar      = dict_plotBlock["legTar"][ihist]
		year_tar     = dict_plotBlock["yearTar"][ihist]

		path_histRef = dict_plotBlock["pathRef"][ihist]
		isMC_ref     = dict_plotBlock["isMCRef"][ihist]
		lumi_ref     = dict_plotBlock["lumiRef"][ihist]
		leg_ref      = dict_plotBlock["legRef"][ihist]
		year_ref     = dict_plotBlock["yearRef"][ihist]

		name_ratio = dict_plotBlock["nameRatio"][ihist]
		dir_plot   = dict_plotBlock["dirPlot"][ihist]
		path_plot  = dict_plotBlock["pathPlot"][ihist]

		print ("     ||")
		print ("     ||-- Reading histograms from period [ #{:02d} ]" . format (ihist+1))
		print ("     ||   | Target:    {}" . format (path_histTar))
		print ("     ||   | Reference: {}" . format (path_histRef))





		# + Open root file to read histogram
		#-----------------------------------
		file_histTar = myroot.TFile . Open (path_histTar, "read")
		file_histRef = myroot.TFile . Open (path_histRef, "read")

		list_nameHist = collector . Get_listHist (file_histTar, "TH1D")

		for name_hist in list_nameHist:
			print ("     || [#] Variable name: {}" . format(name_hist))

			# + Get histogram from file
			#--------------------------
			# * Read histogram
			file_histTar . cd()
			hist_tar = file_histTar . Get(name_hist)

			file_histRef . cd()
			hist_refVal = file_histRef . Get(name_hist)
			hist_refErr = hist_refVal . Clone()

			# * Remove the binding to files
			hist_tar . SetDirectory (0)
			hist_refVal . SetDirectory (0)
			hist_refErr . SetDirectory (0)

			nameXaxis = hist_tar.GetTitle()

			# * Scale histogram if required
			normFactor = 1.0
			intTar = hist_tar.Integral()
			intRef = hist_refVal.Integral()

			if intTar!=0 and intRef!=0:
				normFactor = intTar/intRef
				pass

			#print ("     ||        Normalized by: {}".format(normFactor))

			if (normFactor < 1.0):
				hist_refErr . Scale (normFactor)
				hist_refVal . Scale (normFactor)
				print ("     ||  +>>  Normalized reference by: {}".format(normFactor))
				pass
			else:
				hist_tar . Scale (1/normFactor)
				print ("     ||  +>>  Normalized target by: {}".format(1/normFactor))
				pass




			# + Get ratio histogram
			#----------------------
			hist_ratVal = Get_histRatio (hist_tar, hist_refVal)
			hist_ratErr = hist_refVal . Clone()

			for ibin in range(hist_ratErr.GetNbinsX()):
				bin_orgErr = hist_ratErr.GetBinError(ibin+1)
				bin_orgCon = hist_ratErr.GetBinContent(ibin+1)

				bin_newErr = 0.0
				bin_newCon = 1.0

				if bin_orgCon > 0:
					bin_newErr = bin_orgErr/bin_orgCon
					pass

				hist_ratErr . SetBinContent (ibin+1, bin_newCon)
				hist_ratErr . SetBinError   (ibin+1, bin_newErr)

				pass



			# + Characterize histogram
			#-------------------------
			Characterize_histDist (hist_tar,    myroot.kBlack,    1001, myroot.kBlack,    20, nameXaxis)
			Characterize_histDist (hist_refVal, myroot.kOrange-4, 1001, myroot.kOrange-4,  1, nameXaxis)
			Characterize_histDist (hist_refErr, myroot.kOrange+7, 3144, myroot.kOrange+7,  1, nameXaxis)

			Characterize_histRatio (hist_ratVal, myroot.kBlack,    1001, myroot.kBlack,    20, nameXaxis, name_ratio)
			Characterize_histRatio (hist_ratErr, myroot.kOrange+7, 3144, myroot.kOrange+7,  1, nameXaxis, name_ratio)

			print ("     ||  +>>  Visualization has been setup")


			# + Draw histogram
			#-----------------
			for isLog in range(2):
				#print ("     ||    [+]  Creating log scale: {}" . format(bool(isLog)))
				# + Set maximum Y
				#----------------
				heightMax = max (hist_tar.GetMaximum(), hist_refVal.GetMaximum())
				heightMin = min (hist_tar.GetMinimum(), hist_refVal.GetMinimum()) + 1e-2 #1e-2 to avoid math error in log_10(0)
				multFactor = 1.0
				try: # may fail for odd values
					if (intTar!=0) and (intRef!=0):
						if "rad" in nameXaxis:
							multFactor = pow(10, 0.9*(math.log10(heightMax)-math.log10(heightMin))) if (isLog) else 1.8
							pass
						else:
							multFactor = pow(10, 1.25*(math.log10(heightMax)-math.log10(heightMin)))/heightMax if (isLog) else 1.5
							if isLog and multFactor <10:
								multFactor = 10
							if isLog and multFactor > 100:
								multFactor = 100
							pass
						pass
				except:
					multFactor = 100 if isLog else 1.5

				print("\n", multFactor)

				hist_tar    . SetMaximum (heightMax*multFactor)
				hist_refVal . SetMaximum (heightMax*multFactor)
				hist_refErr . SetMaximum (heightMax*multFactor)



				# + Create canvas
				#----------------
				# * Canvas
				name_canvas = path_plot . split ("/")[-1]

				if (isLog):
					name_canvas = name_canvas . replace ("plot_", "canvasLog_")
					pass
				else:
					name_canvas = name_canvas . replace ("plot_", "canvasLinear_")
					pass

				name_canvas = name_canvas . replace ("_*.png", "_{}".format(name_hist))

				#canvas = myroot.TCanvas (name_canvas, "", 600, 600)
				canvas = myroot.TCanvas ("canvas", "", 600, 600)
				print ("     ||  +>>  Created canvas with name [ {} ]" . format (name_canvas))

				# * Pad for distribution
				canvas . cd()
				pad1 = myroot.TPad ("pad1", "", 0.0, 0.3, 1.0, 1.0)
				pad1 . SetLeftMargin   (0.13)
				pad1 . SetRightMargin  (0.05)
				pad1 . SetTopMargin    (0.08)
				pad1 . SetBottomMargin (0.02)
				pad1 . SetTicks (1, 1)
				pad1 . SetLogy  (isLog)
				pad1 . Draw()
				pad1 . cd()
				print ("     ||     |-> Pad 1 done")

				# * Draw histogram for distribution
				hist_refVal . Draw("hist")
				hist_refErr . Draw("same e2")
				hist_tar    . Draw("same ep")

				# * Draw legend
				legend = myroot.TLegend (0.62, 0.65, 0.91, 0.89)
				legend . SetTextFont (42)
				legend . SetTextSize (0.055)
				legend . SetFillColorAlpha (0, 0.75)
				legend . SetLineColorAlpha (0, 0.75)
				legend . AddEntry (hist_tar,    "{}".format(leg_tar), "ep")
				legend . AddEntry (hist_refVal, "{}".format(leg_ref),  "f")
				legend . AddEntry (hist_refErr, "Stat. unc.",            "f")
				legend . Draw ("same")

				texLogo = myroot.TLatex()
				texLogo . SetNDC()
				texLogo . SetTextFont (42)
				texLogo . SetTextSize (0.07)
				texLogo . DrawLatex (0.18, 0.82, "#bf{CMS}")


				texLogo = myroot.TLatex()
				texLogo . SetNDC()
				texLogo . SetTextFont (42)
				texLogo . SetTextSize (0.05)
				texLogo . DrawLatex (0.29, 0.82, "#it{Preliminary}")


				str_lumi = ""
				# if (year_ref != year_tar):
				# 	str_lumi = "{:.2f} fb^{{-1}} {} vs {:.2f} fb^{{-1}} {} (13.6 TeV)" . format (lumi_tar, year_tar, lumi_ref, year_ref)
				# 	pass
				# else:
				# 	if (lumi_tar != lumi_ref):
				# 		str_lumi = "{:.2f} fb^{{-1}} vs {:.2f} fb^{{-1}} {} (13.6 TeV)" . format (lumi_tar, lumi_ref, year_ref)
				# 		pass
				# 	else:
				# 		str_lumi = "{:.2f} fb^{{-1}} {} (13.6 TeV)" . format (lumi_ref, year_ref)
				# 		pass
				# 	pass
				str_lumi = "{:.2f} fb^{{-1}} {} (13.6 TeV)" . format (lumi_tar, year_tar)
				texLumi = myroot.TLatex()
				texLumi . SetNDC()
				texLumi . SetTextFont (42)
				texLumi . SetTextSize (0.055)
				texLumi . SetTextAlign (31)
				texLumi . DrawLatex (0.955, 0.935, "{}".format(str_lumi))

				# * pad for ratio
				canvas . cd()
				pad2 = myroot.TPad ("pad2", "", 0.0, 0.0, 1.0, 0.3)
				pad2 . SetLeftMargin   (0.13)
				pad2 . SetRightMargin  (0.05)
				pad2 . SetTopMargin    (0.01)
				pad2 . SetBottomMargin (0.30)
				pad2 . SetTicks (1, 1)
				pad2 . SetGrid  (0, 1)
				pad2 . Draw()
				pad2 . cd()

				hist_ratErr . Draw ("e2")
				hist_ratVal . Draw ("ep same")

				pad2 . Update()
				print ("     ||     |-> Pad 2 done")



				# + Save the plots
				#-----------------
				str_plotOutLocal = path_plot . replace ("VariableName", "Variable_{}".format(name_hist))
				str_plotOutLocal = str_plotOutLocal . replace ("_*", "_{}".format(name_hist))
				str_plotOutWeb   = path_plot . replace ("VariableName", "Variable_{}".format(name_hist))
				str_plotOutWeb   = str_plotOutWeb . replace ("_*", "_{}".format(name_hist))
				# str_plotOutWeb   = str_plotOutWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/w/wtabb/www/Egamma/commissioning/Electron/")
				str_plotOutWeb   = str_plotOutWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/f/fmausolf/www/Egamma/commissioning/Electron/")
#				str_plotOutWeb   = str_plotOutWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/e/egmcom/www/commissioning/Electron/")
				#str_plotOutWeb   = str_plotOutWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/l/lcaophuc/www/Commissioning_Automation/Electron/")

				dir_plot_checkLocal = dir_plot . replace ("VariableName", "Variable_{}".format(name_hist))
				dir_plot_checkWeb   = dir_plot . replace ("VariableName", "Variable_{}".format(name_hist))
				# dir_plot_checkWeb   = dir_plot_checkWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/w/wtabb/www/Egamma/commissioning/Electron/")
				dir_plot_checkWeb   = dir_plot_checkWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/f/fmausolf/www/Egamma/commissioning/Electron/")
#				dir_plot_checkWeb   = dir_plot_checkWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/e/egmcom/www/commissioning/Electron/")
				#dir_plot_checkWeb   = dir_plot_checkWeb . replace ("/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/", "/eos/user/l/lcaophuc/www/Commissioning_Automation/Electron/")


				if (isLog):
					str_plotOutLocal = str_plotOutLocal . replace ("/plot", "/plotLog")
					str_plotOutWeb   = str_plotOutWeb   . replace ("/plot", "/plotLog")
					pass
				else:
					str_plotOutLocal = str_plotOutLocal . replace ("/plot", "/plotLinear")
					str_plotOutWeb   = str_plotOutWeb   . replace ("/plot", "/plotLinear")
					pass

				# Create directory to plots
				if not os.path.exists(dir_plot_checkLocal):
					#print ("     ||         | >> Creating [{}]" . format(dir_plot_checkLocal))
					os.makedirs (dir_plot_checkLocal)
					pass

				if not os.path.exists(dir_plot_checkWeb):
					#print ("     ||         | >> Creating [{}]" . format(dir_plot_checkWeb))
					os.makedirs (dir_plot_checkWeb)
					pass

				canvas . SaveAs (str_plotOutLocal)
				print ("     ||     |-> Plot saved to:")
				print ("     ||         {}" . format(str_plotOutLocal))

				str_plotOutLocal = str_plotOutLocal . replace (".png", ".pdf")
				canvas . SaveAs (str_plotOutLocal)
				print ("     ||     |-> Plot saved to:")
				print ("     ||         {}" . format(str_plotOutLocal))

				str_plotOutLocal = str_plotOutLocal . replace (".pdf", ".C")
				canvas . SaveAs (str_plotOutLocal)
				print ("     ||     |-> Plot saved to:")
				print ("     ||         {}" . format(str_plotOutLocal))


				canvas . SaveAs (str_plotOutWeb)
				print ("     ||     |-> Plot saved to:")
				print ("     ||         {}" . format(str_plotOutWeb))

				str_plotOutWeb   = str_plotOutWeb   . replace (".png", ".pdf")
				canvas . SaveAs (str_plotOutWeb)
				print ("     ||     |-> Plot saved to:")
				print ("     ||         {}" . format(str_plotOutWeb))

				# Save canvas to root file
				str_plotOutWeb = str_plotOutWeb . replace (".pdf", ".root")

				file_canvas = myroot . TFile (str_plotOutWeb, "recreate")
				file_canvas . cd()

				canvas . Write()

				file_canvas . Write()
				file_canvas . Close()
				print ("     ||     |-> Canvas saved to:")
				print ("     ||         {}" . format(str_plotOutWeb))

				pass

			pass

		file_histTar . Close()
		file_histRef . Close()

		list_nameHist = []

		pass

	pass
