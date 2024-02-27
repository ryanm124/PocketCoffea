import os
import sys
import json
import argparse
import click

from pocket_coffea.utils import dataset

@click.command()
@click.option(
    '--cfg',
    default=os.getcwd() + "/datasets/datasets_definitions.json",
    help='Config file with parameters specific to the current run',
    required=True,
)
@click.option(
    "-k", "--keys", 
    type=str, 
    multiple=True, 
    help="Keys of the datasets to be created. If None, the keys are read from the datasets definition file."
)
@click.option(
    '-d',
    '--download',
    is_flag=True,
    default=False,
    help='Download datasets from DAS',
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help="Overwrite existing .json datasets",
)
@click.option(
    '-c',
    '--check',
    is_flag=True,
    help="Check existence of the datasets",
)
@click.option(
    '-s',
    '--split-by-year',
    is_flag=True,
    help="Split datasets by year",
)
@click.option("-l", "--local-prefix", type=str, default=None)
@click.option(
    "-ws",
    "--whitelist-sites",
    type=str,
    multiple=True,
)
@click.option(
    "-bs",
    "--blacklist-sites",
    type=str,
    multiple=True,
)
@click.option("-rs", "--regex-sites", type=str)
@click.option("-p", "--parallelize", type=int, default=4)
def build_datasets(cfg, keys, download, overwrite, check,
         split_by_year, local_prefix, whitelist_sites, blacklist_sites, regex_sites, parallelize):
    '''Build dataset fileset in json format'''
    dataset.build_datasets(cfg=cfg,
                           keys=keys,
                           download=download,
                           overwrite=overwrite,
                           check=check,
                           split_by_year=split_by_year,
                           local_prefix=local_prefix,
                           whitelist_sites=whitelist_sites,
                           blacklist_sites=blacklist_sites,
                           regex_sites=regex_sites,
                           parallelize=parallelize)



if __name__ == "__main__":
    build_datasets()
