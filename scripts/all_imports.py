# Imports de bibliotecas padrão
import os
import sys
import time
import logging
from pathlib import Path
import yaml
import pandas as pd
from Bio import Entrez

# Imports de módulos internos do projeto
from scripts.utils import initialize_environment, save_data_to_file, load_csv_to_dataframe, save_xml_data, clear_all_processec, clear_directory
from scripts.ncbi import request_count, request_data
from scripts.parsing import parse_xml_to_bibliometrix_df, parse_xml_to_pubmed_df
from scripts.mapping import map_pubmed_to_bibliometrix, map_pubmed_to_bibtex, map_pubmed_to_ris, map_to_pubmed_format, map_web_of_science_file, map_pubmed_to_bibliometrix_extended



# Lista de elementos exportados
__all__ = [
    "os",
    "sys",
    "time",
    "logging",
    "Path",
    "yaml",
    "pd",
    "Entrez",
    "initialize_environment",
    "save_data_to_file",
    "load_csv_to_dataframe",
    "save_xml_data",
    "clear_all_processec",
    "request_count",
    "request_data",
    "parse_xml_to_bibliometrix_df",
    "parse_xml_to_pubmed_df",
    "map_pubmed_to_bibliometrix",
    "map_pubmed_to_bibtex", 
    "map_pubmed_to_ris", 
    "map_to_pubmed_format",
    "map_web_of_science_file",
    "map_pubmed_to_bibliometrix_extended",
    "clear_directory"
]

# Inicializa o ambiente
initialize_environment()