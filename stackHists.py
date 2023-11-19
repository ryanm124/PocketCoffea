import matplotlib.pyplot as plt
from coffea.util import load
from pocket_coffea.utils.plot_utils import Shape
from IPython.display import display, HTML
display(HTML("<style>.container { width:95% !important; }</style>"))
display(HTML("<style>.output_png { height: auto; }</style>"))
import pickle
import numpy as np
import os
if not os.path.exists('hists'):
    os.makedirs('hists')
import awkward as ak
import math



filename = "AnalysisConfigs/configs/ttHbb/test_sept28_all/output_newconfig7_all.coffea"
o = load(filename)
print("o.keys()")
print(o.keys())
print("o['variables'].keys()")
print(o['variables'].keys())
#print(o['columns']['ttHTobb']['ttHTobb_2018']['baseline'].keys())
#'columns', 'processing_metadata', 'datasets_metadata'
print("o['columns'].keys()")
print(o['columns'].keys())

print("o['datasets_metadata'].keys()")
print(o['datasets_metadata'].keys())

print(o['variables']['nJets']['ttHTobb']['ttHTobb_2018'])
o['variables']['nJets']['ttHTobb']['ttHTobb_2018'].axes[-1].name

'''
for i, var_name in enumerate(o['variables'].keys()):
    varHist = None
    for j, sam_name in enumerate(o['columns'].keys()):
        varHist = o['variables'][var_name][sam_name][sam_name+'_2018']
        print(f"var_name: {var_name}, sam_name: {sam_name}, varHist shape: {varHist.shape}")
        h = varHist.project(varHist.axes[-1].name)[:-1].plot(stack=True, density=False, histtype="fill")
    plt.legend()
    plt.title(var_name)
    plt.savefig(f"hists/all_plot_{i}.png")
    #plt.show()
    plt.clf()



# Loop over all variables
for i, var_name in enumerate(o['variables'].keys()):
    # Initialize an empty histogram to store the sum of histograms for all samples
    total_hist = None
    # Initialize an empty histogram to store the sum of histograms for all samples
    total_hist_value = None
    total_hist_variance = None

    # Loop over all samples
    for sam_name in o['columns'].keys():
        # Access the histogram for the current sample and variable
        varHist = o['variables'][var_name][sam_name][f'{sam_name}_2018']

        # If total_hist is None, initialize it with the shape of the first histogram
        if total_hist is None:
            total_hist = np.zeros(varHist.shape)

        # If total_hist is None, initialize it with the shape of the first histogram
        if total_hist_value is None:
            total_hist_value = varHist.value.copy()
            total_hist_variance = varHist.variance.copy()
        else:
            # Add the current histogram to the total_hist
            total_hist_value += varHist.value
            total_hist_variance += varHist.variance



    # Create the plot for the total histogram
    total_hist = type(varHist)(total_hist_value, total_hist_variance)
    h = varHist.project(varHist.axes[-1].name)[:-1].plot(density=False, histtype="fill")

    # Set legend and title
    plt.legend(o['columns'].keys())
    plt.title(var_name)

    # Save and show the plot
    plt.savefig(f"hists/plot_{i}.png")
    plt.show()

    # Clear the current figure for the next iteration
    plt.clf()
'''

leptonsPhi = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['LeptonGood_phi'].value)
leptonsEta = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['LeptonGood_eta'].value)
leptonsN = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['LeptonGood_N'].value)
leptonsPhi = ak.unflatten(leptonsPhi,leptonsN)
leptonsPhi = ak.to_list(ak.combinations(leptonsPhi,2))
leptonsEta = ak.unflatten(leptonsEta,leptonsN)
leptonsEta = ak.to_list(ak.combinations(leptonsEta,2))

def deltaR(phis,etas):
    leftPhi,rightPhi = ak.unzip(phis)
    leftEta,rightEta = ak.unzip(etas)
    return np.sqrt(pow(leftEta-rightEta,2)+pow(leftPhi-rightPhi,2))

plt.hist(deltaR(leptonsPhi,leptonsEta),bins=200)
plt.title("lepton deltaR")
plt.savefig(f"hists/ttHTobb_lepton_deltaR.png")
#plt.show()

jetsPhi = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_phi'].value)
jetsEta = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_eta'].value)
jetsN = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_N'].value)
jetsPhi = ak.unflatten(jetsPhi,jetsN)
jetsPhi = ak.to_list(ak.combinations(jetsPhi,2))
jetsEta = ak.unflatten(jetsEta,jetsN)
jetsEta = ak.to_list(ak.combinations(jetsEta,2))

plt.hist(ak.flatten(deltaR(jetsPhi,jetsEta)),bins=200)
plt.title("jet deltaR")
plt.savefig(f"hists/ttHTobb_jet_deltaR.png")


