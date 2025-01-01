import yaml
import os
import time
import pandas as pd
import logging
from Bio import Entrez
from pathlib import Path

# var global
CONFIG = None
FILE_PATHS = None
PATH_ROOT = None

def load_config(config_path):
    """
    Load configuration from a YAML file.
    
    :param config_path: Path to the YAML configuration file.
    :return: Dictionary containing configuration data.
    """
    try:
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)
    
    except FileNotFoundError:
        # Log error if configuration file is not found
        raise FileNotFoundError(f"Configuration file not found at {config_path}. Please provide a valid path.")
    
    except yaml.YAMLError as e:
        # Log error if there is an issue parsing the YAML file
        raise ValueError(f"Error parsing YAML file: {e}")


def setup_directories(path_root, directories):
    """
    Create necessary directories if they don't exist.
    
    :param directories: List of directory paths to create.
    """
    try:
        # Iterate through the directory configurations
        for dir_type, dir_path in directories.items():
            
            dir_path = os.path.join(path_root, dir_path)
            dir_path = os.path.normpath(dir_path)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logging.info(f"Created directory: {dir_path}")
            else:
                logging.info(f"Directory already exists: {dir_path}")

    except Exception as e:
        logging.error(f"Error while processing YAML: {e}")
        print(f"Error while processing YAML: {e}")


def configure_logging(path_root, logging_config):
    """
    Configures logging based on the provided dictionary.

    Args:
        logging_config (dict): A dictionary containing logging configuration.

    Raises:
        ValueError: If logging configuration fails.
    """
    try:
        # Validate the logging configuration dictionary
        required_keys = ["log_file", "level", "format", "date_format"]
        for key in required_keys:
            if key not in logging_config:
                raise KeyError(f"Missing required logging configuration key: '{key}'")

        # Extract configuration values
        log_file = logging_config["log_file"]
        level = logging_config["level"].upper()

        log_dir1 = os.path.join(path_root, log_file)
        log_dir2 = os.path.normpath(log_dir1)
                
        # Configure logging
        logging.basicConfig(
            filename=log_dir2,
            level=getattr(logging, level, logging.INFO),
            format=logging_config["format"],
            datefmt=logging_config["date_format"]
        )
        # Test logging setup
        logging.info("Logging configuration successfully loaded.")

    except Exception as e:
        logging.error(f"Error configuring logging: {e}")
        raise ValueError(f"Error configuring logging: {e}")


def get_output_file_paths(file_config):
    """
    Get file paths for outputs based on configuration.
    
    :param file_config: Dictionary with file paths.
    :return: Dictionary of file paths.
    """
    try:
        return {
            key: Path(file_config[key]) for key in file_config
        }
    except KeyError as e:
        logging.error(f"Missing file path in configuration: {e}")
        raise KeyError(f"Missing file path in configuration: {e}")


# Function to save data to CSV files
def save_data_to_file(df, file_path):
    """
    Save the data from a DataFrame to a CSV file. 
    If the file does not exist, it will be created with headers.
    If the file already exists, the data will be appended without headers.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data to be saved.
        file_path (str): The full path of the CSV file.

    Error Handling:
        - Logs any exception that occurs while attempting to save the file.
    
    Example:
        save_data_to_file(my_dataframe, "data.csv")
    """
    try:
        if not os.path.exists(file_path):
            df.to_csv(file_path, sep='|', index=False)
        else:
            df.to_csv(file_path, sep='|', mode='a', header=False, index=False)
    except Exception as e:
        logging.error(f"Error saving file: {e}")


