# METFilter flags

event_flags = {
    "2018": [
        "goodVertices",
        "globalSuperTightHalo2016Filter",
        "HBHENoiseFilter",
        "HBHENoiseIsoFilter",
        "EcalDeadCellTriggerPrimitiveFilter",
        "BadPFMuonFilter",
    ],  # "BadChargedCandidateFilter", "ecalBadCalibFilter
    "2017": [
        "goodVertices",
        "globalSuperTightHalo2016Filter",
        "HBHENoiseFilter",
        "HBHENoiseIsoFilter",
        "EcalDeadCellTriggerPrimitiveFilter",
        "BadPFMuonFilter",
    ],  # "BadChargedCandidateFilter", "ecalBadCalibFilter
    # N.B.: The values for the 2016 pre/post VFP have been copied from the previous 2016 key.
    # These values need to be checked.
    "2016_PostVFP": [
        "goodVertices",
        "globalSuperTightHalo2016Filter",
        "HBHENoiseFilter",
        "HBHENoiseIsoFilter",
        "EcalDeadCellTriggerPrimitiveFilter",
        "BadPFMuonFilter",
    ],  # "BadChargedCandidateFilter", "ecalBadCalibFilter
    "2016_PreVFP": [
        "goodVertices",
        "globalSuperTightHalo2016Filter",
        "HBHENoiseFilter",
        "HBHENoiseIsoFilter",
        "EcalDeadCellTriggerPrimitiveFilter",
        "BadPFMuonFilter",
    ],  # "BadChargedCandidateFilter", "ecalBadCalibFilter
}

event_flags_data = {
    "2018": ["eeBadScFilter"],
    "2017": ["eeBadScFilter"],
    "2016_PostVFP": ["eeBadScFilter"],
    "2016_PreVFP": ["eeBadScFilter"],
}