fatJetsPhi = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['FatJetGood_phi'].value)
fatJetsEta = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['FatJetGood_eta'].value)
fatJetsN = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['FatJetGood_N'].value)
jetsPhi = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_phi'].value)
jetsEta = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_eta'].value)
jetsN = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_N'].value)
jetsPhi = ak.unflatten(jetsPhi,jetsN)
jetsEta = ak.unflatten(jetsEta,jetsN)
fatJetsPhi = ak.unflatten(fatJetsPhi,fatJetsN)
fatJetsEta = ak.unflatten(fatJetsEta,fatJetsN)
allJetsPhi = ak.concatenate([jetsPhi,fatJetsPhi],axis=1)
allJetsEta = ak.concatenate([jetsEta,fatJetsEta],axis=1)
allJetsPhi = ak.to_list(ak.combinations(allJetsPhi,2))
allJetsEta = ak.to_list(ak.combinations(allJetsEta,2))

plt.hist(ak.flatten(deltaR(allJetsPhi,allJetsEta)),bins=200)
plt.title("all jets deltaR")
plt.savefig(f"hists/ttHTobb_alljet_deltaR.png")

jetsBScore = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_btagDeepFlavB'].value)
jetsN = ak.from_numpy(o['columns']['ttHTobb']['ttHTobb_2018']['baseline']['JetGood_N'].value)
jetsBScore = ak.unflatten(jetsBScore,jetsN)
maxBScore = ak.max(jetsBScore,axis=1)
plt.hist(maxBScore,bins=200)
plt.title("jets highest btag score")
plt.semilogy()
plt.savefig(f"hists/ttHTobb_jet_highestBtag.png")

filename2 = "AnalysisConfigs/configs/ttHbb/test_sept28_all/output_all_2018_allbut14a.coffea"
o = load(filename2)
print("o.keys()")
print(o.keys())
print("CUTFLOW")
print(o['cutflow'].keys())
print(o['cutflow'])
print("o['cutflow']['baseline']")
print(o['cutflow']['baseline'])

print("o['sumw']['baseline']")
print(o['sumw']['baseline'])

print("o['sumw']['baseline']['TTToSemiLeptonic__2018']")
print(o['sumw']['baseline']['TTToSemiLeptonic__2018'])

#print(self.output['cutflow'])
#print(o['variables']['nMuonGood']['TTbbDiLeptonic'].keys())
#for i, var_name in enumerate(o['variables'].keys()):
#    varHist = o['variables'][var_name]['TTbbDiLeptonic']['TTbbDiLeptonic_Powheg_2018']
#    h = varHist.stack("cat").project(varHist.axes[-1].name)[:-1].plot(stack=True,density=False,histtype="fill")
#    plt.legend()
#    plt.title(var_name)
#    plt.savefig(f"hists/TTbbDiLeptonic_plot_{i}.png")
#    plt.show()
#    plt.clf()


vars = {}
for i, var_name in enumerate(o['variables'].keys()):
    # Replace 'ttHTobb_2018' with the desired category                                                                          
    hists = {}
    vars[var_name] = hists
    meras = 0
    eeras = 0
    for sam_name in o['columns'].keys():
        sam_namey = sam_name + '__2018'
        if 'ttHToNonbb' in sam_name: sam_namey ='ttHToNonbb_Powheg_2018'
        if 'DYJetsToLL_M-50' in sam_name: sam_namey ='DYJetsToLL_M-50_v7__2018'
        if 'ZJetsToQQ' in sam_name: sam_namey = sam_name + '_v7__2018'
        if 'ST' in sam_name: sam_namey = sam_name + '_v7__2018'
        if 'QCD' in sam_name: sam_namey = sam_name + '_v7__2018'
        if 'WJets' in sam_name: sam_namey = sam_name + '_v7__2018' 
        if 'WJetsToLNu' in sam_name: sam_namey = sam_name + '__2018'
        if 'TTWJets' in sam_name: sam_namey = sam_name + '__2018'
        if 'TTGJets' in sam_name: sam_namey = sam_name + '__2018'
        if 'THW' in sam_name: sam_namey = sam_name + '__2018'
        if 'WW' in sam_name: sam_namey = sam_name + '__2018'
        if 'WZ' in sam_name: sam_namey = sam_name + '__2018'
        if 'ZZ' in sam_name: sam_namey = sam_name + '__2018'
        if 'ttHTobb' in sam_name: sam_namey = sam_name + '_2018'

        print(sam_name)
        print(var_name)
        if 'SingleMuon' in sam_name: 
            if meras == 0:
                sam_namey = sam_name + '_2018_EraA'
            if meras == 1:
                sam_namey = sam_name + '_2018_EraB'
            if meras == 2:
                sam_namey = sam_name + '_2018_EraC'
            if meras == 3:
                sam_namey = sam_name + '_2018_EraD'

            meras+=1
        if 'EGamma' in sam_name:
            if eeras == 0:
                sam_namey = sam_name + '_2018_EraA'
            if eeras == 1:
                sam_namey = sam_name + '_2018_EraB'
            if eeras == 2:
                sam_namey = sam_name + '_2018_EraC'
            if eeras == 3:
                sam_namey = sam_name + '_2018_EraD'

            eeras+=1

        varHist = o['variables'][var_name][sam_name][sam_namey ]
    
        # baseline is the last index in cat, so this is the 1b category                                                                        
        h = varHist.stack("cat").project(varHist.axes[-1].name)[0]
        hists[sam_name]=h

    h2 = hists['TTToSemiLeptonic'] + hists['TTToSemiLeptonic']

    #plt.legend()
    #plt.title(var_name)
    #plt.savefig(f"hists/plot_{var_name}.png")
    #plt.show()
    #plt.clf()

