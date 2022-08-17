# egamma_autocommissioning

---

## Introduction
A package that execute the auto-commissioning for the electron channel of E/gamma

This package reads the list(s) of input ntuples to produce the commissioning plots and transfer those plots to a webpage. The lists containing the processed ntuples are written in a file named `info_processedNtupleLists.txt` and will be ignored the next time the program executes.
If you are testing the package, either comment out the `if` statement below [line 102](https://github.com/rekkhan/egamma_autocommissioning/blob/f41e1f833548b83d3c6bc59e14d6407761155978/tnpEGMAuto_Execute.py#L102) or remove `info_processedNtupleLists.txt` before running the program.

---

## Usage
The program can be run manually by:
```bash
python tnpEGMAuto_Execute.py
```
or using any schedule utility (e.g: `cron_tab`) to have it run automatically

### Note on directories:
- The directory containing the lists of input ntuples is defined by `dir_containNtupleList` in `tnpEGMAuto_Execute.py`
- The main directory contain the histogram root file is defined by `dir_hist` in `Lib_Python/tool_InfoCollector.py`
- The main (local) directory contain the plots is defined by `dirtmp` in `Lib_Python/tool_InfoCollector.py`.
- **NOTE**: The sub-directory is generated automatically based on the information in the list of ntuples.
- The file `info_processedNtupleLists.txt` is stored in the same location to the lists onf input ntuples by default. You can change it by modifying the variable `path_listToIgnore` in `tnpEGMAuto_Execute.py`
- The plots are stored locally and also on an offcial webpage:
/afs/cern.ch/work/e/egmcom/commissioning_automation/Output/EGM_Commissioning_Electron/
if you want to change it to your personal page, you need to modify the following variables:
1. `dir_toEleSample` in `tnpEGMAuto_Execute.py`
2. `str_plotOutWeb` and `dir_plot_checkWeb` in `tnpEGMAuto_Plot.py`. **Note**: the directories related to these two variables must match the ones in `dirtmp` (for local plots) and `dir_toEleSample` (for online plots)

### Notes on the variables & function
The variables we want to study in the commissioning are defined in the following files
1. `UserDefined/usrDefVars.json`: This file contains the variables that is **not** avaiable in the input ntuple and can be computed from the other available variables. Each variable is defined by its name (`"variable"`) and a formula (`"formula"`) telling the program how to compute it. The formulae are C/C++ functions.
2. `UserDefined/usrDefHist_*.json`: These files define the histogram for each variables. The files also apply some selection before filling the histogram. The selections are declared in the first json block, and is apply to all the histogram defined in the same file. You can either adding new histogram to the same json file if the selection is the same, or create new file if you need to apply new cuts.
3. `UserDefined/usrDefFunc_*.h`: these file contains the functions required to obtain th unavailable variables. Each file can only contain one function. Add more functions by create more files.

### The list of input ntuple
An example of ntuple list is in the `Example` directory.
Each list must contain 2 main blocks, corresponding to the set of target samples and reference samples (e.g: data sample vs MC sample)

Information sub-list:
- `fileInput`:  **list** of paths to the input ntuples.
- `runPeriod`:  **list** of run period corresponding to the input ntuples
- `luminosity`: **list** of luminosity.
- `filePU`:     **list** of pileup file. Set to "ignore" in case of data
- `treePU`:     **list** of pileup tree. Set to "ignore" in case of data
The order of `runPeriod`, `luminosity`, `file/treePU` must be the same as of `fileInput`, otherwise the result will be wrong.

**NOTE**:
- The number of ntuples in the ref block and tar block must be the same.
- Result for combined period can be process by `doCombine`. 