def load_csv_to_dataframe(file_path, separator="|"):
    """
    Load a CSV file into a Pandas DataFrame with error handling.

    Parameters:
        file_path (str): The path to the CSV file to load.
        separator (str): The separator used in the CSV file. Default is '|'.

    Returns:
        pd.DataFrame: The loaded DataFrame if successful.
        None: If the file could not be loaded.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None

    try:
        df = pd.read_csv(file_path, sep=separator, dtype=str)
        logging.info(f"DataFrame loaded successfully - total rows: {df.shape[0]}")
                
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing CSV: {e}")
    except Exception as e:
        logging.error(f"Unexpected error loading DataFrame: {e}")

    return None


from xml.dom.minidom import parseString

def save_xml_data(article_id, i, xml_data):
    """
    Saves provided XML data to a file named dynamically based on the article ID.
    
    Args:
        article_id (int or str): The ID of the article to use for naming the file.
        xml_data (str): The XML data to be saved to the file.
        
    Returns:
        str: The filename where the XML data was saved, or None if an error occurred.
    """
    try:
        PATH_XML = os.path.join(PATH_ROOT, CONFIG["directories"].get("xml", "xml"))
        path_xml_filename = os.path.join(PATH_XML, f"{i}_article_{article_id}.xml")
        path_xml_filename = os.path.normpath(path_xml_filename)
        
        decoded_data = xml_data.decode("utf-8")

        # Formata o XML automaticamente
        dom = parseString(decoded_data)  # Parse o XML
        formatted_xml = dom.toprettyxml(indent="  ")  # Adiciona identação e quebras de linha

        #print(formatted_xml)
        if not decoded_data:
            logging.warning(f"No XML data provided for article ID: {article_id} {i}")
            return None

        with open(path_xml_filename, "w", encoding="utf-8") as file:
            file.write(formatted_xml)

        logging.info(f"XML data successfully saved to file: {article_id} {i}")
        return True
    
    except Exception as e:
        logging.error(f"An error occurred while saving XML data for article ID {article_id} {i}: {e}", exc_info=True)
        return False


import sys
#cler log processing, files gerated
def clear_all_processec():
    """
    Deletes all log files in the specified directory.

    Args:
        log_dir (str): Path to the directory containing log files.
    """
    #print("clear files:", CONFIG["files"].items())
    for file_key, file_name in CONFIG["files"].items():
        path_file_name = os.path.join(OUTPUT_PATH, file_name)

        try:
            # Check if the file exists before attempting to delete
            if os.path.exists(path_file_name):
                os.remove(path_file_name)
                print(f"Removed file: {path_file_name}")
                logging.info(f"Removed file: {path_file_name}")    
            else:
                print(f"File {path_file_name} not found.")
                logging.info(f"File  {path_file_name} not found.")    

        except Exception as e:
            print(f"Error removing file {path_file_name}: {e}")
            logging.info(f"Error removing file  {path_file_name} :{e}")    


    #clear xml process
    FILE_XML = os.path.join(PATH_ROOT, CONFIG["directories"]["xml"])
    PATH_FILE_XML = os.path.normpath(os.path.join(PATH_ROOT, FILE_XML))

    # Iterate through all files in the directory
    for file_name in os.listdir(PATH_FILE_XML):
        file_path = os.path.join(PATH_FILE_XML, file_name)

        # Check if the current item is a file
        if os.path.isfile(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file: {file_name}")
        else:
            logging.warning(f"Skipping non-file item: {file_name}")


    # clean log file 
    FILE_LOG_TMP = os.path.join(PATH_ROOT, CONFIG["logging"].get("log_file", "execution.log"))
    FILE_LOG = os.path.normpath(FILE_LOG_TMP)

    # Open the file in write mode to clear its contents
    with open(FILE_LOG, 'w'):
        pass  # No content is written, so the file is cleared


def clear_directory(output_dir):
    """
    Remove todos os arquivos em um diretório especificado.
    """
    if not os.path.exists(output_dir):
        print(f"O diretório '{output_dir}' não existe.")
        return

    # Lista todos os arquivos no diretório
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        try:
            if os.path.isfile(file_path):  # Apenas remove arquivos, não subdiretórios
                os.remove(file_path)
                print(f"Arquivo removido: {file_path}")
        except Exception as e:
            print(f"Erro ao remover o arquivo '{file_path}': {e}")


# var global
CONFIG = None
FILE_PATHS = None
PATH_ROOT = None
INPUT_PATH = None
OUTPUT_PATH = None

def initialize_environment():
    """
    Initialize the application environment by loading configuration, 
    setting up directories, and configuring logging.
    """
    global CONFIG, FILE_PATHS, PATH_ROOT, INPUT_PATH, OUTPUT_PATH

    # Root path for the application
    PATH_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
    sys.path.append(PATH_ROOT)

    config_path = os.path.join(PATH_ROOT, 'config', 'config.yaml')
    CONFIG = load_config(config_path)
    
    configure_logging(PATH_ROOT, CONFIG["logging"])

    # Define email and API key for Entrez
    Entrez.email = CONFIG["api_email"]
    Entrez.api_key = CONFIG["api_key"] 

    setup_directories(PATH_ROOT, CONFIG["directories"])

    FILE_PATHS = get_output_file_paths(CONFIG["files"])
    logging.info(f"Environment initialized successfully.{PATH_ROOT}")

    #path input process
    DATA_INPUT_PATH_TMP = CONFIG["directories"]['input']
    INPUT_PATH = os.path.normpath(os.path.join(PATH_ROOT, DATA_INPUT_PATH_TMP))

    #path output process
    RESEARCH_OUTPUT_PATH_TMP = CONFIG["directories"]['output'] 
    OUTPUT_PATH     = os.path.normpath(os.path.join(PATH_ROOT, RESEARCH_OUTPUT_PATH_TMP))



