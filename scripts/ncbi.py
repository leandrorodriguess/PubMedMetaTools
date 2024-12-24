import logging
#from tqdm import tqdm
from Bio import Entrez


# Função para contar resultados da consulta
def request_count(query):
    """
    Performs a search query on the PubMed database and retrieves the total count of results and a list of article IDs.

    Args:
        query (str): The search term to query the PubMed database.

    Returns:
        tuple: A tuple containing:
            - int: The total number of results found.
            - list: A list of PubMed IDs (PMIDs) for the articles retrieved by the query.
    
    Raises:
        Exception: If an error occurs during the request, it will be logged.
    """
    try:
        # Perform the search query on PubMed
        handle = Entrez.esearch(db="pubmed", term=query, retmax=200)
        record = Entrez.read(handle)
        handle.close()
        
        # Return the total count and the list of IDs
        return int(record["Count"]), record.get("IdList", [])
    
    except Exception as e:
        # Log the error and return default values
        logging.error(f"Error during query execution: {e}")
        return 0, []
    
    
def request_data(id):
    try:
        handle = Entrez.efetch(db="pubmed", query_key="1", id=id, retstart=0,
                                retmax=5, rettype="xml")
        xml_data = handle.read()
        #print(xml_data)
        handle.close()
          
        return xml_data
    except Exception as e:
        logging.error(f"Error during data fetch: {e}")
        return []