'''
for i, var_name in enumerate(o['variables'].keys()):
    # Replace 'ttHTobb_2018' with the desired category
    varHist = None
    for sam_name in o['columns'].keys():
        varHist = o['variables'][var_name][sam_name][sam_name+'_2018']
        h = varHist.stack("cat").project(varHist.axes[-1].name)[0].plot(stack=True,density=False,histtype="fill")
       
    plt.legend()
    plt.title(var_name)
    plt.savefig(f"hists/plot_{var_name}.png")
    plt.show()
    plt.clf()


for i, var_name in enumerate(o['variables'].keys()):
    # Replace 'ttHTobb_2018' with the desired category
    varHist = o['variables'][var_name]['ttHTobb']['ttHTobb_2018']['baseline']
    print(varHist)
    print("varHist")
    print(varHist.axes[-1].name)
    print("varHist.axes[-1].name")    
    # Project onto the last axis (assuming it's the category axis) and plot
    h = varHist.project(varHist.axes[-1].name)[:-1].plot(density=False, histtype="fill")
    
    plt.legend()
    plt.title(var_name)
    plt.savefig(f"hists/ttHTobb_plot_{i}.png")
    plt.show()
    plt.clf()
'''
import yaml

# Load the data from the YAML file
with open('/afs/cern.ch/user/a/asparker/public/sept_ttH/PocketCoffea/AnalysisConfigs/configs/ttHbb/params/plotting_style.yaml', 'r') as yaml_file:
    plotting_styles = yaml.safe_load(yaml_file)

# Assuming your cutflow data is stored in the 'cutflow_data' dictionary
cutflow_data = o['cutflow']['baseline']
cutflow_uncerts = o['sumw']['baseline']


# Define LaTeX table header
latex_table = "\\begin{table}[htbp]\n"
latex_table += "\\centering\n"
latex_table += "\\begin{tabular}{|l|c|}\n"
latex_table += "\\hline\n"
latex_table += "Process & Count \\\\\n"
latex_table += "\\hline\n"

# Iterate through the groups in the plotting_styles YAML and add rows to the LaTeX table
for group, processes in plotting_styles['plotting_style']['samples_groups'].items():
    group_count = 0
    group_uncert = 0

    for process in processes:
        print(process)
        process2 = process + "__2018"
        if 'ttHToNonbb' in process2: process2 ='ttHToNonbb_Powheg_2018'
        if 'DYJetsToLL_M-50' in process2: process2 ='DYJetsToLL_M-50_v7__2018'
        if 'ZJetsToQQ' in process2: process2 = process+ '_v7__2018'
        if 'ST' in process2: process2 = process+ '_v7__2018'
        if 'QCD' in process2: process2 = process+ '_v7__2018'

        print(processes)
        if process2 in cutflow_data:
            print("process2 in cutflow data")
    
            group_count += cutflow_data[process2][process]
            group_uncert += cutflow_uncerts[process2][process]
            print(group_count)

    # Replace group names with the ones from the YAML labels_mc section
    group_label = plotting_styles['plotting_style']['labels_mc'].get(group, group)
    
    group_uncert2 = math.sqrt(group_uncert) # * group_uncert)

    latex_table += f"{group_label} & {group_count} \pm {group_uncert2:.4g}  \\\\\n"

# Add LaTeX table footer
latex_table += "\\hline\n"
latex_table += "\\end{tabular}\n"
latex_table += "\\caption{Cutflow table}\n"
latex_table += "\\label{tab:cutflow}\n"
latex_table += "\\end{table}"

# Print the LaTeX table
print(latex_table)
