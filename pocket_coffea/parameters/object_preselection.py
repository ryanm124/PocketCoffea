# Common cuts applied to objects

object_preselection = {
    "dimuon": {
        "Muon": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.25, #PFIsoLoose
            "id": "tightId",
        },
        "Electron": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.06,
            "id": "mvaFall17V2Iso_WP80",
        },
        "Jet": {
            "dr": 0.4,
            "pt": 30,
            "eta": 2.4,
            "jetId": 2,
            "puId": {"wp": "L", "value": 4, "maxpt": 50.0},
        },
    },
    "dilepton": {
        "Muon": {
            "pt": 25,
            "eta": 2.4,
            "iso": 0.25, #PFIsoLoose
            "id": "looseId",
        },
        "Electron": {
            "pt": 25,
            "eta": 2.4,
            "iso": 0.06,
            "id": "mvaFall17V2Iso_WPL",
        },
        "Jet": {
            "dr": 0.4,
            "pt": 30,
            "eta": 2.4,
            "jetId": 2,
            "puId": {"wp": "L", "value": 4, "maxpt": 50.0},
        },
        "FatJet": {
            "dr": 0.8,
            "pt": 200,
            "eta": 2.4,
            "jetId": 2
        },
    },
    "semileptonic": {
        "Muon": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.15, #PFIsoTight
            "id": "tightId",
        },
        "Electron": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.06,
            "id": "mvaFall17V2Iso_WP80",
        },
        "Jet": {
            "dr": 0.4,
            "pt": 30,
            "eta": 2.4,
            "jetId": 2,
            "puId": {"wp": "L", "value": 4, "maxpt": 50.0},
        },
    },
    "semileptonic_partonmatching": {
        "Muon": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.15, #PFIsoTight
            "id": "tightId",
        },
        "Electron": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.06,
            "id": "mvaFall17V2Iso_WP80",
        },
        "Jet": {
            "dr": 0.4,
            "pt": 20,
            "eta": 2.4,
            "jetId": 2,
            "puId": {"wp": "L", "value": 4, "maxpt": 50.0},
        },
    },
    "mutag": {
        "Muon": {
            "pt": 5,
            "eta": 2.4,
            "iso": 0.15,
            "id": "tightId"
        },
        "Electron": {
            "pt": 15,
            "eta": 2.4,
            "iso": 0.06,
            "id": "mvaFall17V2Iso_WP80",
        },
        "Jet": {
            "dr": 0.4,
            "pt": 25,
            "eta": 2.5,
            "jetId": 2,
            "puId": {"wp": "L", "value": 4, "maxpt": 50.0},
        },
        "FatJet": {
            "pt": 350,
            "eta": 2.4,
            "msd": 40,
            "jetId": 2,
            "nsubjet": 2,
            "nmusj": 1,
            "dimuon_pt_ratio": 0.6,
        },
    },
}
