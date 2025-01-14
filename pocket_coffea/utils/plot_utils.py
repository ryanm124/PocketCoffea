import os
from copy import deepcopy

import math
import numpy as np
import awkward as ak
import hist

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import mplhep as hep

from ..parameters.lumi import lumi, femtobarn
from ..parameters.plotting import style_cfg


class Style:
    '''This class manages all the style options for Data/MC plots.'''
    def __init__(self, style_cfg=style_cfg) -> None:
        required_keys = ["opts_figure", "opts_mc", "opts_data", "opts_unc"]
        for key in required_keys:
            assert key in style_cfg, f"The key `{key}` is not defined in the style dictionary."
        for key, item in style_cfg.items():
            setattr(self, key, item)
        self.has_labels = False
        self.has_samples_map = False
        self.has_lumi = False
        if "labels" in style_cfg:
            self.has_labels = True
        if "samples_map" in style_cfg:
            self.has_samples_map = True
        if "lumi_processed" in style_cfg:
            self.has_lumi = True
        self.set_defaults()

    def set_defaults(self):
        if not "stack" in self.opts_mc:
            self.opts_mc["stack"] = True
        if not hasattr(self, "fontsize"):
            self.fontsize = 22


class PlotManager:
    '''This class manages multiple Shape objects and their plotting.'''
    def __init__(self, hist_cfg, plot_dir, only_cat=[''], style_cfg=style_cfg, data_key="DATA", log=False, density=False, save=True) -> None:
        self.shape_objects = {}
        self.plot_dir = plot_dir
        self.only_cat = only_cat
        self.data_key = data_key
        self.log = log
        self.density = density
        self.save = save
        for name, h_dict in hist_cfg.items():
            self.shape_objects[name] = Shape(h_dict, name, plot_dir, only_cat=self.only_cat, style_cfg=style_cfg, data_key=self.data_key, log=self.log, density=self.density)

    def plot_datamc_all(self, syst=True, spliteras=False):
        '''Plots all the histograms contained in the dictionary, for all years and categories.'''
        for name, datamc in self.shape_objects.items():
            if ((datamc.is_mc_only) | (datamc.is_data_only)):
                ratio = False
            else:
                ratio = True
            datamc.plot_datamc_all(ratio, syst, spliteras, save=self.save)


