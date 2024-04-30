import awkward as ak
import numpy as np

# from ..parameters.object_preselection import object_preselection
from ..lib.deltaR_matching import get_matching_pairs_indices, object_matching


def lepton_selection(events, lepton_flavour, params):

    leptons = events[lepton_flavour]
    cuts = params.object_preselection[lepton_flavour]
    # Requirements on pT and eta
    passes_eta = abs(leptons.eta) < cuts["eta"]
    passes_pt = leptons.pt > cuts["pt"]

    if lepton_flavour == "Electron":
        # Requirements on SuperCluster eta, isolation and id
        etaSC = abs(leptons.deltaEtaSC + leptons.eta)
        passes_SC = np.invert((etaSC >= 1.4442) & (etaSC <= 1.5660))
        #passes_iso = leptons.miniPFRelIso_chg < cuts["iso"]
        passes_id = leptons[cuts['id']] >= 4 # 4 = tight ID for cutBased  #== True

        good_leptons = passes_eta & passes_pt & passes_SC  & passes_id

    elif lepton_flavour == "Muon":
        # Requirements on isolation and id miniPFRelIso_chg
        #passes_iso = leptons.pfRelIso04_all < cuts["iso"] //miniPFRelIso_chg
        passes_iso = leptons.pfRelIso04_all < cuts["iso"]
        passes_id = leptons[cuts['id']] == True

        good_leptons = passes_eta & passes_pt  & passes_id & passes_iso

    return leptons[good_leptons]


def get_dilepton(electrons, muons, transverse=False):

    fields = {
        "pt": 0.,
        "eta": 0.,
        "phi": 0.,
        "mass": 0.,
        "charge": 0.,
    }
    
    leptons = ak.pad_none(ak.with_name(ak.concatenate([ muons[:, 0:2], electrons[:, 0:2]], axis=1), "PtEtaPhiMCandidate"), 2)
    nlep =  ak.num(leptons[~ak.is_none(leptons, axis=1)])
    ll = leptons[:,0] + leptons[:,1]

    for var in fields.keys():
        fields[var] = ak.where(
            (nlep == 2),
            getattr(ll, var),
            fields[var]
        )
        
    fields["deltaR"] = ak.where(
        (nlep == 2), leptons[:,0].delta_r(leptons[:,1]), -1)

    if transverse:
        fields["eta"] = ak.zeros_like(fields["pt"])
    dileptons = ak.zip(fields, with_name="PtEtaPhiMCandidate")

    # add dilepton mass cut (addded in custom cut functions instead)
    #mass_min = dileptons.mass > 20
    #zmass_rej = ak.any( ( (dileptons.mass < 76 ) or (dileptons.mass > 106  )) , axis=1)  
    #mass_pass = mass_min &  zmass_rej   

    #dileptons = dileptons[mass_pass]
    return dileptons
    
def get_lepW(electrons, muons, MET, jets, fatjets, transverse=False):

    mfields = {
        "pt": MET.pt,
        "eta": ak.zeros_like(MET.pt),
        "phi": MET.phi,
        "mass": ak.zeros_like(MET.pt),
        "charge": ak.zeros_like(MET.pt),
    }

    METs = ak.zip(mfields, with_name="PtEtaPhiMCandidate")

    
    fields = {
        "pt": 0.,
        "eta": 0.,
        "phi": 0.,
        "mass": 0.,
        "charge": 0.,
    }

    leptons = ak.pad_none(ak.with_name(ak.concatenate([ muons[:, 0:2], electrons[:, 0:2]], axis=1), "PtEtaPhiMCandidate"), 2)
    nlep =  ak.num(leptons[~ak.is_none(leptons, axis=1)])
    l = leptons[:,0]# + leptons[:,1]

    Wcand1 = l + METs

    #Wcand2 = jets

    for var in fields.keys():
        fields[var] = ak.where(
            (nlep >= 1),
            getattr(l, var),
            fields[var]
        )

    jfields = {
        "pt": jets.pt,
        "eta": jets.eta ,
        "phi": jets.phi,
        "mass": jets.mass,
        "charge": ak.zeros_like(jets.pt), 
    }

    JETs = ak.zip(jfields, with_name="PtEtaPhiMCandidate")

    fjfields = {
        "pt": fatjets.pt,
        "eta": fatjets.eta ,
        "phi": fatjets.phi,
        "mass": fatjets.mass,
        "charge": ak.zeros_like(fatjets.pt), 
    }

    FATJETs = ak.zip(fjfields, with_name="PtEtaPhiMCandidate")
    
        
    #fields["deltaR"] = ak.where(
    #    (Wcand1 != None), Wcand1[:].delta_r(FATJETs[:]), -1)

    if transverse:
        fields["eta"] = ak.zeros_like(fields["pt"])
    Wcand = ak.zip(fields, with_name="PtEtaPhiMCandidate")


    return Wcand

