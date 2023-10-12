# Plots

In order to produce Data/MC plots from the .coffea output file a dedicated `make_plots.py` script is implemented.

The plotting procedure is managed by several classes each targeting a specific task:

- `Shape`: for each histogram a `Shape` object is instantiated, storing all the relevant metadata and parameters.
- `SystUnc`: manages the systematic uncertainties. For each systematic uncertainty, a `SystUnc` object is instantiated. The up/down variations are stored in this object. These objects can be summed with each other to get their sum in quadrature.
- `PlotManager`: manages and stores several `Shape` objects to produce plots in all possible categories, exploiting multiprocessing.
- `SystManager`: manages several systematic uncertainties to get the total systematic uncertainty or MCstat only.

## Produce data/MC plots

Once the output .coffea file has been produced, plots can be produced by executing the plotting script:

```
cd /path/to/output/folder
make_plots.py --cfg parameters_dump.yaml -op plotting_style.yaml -i output_all.coffea -o plots -j 8
```

The `make_plots.py` takes as **required** arguments:

- `--cfg`: The .yaml config file dumped after running the analysis, containing all the analysis parameters
- `-o`: Output folder where the plots are saved
- `-i`: Input .coffea file with histograms

The optional arguments are:

- `-op`: Additional .yaml config file to overwrite the plotting style when plotting
- `-j`: Number of workers used for plotting
- `--only_cat`: Filter categories with a list of strings
- `--only_syst`: Filter systematics with a list of strings
- `--exclude_hist`: Exclude histograms with a list of strings
- `--split_systematics`: Split systematic uncertainties in the ratio plot
- `--partial_unc_band`: Plot only the partial uncertainty band corresponding to the systematics specified as the argument `only_syst`
- `--overwrite`: If the output folder is already existing, overwrite its content
- `--log`: Set y-axis scale to log
- `--density`: Set density parameter to have a normalized plot

## Plotting parameters

The parameters provided by the `--cfg` argument can be overwritten by providing an additional parameter to the script with `--overwrite_parameters` (`-op`).

The structure of the additional .yaml config file has to be the following:
```
plotting_style:

    labels_mc:
        TTToSemiLeptonic: "$t\\bar{t}$ semilep."
        TTTo2L2Nu : "$t\\bar{t}$ dilepton"

    colors_mc:
        TTTo2L2Nu: [0.51, 0.79, 1.0]
        TTToSemiLeptonic: [1.0, 0.71, 0.24]

    samples_groups:
        ttbar:
            TTTo2L2Nu
            TTToSemiLeptonic
```

The user can define custom labels for the MC samples and a custom coloring scheme. Additionally, the Data and MC samples can be merged between each other by specifying a dictionary of samples in the `samples_groups` key. In the example above, a single sample `ttbar` will be plotted by merging the samples `TTTo2L2Nu` and `TTToSemiLeptonic`.