class Shape:
    '''This class handles the plotting of 1D data/MC histograms.
    The constructor requires as arguments:
    - h_dict: dictionary of histograms, with each entry corresponding to a different MC sample.
    - name: name that identifies the Shape object.
    - style_cfg: dictionary with style and plotting options.
    - data_key: prefix for data samples (e.g. default in PocketCoffea: "DATA_SingleEle")'''
    def __init__(self, h_dict, name, plot_dir, only_cat=[''], style_cfg=style_cfg, data_key="DATA", log=False, density=False) -> None:
        self.h_dict = h_dict
        self.name = name
        self.plot_dir = plot_dir
        self.only_cat = only_cat
        self.style = Style(style_cfg)
        if self.style.has_lumi:
            self.lumi_fraction = {year : l / lumi[year]['tot'] for year, l in self.style.lumi_processed.items()}
        self.data_key = data_key
        self.log = log
        self.density = density
        assert type(h_dict) == dict, "The Shape object receives a dictionary of hist.Hist objects as argument."
        self.group_samples()
        assert self.dense_dim == 1, f"The dimension of the histogram '{self.name}' is {self.dense_dim}. Only 1D histograms are supported."
        self.load_attributes()

    @property
    def dense_axes(self):
        '''Returns the list of dense axes of a histogram, defined as the axes that are not categorical axes.'''
        dense_axes_dict = {s : [] for s in self.h_dict.keys()}

        for s, h in self.h_dict.items():
            for ax in h.axes:
                if not type(ax) in [hist.axis.StrCategory, hist.axis.IntCategory]:
                    dense_axes_dict[s].append(ax)
        dense_axes = list(dense_axes_dict.values())
        assert all(v == dense_axes[0] for v in dense_axes), "Not all the histograms in the dictionary have the same dense dimension."
        dense_axes = dense_axes[0]

        return dense_axes

    def _categorical_axes(self, mc=True):
        '''Returns the list of categorical axes of a histogram.'''
        # Since MC and data have different categorical axes, the argument mc needs to specified
        if mc:
            d = {s : v for s, v in self.h_dict.items() if s in self.samples_mc}
        else:
            d = {s : v for s, v in self.h_dict.items() if s in self.samples_data}
        categorical_axes_dict = {s : [] for s in d.keys()}

        for s, h in d.items():
            for ax in h.axes:
                if type(ax) in [hist.axis.StrCategory, hist.axis.IntCategory]:
                    categorical_axes_dict[s].append(ax)
        categorical_axes = list(categorical_axes_dict.values())
        assert all(v == categorical_axes[0] for v in categorical_axes), "Not all the histograms in the dictionary have the same categorical dimension."
        categorical_axes = categorical_axes[0]

        return categorical_axes

    @property
    def categorical_axes_mc(self):
        '''Returns the list of categorical axes of a MC histogram.'''
        return self._categorical_axes(mc=True)

    @property
    def categorical_axes_data(self):
        '''Returns the list of categorical axes of a data histogram.'''
        return self._categorical_axes(mc=False)

    @property
    def dense_dim(self):
        '''Returns the number of dense axes of a histogram.'''
        return len(self.dense_axes)
    
    def get_axis_items(self, axis_name, mc=True):
        '''Returns the list of values contained in a Hist axis.'''
        if mc:
            axis = [ax for ax in self.categorical_axes_mc if ax.name == axis_name][0]
        else:
            axis = [ax for ax in self.categorical_axes_data if ax.name == axis_name][0]
        return list(axis.value(range(axis.size)))

    def _stack_sum(self, mc=None, stack=None):
        '''Returns the sum histogram of a stack (`hist.stack.Stack`) of histograms.'''
        if not stack:
            if mc:
                stack = self.stack_mc_nominal
            else:
                stack = self.stack_data
        if len(stack) == 1:
            return stack[0]
        else:
            htot = stack[0]
            for h in stack[1:]:
                htot = htot + h
            return htot

    @property
    def stack_sum_data(self):
        '''Returns the sum histogram of a stack (`hist.stack.Stack`) of data histograms.'''
        return self._stack_sum(mc=False)

    @property
    def stack_sum_mc_nominal(self):
        '''Returns the sum histogram of a stack (`hist.stack.Stack`) of MC histograms.'''
        return self._stack_sum(mc=True)

    @property
    def samples(self):
        return list(self.h_dict.keys())

    @property
    def samples_data(self):
        return list(filter(lambda d : self.data_key in d, self.samples))

    @property
    def samples_mc(self):
        return list(filter(lambda d : self.data_key not in d, self.samples))

    def group_samples(self):
        '''Groups samples according to the dictionary self.style.samples_map'''
        if not self.style.has_samples_map:
            return
        h_dict_grouped = {}
        samples_in_map = []
        for sample_new, samples_list in self.style.samples_map.items():
            h_dict_grouped[sample_new] = self._stack_sum(stack=hist.Stack.from_dict({s : h for s, h in self.h_dict.items() if s in samples_list}))
            samples_in_map += samples_list
        for s, h in self.h_dict.items():
            if s not in samples_in_map:
                h_dict_grouped[s] = h
        self.h_dict = deepcopy(h_dict_grouped)

    def load_attributes(self):
        '''Loads the attributes from the dictionary of histograms.'''
        assert len(set([self.h_dict[s].ndim for s in self.samples_mc])), "Not all the MC histograms have the same dimension."
        for ax in self.categorical_axes_mc:
            setattr(self, {'year': 'years', 'cat': 'categories', 'variation': 'variations'}[ax.name], self.get_axis_items(ax.name))
        self.xaxis = self.dense_axes[0]
        self.xlabel = self.xaxis.label
        self.xcenters = self.xaxis.centers
        self.xedges = self.xaxis.edges
        self.xbinwidth = np.ediff1d(self.xedges)
        self.is_mc_only = True if len(self.samples_data) == 0 else False
        self.is_data_only = True if len(self.samples_mc) == 0 else False
        if self.is_data_only | (not self.is_mc_only):
            self.lumi = {year : femtobarn(lumi[year]['tot'], digits=1) for year in self.years}

    def build_stacks(self, year, cat, spliteras=False):
        '''Builds the data and MC stacks, applying a slicing by year and category.
        If spliteras is True, the extra axis "era" is kept in the data stack to
        distinguish between data samples from different data-taking eras.'''
        slicing_mc = {'year': year, 'cat': cat}
        slicing_mc_nominal = {'year': year, 'cat': cat, 'variation': 'nominal'}
        self.h_dict_mc = {d: self.h_dict[d][slicing_mc] for d in self.samples_mc}
        self.h_dict_mc_nominal = {d: self.h_dict[d][slicing_mc_nominal] for d in self.samples_mc}
        # Store number of weighted MC events
        self.nevents = {d: round(sum(self.h_dict_mc_nominal[d].values()), 1) for d in self.samples_mc}
        reverse=True
        # Order the events dictionary by decreasing number of events if linear scale, increasing if log scale
        # N.B.: Here implement if log: reverse=False
        self.nevents = dict( sorted(self.nevents.items(), key=lambda x:x[1], reverse=reverse) )
        color = iter(cm.gist_rainbow(np.linspace(0, 1, len(self.nevents.keys()))))
        # Assign random colors to each sample
        self.colors = [next(color) for d in self.nevents.keys()]
        if hasattr(self.style, "colors"):
            # Initialize random colors
            for i, d in enumerate(self.nevents.keys()):
                # If the color for a corresponding sample exists in the dictionary, assign the color to the sample
                if d in self.style.colors:
                    self.colors[i] = self.style.colors[d]
        # Order the MC dictionary by number of events
        self.h_dict_mc = {d: self.h_dict_mc[d] for d in self.nevents.keys()}
        self.h_dict_mc_nominal = {d: self.h_dict_mc_nominal[d] for d in self.nevents.keys()}
        # Build MC stack with variations and nominal MC stack
        self.stack_mc = hist.Stack.from_dict(self.h_dict_mc)
        self.stack_mc_nominal = hist.Stack.from_dict(self.h_dict_mc_nominal)

        if not self.is_mc_only:
            # Sum over eras if specified as extra argument
            if 'era' in self.categorical_axes_data:
                if spliteras:
                    slicing_data = {'year': year, 'cat': cat}
                else:
                    slicing_data = {'year': year, 'cat': cat, 'era': sum}
            else:
                if spliteras:
                    raise Exception("No axis 'era' found. Impossible to split data by era.")
                else:
                    slicing_data = {'year': year, 'cat': cat}
            self.h_dict_data = {d: self.h_dict[d][slicing_data] for d in self.samples_data}
            self.stack_data = hist.Stack.from_dict(self.h_dict_data)

    def get_datamc_ratio(self):
        '''Computes the data/MC ratio and the corresponding uncertainty.'''
        num = self.stack_sum_data.values()
        den = self.stack_sum_mc_nominal.values()
        self.ratio = num / den
        # TO DO: Implement Poisson interval valid also for num~0
        # np.sqrt(num) is just an approximation of the uncertainty valid at large num
        self.ratio_unc = np.sqrt(num) / den
        self.ratio_unc[np.isnan(self.ratio_unc)] = np.inf

    def get_systematic_uncertainty(self):
        '''Instantiates the `SystUnc` objects and stores them in a dictionary with one entry for each systematic uncertainty.'''
        self.syst_manager = SystManager(self)

    def define_figure(self, year=None, ratio=True):
        '''Defines the figure for the Data/MC plot.
        If ratio is True, a subplot is defined to include the Data/MC ratio plot.'''
        plt.style.use([hep.style.ROOT, {'font.size': self.style.fontsize}])
        plt.rcParams.update({'font.size': self.style.fontsize})
        if ratio:
            self.fig, (self.ax, self.rax) = plt.subplots(2, 1, **self.style.opts_figure["datamc_ratio"])
            self.fig.subplots_adjust(hspace=0.06)
        else:
            self.fig, self.ax  = plt.subplots(1, 1, **self.style.opts_figure["datamc"])
        if self.is_mc_only:
            hep.cms.text("Simulation Preliminary", fontsize=self.style.fontsize, loc=0, ax=self.ax)
        if year:
            if not self.is_mc_only:
                hep.cms.lumitext(text=f'{self.lumi[year]}' + r' fb$^{-1}$, 13 TeV,' + f' {year}', fontsize=self.style.fontsize, ax=self.ax)
            else:
                hep.cms.lumitext(text=f'{year}', fontsize=self.style.fontsize, ax=self.ax)

    def format_figure(self, ratio=True):
        '''Formats the figure's axes, labels, ticks, xlim and ylim.'''
        ylabel = "Counts" if not self.density else "A.U."
        self.ax.set_ylabel(ylabel, fontsize=self.style.fontsize)
        self.ax.legend(fontsize=self.style.fontsize, ncol=2, loc="upper right")
        self.ax.tick_params(axis='x', labelsize=self.style.fontsize)
        self.ax.tick_params(axis='y', labelsize=self.style.fontsize)
        self.ax.set_xlim(self.xedges[0], self.xedges[-1])
        if self.log:
            self.ax.set_yscale("log")
            if self.is_mc_only:
                exp = math.floor(math.log(max(self.stack_sum_mc_nominal.values()), 10))
            else:
                exp = math.floor(math.log(max(self.stack_sum_data.values()), 10))
            self.ax.set_ylim((0.01, 10 ** (exp + 3)))
        else:
            if self.is_mc_only:
                reference_shape = self.stack_sum_mc_nominal.values()
            else:
                reference_shape = self.stack_sum_data.values()
            if self.density:
                integral = sum(reference_shape) * self.xbinwidth
                reference_shape = reference_shape / integral
            ymax = max(reference_shape)
            if not np.isnan(ymax):
                self.ax.set_ylim((0, 2.0 * ymax))
        if ratio:
            self.ax.set_xlabel("")
            self.rax.set_xlabel(self.xlabel, fontsize=self.style.fontsize)
            self.rax.set_ylabel("Data / MC", fontsize=self.style.fontsize)
            self.rax.yaxis.set_label_coords(-0.075, 1)
            self.rax.tick_params(axis='x', labelsize=self.style.fontsize)
            self.rax.tick_params(axis='y', labelsize=self.style.fontsize)
            self.rax.set_ylim((0.5, 1.5))
        if self.style.has_labels:
            handles, labels = self.ax.get_legend_handles_labels()
            labels_new = []
            handles_new = []
            for i, l in enumerate(labels):
                if l in self.style.labels:
                    labels_new.append(f"{self.style.labels[l]}")
                else:
                    labels_new.append(l)
                handles_new.append(handles[i])
            labels = labels_new
            handles = handles_new
            self.ax.legend(handles, labels, fontsize=self.style.fontsize, ncol=2, loc="upper right")

    def plot_mc(self, ax=None):
        '''Plots the MC histograms as a stacked plot.'''
        if ax:
            self.ax = ax
        self.stack_mc_nominal.plot(ax=self.ax, color=self.colors, density=self.density, **self.style.opts_mc)
        self.format_figure(ratio=False)

    def plot_data(self, ax=None):
        '''Plots the data histogram as an errorbar plot.'''
        if ax:
            self.ax = ax
        y = self.stack_sum_data.values()
        yerr = np.sqrt(y)
        integral = (sum(y) * self.xbinwidth)
        if self.density:
            y = y / integral
            yerr = yerr / integral
        self.ax.errorbar(self.xcenters, y, yerr=yerr, **self.style.opts_data)
        self.format_figure(ratio=False)

    def plot_datamc_ratio(self, ax=None):
        '''Plots the Data/MC ratio as an errorbar plot.'''
        self.get_datamc_ratio()
        if ax:
            self.rax = rax
        self.rax.errorbar(self.xcenters, self.ratio, yerr=self.ratio_unc, **self.style.opts_data)
        self.format_figure(ratio=True)

    def plot_systematic_uncertainty(self, ratio=False, ax=None):
        '''Plots the asymmetric systematic uncertainty band on top of the MC stack, if `ratio` is set to False.
        To plot the systematic uncertainty in a ratio plot, `ratio` has to be set to True and the uncertainty band will be plotted around 1 in the ratio plot.'''
        ax = self.ax
        up = self.syst_manager.total.up
        down = self.syst_manager.total.down
        if ratio:
            # In order to get a consistent uncertainty band, the up/down variations of the ratio are set to 1 where the nominal value is 0
            ax = self.rax
            up = self.syst_manager.total.ratio_up
            down = self.syst_manager.total.ratio_down

        unc_band = np.array([down, up])
        ax.fill_between(
            self.xedges,
            np.r_[unc_band[0], unc_band[0, -1]],
            np.r_[unc_band[1], unc_band[1, -1]],
            **self.style.opts_unc['total'],
            label="syst. unc.",
        )
        if ratio:
            ax.hlines(1.0, *ak.Array(self.xedges)[[0,-1]], colors='gray', linestyles='dashed')

    def plot_datamc(self, year=None, ratio=True, syst=True, ax=None, rax=None):
        '''Plots the data histogram as an errorbar plot on top of the MC stacked histograms.
        If ratio is True, also the Data/MC ratio plot is plotted.
        If syst is True, also the total systematic uncertainty is plotted.'''
        if ratio:
            if self.is_mc_only:
                raise Exception("The Data/MC ratio cannot be plotted if the histogram is MC only.")
            if self.is_data_only:
                raise Exception("The Data/MC ratio cannot be plotted if the histogram is Data only.")

        if ax:
            self.ax = ax
        if rax:
            self.rax = rax
        if (not self.is_mc_only) & (not self.is_data_only):
            self.plot_mc()
            self.plot_data()
            if syst:
                self.plot_systematic_uncertainty()
        elif self.is_mc_only:
            self.plot_mc()
            if syst:
                self.plot_systematic_uncertainty()
        elif self.is_data_only:
            self.plot_data()

        if ratio:
            self.plot_datamc_ratio()
            if syst:
                self.plot_systematic_uncertainty(ratio)

        self.format_figure(ratio)

    def plot_datamc_all(self, ratio=True, syst=True, spliteras=False, save=True):
        '''Plots the data and MC histograms for each year and category contained in the histograms.
        If ratio is True, also the Data/MC ratio plot is plotted.
        If syst is True, also the total systematic uncertainty is plotted.'''
        for year in self.years:
            for cat in self.categories:
                if not any([c in cat for c in self.only_cat]):
                    continue
                self.define_figure(year, ratio)
                self.build_stacks(year, cat, spliteras)
                self.get_systematic_uncertainty()
                self.plot_datamc(year, ratio, syst)
                if save:
                    plot_dir = os.path.join(self.plot_dir, cat)
                    if self.log:
                        plot_dir = os.path.join(plot_dir, "log")
                    if not os.path.exists(plot_dir):
                        os.makedirs(plot_dir)
                    filepath = os.path.join(plot_dir, f"{self.name}_{year}_{cat}.png")
                    print("Saving", filepath)
                    plt.savefig(filepath, dpi=150, format="png")
                else:
                    plt.show(self.fig)
                plt.close(self.fig)


