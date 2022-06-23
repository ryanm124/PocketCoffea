import awkward as ak

from coffea import hist, processor
from coffea.processor import dict_accumulator, defaultdict_accumulator
from coffea.analysis_tools import Weights

from ..workflows.base import ttHbbBaseProcessor
from ..lib.pileup import sf_pileup_reweight
from ..lib.scale_factors import sf_ele_reco, sf_ele_id, sf_mu
from ..parameters.lumi import lumi
from ..parameters.samples import samples_info

class semileptonicTriggerProcessor(ttHbbBaseProcessor):
    def __init__(self,cfg) -> None:
        super().__init__(cfg=cfg)
        # Accumulator with sum of weights of the events passing each category for each sample
        self._eff_dict = {cat: defaultdict_accumulator(float) for cat in self._categories}
        self._accum_dict["trigger_efficiency"] = dict_accumulator(self._eff_dict)

    def compute_weights(self):
        self.weights = Weights(self.nevents)
        if self.isMC:
            self.weights.add('genWeight', self.events.genWeight)
            self.weights.add('lumi', ak.full_like(self.events.genWeight, lumi[self._year]))
            self.weights.add('XS', ak.full_like(self.events.genWeight, samples_info[self._sample]["XS"]))
            self.weights.add('sum_genweights', ak.full_like(self.events.genWeight, 1./self.output["sum_genweights"][self._sample]))
            # Pileup reweighting with nominal, up and down variations
            self.weights.add('pileup', *sf_pileup_reweight(self.events, self._year))
            # Electron reco and id SF with nominal, up and down variations
            self.weights.add('sf_ele_reco', *sf_ele_reco(self.events, self._year))
            self.weights.add('sf_ele_id',   *sf_ele_id(self.events, self._year))
            # Muon id and iso SF with nominal, up and down variations
            self.weights.add('sf_mu_id',  *sf_mu(self.events, self._year, 'id'))
            self.weights.add('sf_mu_iso', *sf_mu(self.events, self._year, 'iso'))

    def postprocess(self, accumulator):
        super().postprocess(accumulator=accumulator)

        for trigger in self.cfg.triggers_to_measure:
            den_mc   = sum(accumulator["sumw"]["inclusive"].values())
            den_data = accumulator["cutflow"]["inclusive"]["DATA"]
            for category, cuts in self._categories.items():
                num_mc = sum(accumulator["sumw"][category].values())
                num_data = accumulator["cutflow"][category]["DATA"]
                eff_mc   = num_mc/den_mc
                eff_data = num_data/den_data
                accumulator["trigger_efficiency"][category] = {}
                accumulator["trigger_efficiency"][category]["mc"] = eff_mc
                accumulator["trigger_efficiency"][category]["data"] = eff_data
                accumulator["trigger_efficiency"][category]["sf"] = eff_data/eff_mc

        return accumulator