# self.events.JetGood , self.events.nJetGood, self.events.nBJetGood 
def get_hadW(jets , Bjets, fatjets, transverse=False):
    # add a cut on >=2 NON B tagged jets
    jfields = {
        "pt": jets.pt,
        "eta": jets.eta ,
        "phi": jets.phi,
        "mass": jets.mass,
        "charge": ak.zeros_like(jets.pt),
    }

    JETs = ak.zip(jfields, with_name="PtEtaPhiMCandidate")
    nJET =  ak.num(JETs[~ak.is_none(JETs, axis=1)])

    bjfields = {
        "pt": Bjets.pt,
        "eta": Bjets.eta ,
        "phi": Bjets.phi,
        "mass": Bjets.mass,
        "charge": ak.zeros_like(Bjets.pt),
    }

    BJETs = ak.zip(bjfields, with_name="PtEtaPhiMCandidate")
    nBJET =  ak.num(BJETs[~ak.is_none(BJETs, axis=1)])

    nonBjets = nJET - nBJET
    Wcand2 = None
    #if (nJET >=2   ):
    #Wcand2 = JETs[:,0] +  JETs[:,1]
    if len(JETs) >= 2:
        Wcand2 = JETs[0] + JETs[1]
    else:
        # Handle the case when there are less than 2 jets
        # For example, raise an error or set Wcand2 to None
        Wcand2 = None  # or any other appropriate handling

    fields = {
        "pt": 0.,
        "eta": 0.,
        "phi": 0.,
        "mass": 0.,
        "charge": 0.,
    }

    #for var in fields.keys():
    #    fields[var] = ak.where(
    #        (Wcand2 != None),
    #        getattr(Wcand2, var),
    #       fields[var]
    #        )
        
    fjfields = {
	"pt": fatjets.pt,
        "eta": fatjets.eta ,
        "phi": fatjets.phi,
        "mass": fatjets.mass,
        "charge": ak.zeros_like(fatjets.pt), 
    }

    FATJETs = ak.zip(fjfields, with_name="PtEtaPhiMCandidate")
        
    #fields["deltaR"] = ak.where(
    #    (Wcand2 != None), Wcand2[:].delta_r(FATJETs[:]), -1)

    if transverse:
        fields["eta"] = ak.zeros_like(fields["pt"])
    Wcand = ak.zip(fields, with_name="PtEtaPhiMCandidate")


    return Wcand



def get_diboson(dileptons, MET, transverse=False):

    fields = {
        "pt": MET.pt,
        "eta": ak.zeros_like(MET.pt),
        "phi": MET.phi,
        "mass": ak.zeros_like(MET.pt),
        "charge": ak.zeros_like(MET.pt),
    }

    METs = ak.zip(fields, with_name="PtEtaPhiMCandidate")
    if transverse:
        dileptons_t = dileptons[:]
        dileptons_t["eta"] = ak.zeros_like(dileptons_t.eta)
        dibosons = dileptons_t + METs
    else:
        dibosons = dileptons + METs

    return dibosons


def get_charged_leptons(electrons, muons, charge, mask):

    fields = {
        "pt": None,
        "eta": None,
        "phi": None,
        "mass": None,
        "energy": None,
        "charge": None,
        "x": None,
        "y": None,
        "z": None,
    }

    nelectrons = ak.num(electrons)
    nmuons = ak.num(muons)
    mask_ee = mask & ((nelectrons + nmuons) == 2) & (nelectrons == 2)
    mask_mumu = mask & ((nelectrons + nmuons) == 2) & (nmuons == 2)
    mask_emu = mask & ((nelectrons + nmuons) == 2) & (nelectrons == 1) & (nmuons == 1)

    for var in fields.keys():
        if var in ["eta", "phi"]:
            default = ak.from_iter(len(electrons) * [[-9.0]])
        else:
            default = ak.from_iter(len(electrons) * [[-999.9]])
        if not var in ["energy", "x", "y", "z"]:
            fields[var] = ak.where(
                mask_ee, electrons[var][electrons.charge == charge], default
            )
            fields[var] = ak.where(
                mask_mumu, muons[var][muons.charge == charge], fields[var]
            )
            fields[var] = ak.where(
                mask_emu & ak.any(electrons.charge == charge, axis=1),
                electrons[var][electrons.charge == charge],
                fields[var],
            )
            fields[var] = ak.where(
                mask_emu & ak.any(muons.charge == charge, axis=1),
                muons[var][muons.charge == charge],
                fields[var],
            )
            fields[var] = ak.flatten(fields[var])
        else:
            fields[var] = ak.where(
                mask_ee, getattr(electrons, var)[electrons.charge == charge], default
            )
            fields[var] = ak.where(
                mask_mumu, getattr(muons, var)[muons.charge == charge], fields[var]
            )
            fields[var] = ak.where(
                mask_emu & ak.any(electrons.charge == charge, axis=1),
                getattr(electrons, var)[electrons.charge == charge],
                fields[var],
            )
            fields[var] = ak.where(
                mask_emu & ak.any(muons.charge == charge, axis=1),
                getattr(muons, var)[muons.charge == charge],
                fields[var],
            )
            fields[var] = ak.flatten(fields[var])

    charged_leptons = ak.zip(fields, with_name="PtEtaPhiMCandidate")

    return charged_leptons