class SystManager:
    '''This class handles the systematic uncertainties of 1D MC histograms.'''
    def __init__(self, datamc : Shape, has_mcstat=True) -> None:
        self.datamc = datamc
        assert all([(var == "nominal") | var.endswith(("Up", "Down")) for var in self.datamc.variations]), "All the variations names that are not 'nominal' must end in 'Up' or 'Down'."
        self.variations_up = [var for var in self.datamc.variations if var.endswith("Up")]
        self.variations_down = [var for var in self.datamc.variations if var.endswith("Down")]
        assert len(self.variations_up) == len(self.variations_down), "The number of up and down variations is mismatching."
        self.systematics = [s.split("Up")[0] for s in self.variations_up]
        if has_mcstat:
            self.systematics.append("mcstat")
        self.syst_dict = {}

        for syst_name in self.systematics:
            self.syst_dict[syst_name] = SystUnc(self.datamc, syst_name)

    @property
    def total(self):
        total = SystUnc(name="total", syst_list=list(self.syst_dict.values()))
        return total

    @property
    def mcstat(self):
        return self.syst_dict["mcstat"]

    def get_syst(self, syst_name : str):
        '''Returns the SystUnc object corresponding to a given systematic uncertainty,
        passed as the argument `syst_name`.'''
        return self.syst_dict[syst_name]


class SystUnc:
    '''This class stores the information of a single systematic uncertainty of a 1D MC histogram.
    The built-in __add__() method implements the sum in quadrature of two systematic uncertainties,
    returning a `SystUnc` instance corresponding to their sum in quadrature.'''
    def __init__(self, datamc : Shape = None, name : str = None, syst_list : list = None) -> None:
        self.datamc = datamc
        self.name = name
        self.is_mcstat = self.name == "mcstat"

        # Initialize the arrays of the nominal yield and squared errors as 0
        self.nominal = 0.0
        self.err2_up = 0.0
        self.err2_down = 0.0
        if datamc:
            if syst_list:
                raise Exception("The initialization of the instance is ambiguous. Either a `DataMC` object or a list of `SystUnc` objects should be passed to the constructor.")
            else:
                self.syst_list = [self]
            self._get_err2()
            # Inherit style from Shape object
            self.style = self.datamc.style
            # Full nominal MC including all MC samples
            self.h_mc_nominal = self.datamc.stack_sum_mc_nominal
            self.nominal = self.h_mc_nominal.values()
            self.xlabel = self.datamc.xlabel
            self.xcenters = self.datamc.xcenters
            self.xedges = self.datamc.xedges
            self.xbinwidth = self.datamc.xbinwidth
        elif syst_list:
            self.syst_list = syst_list
            assert self.nsyst > 0, "Attempting to initialize a `SystUnc` instance with an empty list of systematic uncertainties."
            assert not ((self._n_empty == 1) & (self.nsyst == 1)), "Attempting to intialize a `SystUnc` instance with an empty systematic uncertainty."
            self._get_err2_from_syst()
            # Get default style
            self.style = Style()

    def __add__(self, other):
        '''Sum in quadrature of two systematic uncertainties.
        In case multiple objects are summed, the information on the systematic uncertainties that
        have been summed is stored in self.syst_list.'''
        return SystUnc(name=f"{self.name}_{other.name}", syst_list=[self, other])

    @property
    def up(self):
        return self.nominal + np.sqrt(self.err2_up)

    @property
    def down(self):
        return self.nominal - np.sqrt(self.err2_down)

    @property
    def ratio_up(self):
        return np.where(self.nominal != 0, self.up / self.nominal, 1)

    @property
    def ratio_down(self):
        return np.where(self.nominal != 0, self.down / self.nominal, 1)

    @property
    def nsyst(self):
        return len(self.syst_list)

    @property
    def _is_empty(self):
        return np.sum(self.nominal) == 0

    @property
    def _n_empty(self):
        return len([s for s in self.syst_list if s._is_empty])

    def _get_err2_from_syst(self):
        '''Method used in the constructor to instanstiate a SystUnc object from
        a list of SystUnc objects. The sytematic uncertainties in self.syst_list,
        are summed in quadrature to define a new SystUnc object.'''
        index_non_empty = [i for i, s in enumerate(self.syst_list) if not s._is_empty][0]
        self.nominal = self.syst_list[index_non_empty].nominal
        self.xlabel = self.syst_list[index_non_empty].xlabel
        self.xcenters = self.syst_list[index_non_empty].xcenters
        self.xedges = self.syst_list[index_non_empty].xedges
        self.xbinwidth = self.syst_list[index_non_empty].xbinwidth
        for syst in self.syst_list:
            if not ((self._is_empty) | (syst._is_empty)):
                assert all(np.equal(self.nominal, syst.nominal)), "Attempting to sum systematic uncertainties with different nominal MC."
                assert all(np.equal(self.xcenters, syst.xcenters)), "Attempting to sum systematic uncertainties with different bin centers."
            self.err2_up += syst.err2_up
            self.err2_down += syst.err2_up

    def _get_err2(self):
        '''Method used in the constructor to instanstiate a SystUnc object from
        a Shape object. The corresponding up/down squared uncertainties are stored and take
        into account the possibility for the uncertainty to be one-sided.'''
        # Loop over all the MC samples and sum the systematic uncertainty in quadrature
        for h in self.datamc.stack_mc:
            # Nominal variation for a single MC sample
            h_nom = h[{'variation': 'nominal'}]
            nom = h_nom.values()
            # Sum in quadrature of mcstat
            if self.is_mcstat:
                mcstat_err2 = h_nom.variances()
                self.err2_up += mcstat_err2
                self.err2_down += mcstat_err2
                continue
            # Up/down variations for a single MC sample
            var_up = h[{'variation': f'{self.name}Up'}].values()
            var_down = h[{'variation': f'{self.name}Down'}].values()
            # Compute the uncertainties corresponding to the up/down variations
            err_up = var_up - nom
            err_down = var_down - nom
            # Compute the flags to check which of the two variations (up and down) are pushing the nominal value up and down
            up_is_up = err_up > 0
            down_is_down = err_down < 0
            # Compute the flag to check if the uncertainty is one-sided, i.e. when both variations are up or down
            is_onesided = (up_is_up ^ down_is_down)

            # Sum in quadrature of the systematic uncertainties taking into account if the uncertainty is one- or double-sided
            err2_up_twosided = np.where(up_is_up, err_up**2, err_down**2)
            err2_down_twosided = np.where(up_is_up, err_down**2, err_up**2)
            err2_max = np.maximum(err2_up_twosided, err2_down_twosided)
            err2_up_onesided = np.where(is_onesided & up_is_up, err2_max, 0)
            err2_down_onesided = np.where(is_onesided & down_is_down, err2_max, 0)
            err2_up_combined = np.where(is_onesided, err2_up_onesided, err2_up_twosided)
            err2_down_combined = np.where(is_onesided, err2_down_onesided, err2_down_twosided)
            # Sum in quadrature of the systematic uncertainty corresponding to a MC sample
            self.err2_up += err2_up_combined
            self.err2_down += err2_down_combined

    def plot(self, ax=None):
        '''Plots the nominal, up and down systematic variations on the same plot.'''
        plt.style.use([hep.style.ROOT, {'font.size': self.style.fontsize}])
        plt.rcParams.update({'font.size': self.style.fontsize})
        if not ax:
            self.fig, self.ax  = plt.subplots(1, 1, **self.style.opts_figure["datamc"])
        else:
            self.ax = ax
            self.fig = self.ax.get_figure
        hep.cms.text("Simulation Preliminary", fontsize=self.style.fontsize, loc=0, ax=self.ax)
        #hep.cms.lumitext(text=f'{self.lumi[year]}' + r' fb$^{-1}$, 13 TeV,' + f' {year}', fontsize=self.style.fontsize, ax=self.ax)
        self.ax.hist(self.xcenters, weights=self.nominal, histtype="step", label="nominal", **self.style.opts_syst["nominal"])
        self.ax.hist(self.xcenters, weights=self.up, histtype="step", label=f"{self.name} up", **self.style.opts_syst["up"])
        self.ax.hist(self.xcenters, weights=self.down, histtype="step", label=f"{self.name} down", **self.style.opts_syst["down"])
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel("Counts")
        self.ax.legend()
        return self.fig, self.ax
