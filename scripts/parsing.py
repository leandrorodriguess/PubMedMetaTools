"""
parsing.py

This module contains functions to process PubMed XML data.
"""

import xml.etree.ElementTree as ET
import pandas as pd
import logging


def extract_abstract_text(article):
    """
    Extrai e concatena textos de AbstractText, lidando com casos com ou sem o atributo 'Label'.
    """
    # Lista para armazenar os fragmentos
    abstract_fragments = []

    # Itera sobre todas as tags <AbstractText>
    for abstract in article.findall('.//Abstract/AbstractText'):
        # Verifica se a tag possui o atributo Label
        label = abstract.attrib.get('Label', '').strip()  # Obtém o valor de 'Label', se existir
        text = abstract.text.strip() if abstract.text else ""  # Texto principal da tag

        # Concatena o label e o texto principal, se existir
        if label:
            fragment = f"{label}: {text}"
        else:
            fragment = text

        # Adiciona o fragmento à lista
        abstract_fragments.append(fragment)

        # Inclui textos residuais após sub-tags (e.g., <b>, <sup>)
        for sub_element in abstract:
            if sub_element.tail:
                abstract_fragments.append(sub_element.tail.strip())

    # Retorna o texto concatenado
    return "".join(abstract_fragments)



def process_mesh_headings(article):
    """
    Processa os MeshHeadings de um artigo XML e cria uma string formatada conforme as regras.
    """
    mesh_descriptors = []

    # Itera sobre todas as tags MeshHeading
    for mesh_heading in article.findall('.//MeshHeadingList/MeshHeading'):
        # Localiza a tag DescriptorName e verifica o atributo MajorTopicYN
        descriptor_element = mesh_heading.find('DescriptorName')
        if descriptor_element is not None:
            descriptor = descriptor_element.text.strip()
            # Adiciona o asterisco se MajorTopicYN="Y"
            if descriptor_element.attrib.get('MajorTopicYN') == "Y":
                descriptor = f"*{descriptor}"
        else:
            descriptor = ""  # Define como vazio se não encontrar DescriptorName

        qualifiers = []  # Lista para armazenar os QualifierName processados

        # Itera sobre as tags QualifierName associadas ao MeshHeading
        for qualifier in mesh_heading.findall('QualifierName'):
            qualifier_text = qualifier.text.strip()
            # Adiciona o asterisco se MajorTopicYN="Y" no QualifierName
            if qualifier.attrib.get('MajorTopicYN') == "Y":
                qualifier_text = f"*{qualifier_text}"
            qualifiers.append(qualifier_text)

        # Concatena DescriptorName com os QualifierNames usando "/"
        if descriptor:  # Somente adiciona se o descriptor não for vazio
            full_descriptor = f"{descriptor}/{'/'.join(qualifiers)}" if qualifiers else descriptor
            mesh_descriptors.append(full_descriptor)

    # Retorna a string final concatenada com "; "
    return "; ".join(mesh_descriptors)



def process_mesh_headings_bibliometrix(article):
    """
    Processa os MeshHeadings de um artigo XML e cria uma string formatada conforme as regras.
    """
    mesh_descriptors = []

    # Itera sobre todas as tags MeshHeading
    for mesh_heading in article.findall('.//MeshHeadingList/MeshHeading'):
        # Localiza a tag DescriptorName e verifica o atributo MajorTopicYN
        descriptor_element = mesh_heading.find('DescriptorName')
        if descriptor_element is not None:
            descriptor = descriptor_element.text.strip()
            # Adiciona o asterisco se MajorTopicYN="Y"
            if descriptor_element.attrib.get('MajorTopicYN') == "Y":
                descriptor = f"{descriptor}"
        else:
            descriptor = ""  # Define como vazio se não encontrar DescriptorName

        qualifiers = []  # Lista para armazenar os QualifierName processados

        # Itera sobre as tags QualifierName associadas ao MeshHeading
        for qualifier in mesh_heading.findall('QualifierName'):
            qualifier_text = qualifier.text.strip()
            # Adiciona o asterisco se MajorTopicYN="Y" no QualifierName
            if qualifier.attrib.get('MajorTopicYN') == "Y":
                qualifier_text = f"{qualifier_text}"
            qualifiers.append(qualifier_text)

        # Concatena DescriptorName com os QualifierNames usando "/"
        if descriptor:  # Somente adiciona se o descriptor não for vazio
            full_descriptor = f"{descriptor};{';'.join(qualifiers)}" if qualifiers else descriptor
            mesh_descriptors.append(full_descriptor)

    # Retorna a string final concatenada com "; "
    return "; ".join(mesh_descriptors)



def parse_xml_to_df(xml_data, df=None):
    """
    Parse PubMed XML data and append the extracted metadata to an existing DataFrame.

    Args:
        xml_data (str): String containing the PubMed XML data.
        df (pd.DataFrame, optional): Existing DataFrame to append new rows to. Defaults to None.

    Returns:
        pd.DataFrame: Updated DataFrame containing parsed PubMed article metadata.
    """
    # Parse the XML
    root = ET.fromstring(xml_data)

    # Create an empty DataFrame if none is provided
    if df is None:
        df = pd.DataFrame()

    # List to temporarily store rows
    rows = []

    # Iterate through articles in the XML
    for article in root.findall('.//PubmedArticle'):
        row = {}

        # Direct mapping with XML tag names
        row["PMID"] = article.findtext('.//PMID')
        row["ArticleTitle"] = article.findtext('.//ArticleTitle')
        row["JournalTitle"] = article.findtext('.//Journal/Title')
        row["ISOAbbreviation"] = article.findtext('.//Journal/ISOAbbreviation')
        row["Country"] = article.findtext('.//MedlineJournalInfo/Country')
        row["Volume"] = article.findtext('.//JournalIssue/Volume')
        row["Pages"] = article.findtext('.//Pagination/MedlinePgn')
        row["ISSN"] = article.findtext('.//ISSN')
        row["Language"] = article.findtext('.//Language')
        row["AbstractText"] = article.findtext('.//Abstract/AbstractText')
        row["CopyrightInformation"] = article.findtext('.//Abstract/CopyrightInformation', "")
        row["DOI"] = article.findtext(".//ELocationID[@EIdType='doi']")
        row["PII"] = article.findtext(".//ELocationID[@EIdType='pii']")

        row["PublicationYear"] = article.findtext('.//JournalIssue/PubDate/Year')
        row["PublicationSeason"] = article.findtext('.//JournalIssue/PubDate/Season')


        # Authors and affiliations
        authors = []
        affiliations = []
        for author in article.findall('.//Author'):
            last_name = author.findtext('LastName', default="")
            fore_name = author.findtext('ForeName', default="")
            initials = author.findtext('Initials', default="")
            full_name = f"{last_name}, {fore_name} {initials}".strip(", ")
            authors.append(full_name)
            
            affiliation = author.findtext('.//AffiliationInfo/Affiliation', default="")
            if affiliation:
                affiliations.append(affiliation)

        row["Authors"] = "; ".join(authors)
        row["Affiliations"] = "; ".join(affiliations)

        # Keywords and MeSH terms
        keywords = [kw.text for kw in article.findall('.//Keyword') if kw.text]
        mesh_terms = [
            f"{mesh.findtext('DescriptorName')} (MajorTopic: {mesh.find('DescriptorName').get('MajorTopicYN', 'N')})"
            for mesh in article.findall('.//MeshHeading')
        ]

        row["Keywords"] = "; ".join(keywords)
        row["MeshTerms"] = "; ".join(mesh_terms)

        # Chemical substances
        chemicals = [
            chemical.findtext('NameOfSubstance', default="")
            for chemical in article.findall('.//Chemical')
        ]
        row["ChemicalSubstances"] = "; ".join(chemicals)

        # Grants
        grants = [grant.findtext('GrantID', default="") for grant in article.findall('.//Grant')]
        grant_agencies = [grant.findtext('Agency', default="") for grant in article.findall('.//Grant')]

        row["GrantIDs"] = "; ".join(grants)
        row["GrantOrganizations"] = "; ".join(grant_agencies)

        # Document types
        doc_types = [dt.text for dt in article.findall('.//PublicationType') if dt.text]
        row["DocumentTypes"] = "; ".join(doc_types)

        # Additional fields
        row["Status"] = article.find('.//MedlineCitation').get('Status', 'Unknown')
        row["LastRevisionDate"] = article.findtext('.//DateRevised/Year') + "-" + \
                                  article.findtext('.//DateRevised/Month') + "-" + \
                                  article.findtext('.//DateRevised/Day')
        row["CompletionDate"] = article.findtext('.//DateCompleted/Year') + "-" + \
                                article.findtext('.//DateCompleted/Month') + "-" + \
                                article.findtext('.//DateCompleted/Day')

        # Publication history
        history = []
        for pub_date in article.findall('.//PubMedPubDate'):
            status = pub_date.get("PubStatus", "unknown")
            date = f"{pub_date.findtext('Year')}-{pub_date.findtext('Month')}-{pub_date.findtext('Day')}"
            history.append(f"{status}: {date}")
        row["PublicationHistory"] = "; ".join(history)

        # Conflict of interest
        row["ConflictOfInterest"] = article.findtext(".//CoiStatement")

        # PubMed Central ID
        row["PMCID"] = article.findtext(".//ArticleId[@IdType='pmc']")

        # Citações
        citations = []
        for reference in article.findall('.//ReferenceList/Reference'):
            citation_text = reference.findtext('Citation', default="")
            if citation_text:
                citations.append(citation_text)
        row["Citations"] = "; ".join(citations)




def parse_xml_to_bibliometrix_df(xml_data, df=None):
    """
    Parse PubMed XML data and append the extracted metadata to an existing DataFrame.

    Args:
        xml_data (str): String containing the PubMed XML data.
        df (pd.DataFrame, optional): Existing DataFrame to append new rows to. Defaults to None.

    Returns:
        pd.DataFrame: Updated DataFrame containing parsed PubMed article metadata.
    """
    if df is None:
        df = pd.DataFrame()

    try:
        # Parse the XML
        root = ET.fromstring(xml_data)

        # Create an empty DataFrame if none is provided
        if df is None:
            df = pd.DataFrame()

        # List to temporarily store rows
        rows = []

        # Iterate through articles in the XML
        for article in root.findall('.//PubmedArticle'):
            row = {}

            # Direct mapping with XML tag names
            row["PMID"] = article.findtext('.//PMID')
            row["ArticleTitle"] = article.findtext('.//ArticleTitle')
            row["JournalTitle"] = article.findtext('.//Journal/Title')
            row["ISOAbbreviation"] = article.findtext('.//Journal/ISOAbbreviation')
            row["Country"] = article.findtext('.//MedlineJournalInfo/Country')
            row["Volume"] = article.findtext('.//JournalIssue/Volume')
            row["Pages"] = article.findtext('.//Pagination/MedlinePgn')
            row["ISSN"] = article.findtext('.//ISSN')
            row["Language"] = article.findtext('.//Language')
            row["AbstractText"] = extract_abstract_text(article) 
            row["CopyrightInformation"] = article.findtext('.//Abstract/CopyrightInformation', "")
            row["DOI"] = article.findtext(".//ELocationID[@EIdType='doi']")
            row["PII"] = article.findtext(".//ELocationID[@EIdType='pii']")

            row["PublicationYear"] = article.findtext('.//JournalIssue/PubDate/Year')
            row["PublicationSeason"] = article.findtext('.//JournalIssue/PubDate/Season')


            # Authors and affiliations
            authors = []
            affiliations = []
            for author in article.findall('.//Author'):
                last_name = author.findtext('LastName', default="")
                fore_name = author.findtext('ForeName', default="")
                initials = author.findtext('Initials', default="")
                full_name = f"{last_name}, {fore_name} {initials}".strip(", ")
                authors.append(full_name)
                
                affiliation = author.findtext('.//AffiliationInfo/Affiliation', default="")
                if affiliation:
                    affiliations.append(affiliation)

            row["Authors"] = "; ".join(authors)
            row["Affiliations"] = "; ".join(affiliations)

            # Keywords and MeSH terms
            keywords = [kw.text for kw in article.findall('.//Keyword') if kw.text]
            #mesh_terms = [
            #    f"{mesh.findtext('DescriptorName')} (MajorTopic: {mesh.find('DescriptorName').get('MajorTopicYN', 'N')})"
            #    for mesh in article.findall('.//MeshHeading')
            #]

            row["Keywords"] = "; ".join(keywords)
            #row["MeshTerms"] = "; ".join(mesh_terms)
            row["MeshTerms"] = process_mesh_headings_bibliometrix(article)
            
            # Chemical substances
            chemicals = [
                chemical.findtext('NameOfSubstance', default="")
                for chemical in article.findall('.//Chemical')
            ]
            row["ChemicalSubstances"] = "; ".join(chemicals)

            # Grants
            grants = [grant.findtext('GrantID', default="") for grant in article.findall('.//Grant')]
            grant_agencies = [grant.findtext('Agency', default="") for grant in article.findall('.//Grant')]

            row["GrantIDs"] = "; ".join(grants)
            row["GrantOrganizations"] = "; ".join(grant_agencies)

            # Document types
            doc_types = [dt.text for dt in article.findall('.//PublicationType') if dt.text]
            row["DocumentTypes"] = "; ".join(doc_types)

            # Additional fields
            row["Status"] = article.find('.//MedlineCitation').get('Status', 'Unknown')

            year_revised = article.findtext('.//DateRevised/Year')
            month_revised = article.findtext('.//DateRevised/Month')
            day_revised = article.findtext('.//DateRevised/Day')
            
            row["LastRevisionDate"] = f"{year_revised or '0000'}-{month_revised or '00'}-{day_revised or '00'}"
                   
            year_completed = article.findtext('.//DateCompleted/Year')
            month_completed = article.findtext('.//DateCompleted/Month')
            day_completed = article.findtext('.//DateCompleted/Day')

            row["CompletionDate"] = f"{year_completed or '0000'}-{month_completed or '00'}-{day_completed or '00'}"

            # Publication history
            history = []
            for pub_date in article.findall('.//PubMedPubDate'):
                status = pub_date.get("PubStatus", "unknown")
                date = f"{pub_date.findtext('Year')}-{pub_date.findtext('Month')}-{pub_date.findtext('Day')}"
                history.append(f"{status}: {date}")
            row["PublicationHistory"] = "; ".join(history)

            # Conflict of interest
            row["ConflictOfInterest"] = article.findtext(".//CoiStatement")

            # PubMed Central ID
            row["PMCID"] = article.findtext(".//ArticleId[@IdType='pmc']")

            # Citações
            citations = []
            for reference in article.findall('.//ReferenceList/Reference'):
                citation_text = reference.findtext('Citation', default="")
                if citation_text:
                    citations.append(citation_text)
            row["Citations"] = "; ".join(citations)

            rows.append(row)

        # Convert the list of dictionaries into a DataFrame and concatenate it with the existing one
        new_df = pd.DataFrame(rows)
        df = pd.concat([df, new_df], ignore_index=True)

        return df
    except ET.ParseError as e:
        logging.error(f"Error parsing XML data: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


def parse_xml_to_pubmed_df(xml_data, df=None):
    """
    Parse PubMed XML data, extracting all relevant fields and appending them to an existing DataFrame.

    Args:
        xml_data (str): String containing the PubMed XML data.
        df (pd.DataFrame, optional): Existing DataFrame to append new rows to. Defaults to None.

    Returns:
        pd.DataFrame: Updated DataFrame containing parsed PubMed article metadata.
    """
    if df is None:
        df = pd.DataFrame()

    try:
        root = ET.fromstring(xml_data)
        rows = []

        for article in root.findall('.//PubmedArticle'):
            row = {}

            try:     
                # Core fields from XML
                row["PMID"] = article.findtext('.//PMID', "Unknown")
                row["Owner"] = article.find('.//MedlineCitation').get('Owner', 'Unknown')

                # MedlineCitation Status
                row["MedlineCitation.Status"] = article.find('.//MedlineCitation').get('Status', "Unknown")
                row["DataBankName"] = article.findtext('.//DataBankName', "Unknown")

                row["PublicationStatus"] = article.findtext('.//PublicationStatus', "Unknown")


                # DateCompleted and DateRevised
                row["DateCompleted"] = "".join(
                    filter(None, [
                        article.findtext('.//DateCompleted/Year'),
                        article.findtext('.//DateCompleted/Month'),
                        article.findtext('.//DateCompleted/Day')
                    ])
                )
                row["DateRevised"] = "".join(
                    filter(None, [
                        article.findtext('.//DateRevised/Year'),
                        article.findtext('.//DateRevised/Month'),
                        article.findtext('.//DateRevised/Day')
                    ])
                )
                # Extração do campo ArticleDate no formato esperado
                row["ArticleDate"] = "".join(
                    filter(None, [
                            article.findtext('.//ArticleDate/Year'),
                            article.findtext('.//ArticleDate/Month'),
                            article.findtext('.//ArticleDate/Day'),
                        ])
                )

                row["ELocationDOI"] = root.findtext('.//ELocationID[@EIdType="doi"]', "Unknown")
                row["LocationPII"] = root.findtext('.//ELocationID[@EIdType="pii"]', "Unknown")
                row["ArticleIdListPII"] = root.findtext('.//ArticleId[@IdType="pii"]', "Unknown")
                row["ArticleIdListDOI"] = root.findtext('.//ArticleId[@IdType="doi"]', "Unknown")


                # ISSN and Linking
                row["ISSN"] = article.findtext('.//ISSN[@IssnType="Electronic"]', "Unknown")
                row["ISSNLinking"] = article.findtext('.//ISSNLinking', "Unknown")

                # Journal Issue
                row["JournalIssue.Volume"] = article.findtext('.//JournalIssue/Volume', "Unknown")
                row["JournalIssue.Issue"] = article.findtext('.//JournalIssue/Issue', "Unknown")
                row["PubDate.Year"] = article.findtext('.//PubDate/Year', "Unknown")
                row["PublicationSeason"] = article.findtext('.//JournalIssue/PubDate/Season', "Unknown")

                # Article Title and Abstract
                row["ArticleTitle"] = article.findtext('.//ArticleTitle', "Unknown")
                #row["Abstract.AbstractText"] = " ".join(
                #    [abstract.text.strip() for abstract in article.findall('.//Abstract/AbstractText') if abstract.text]
                #)
                row["Abstract.AbstractText"] = extract_abstract_text(article)
                row["CopyrightInformation"] = article.findtext('.//Abstract/CopyrightInformation', "Unknown")

                # StartPage and MedlinePgn
                row["StartPage"] = article.findtext('.//StartPage', "Unknown")
                row["MedlinePgn"] = article.findtext('.//MedlinePgn', "Unknown")

                # AccessionNumber
                accession_number = article.findtext('.//AccessionNumberList/AccessionNumber', None)
                row["AccessionNumber"] = accession_number if accession_number else "Unknown"

                # PubMedPubDate fields
                pub_dates = article.findall('.//PubMedPubDate')
                for pub_date in pub_dates:
                    status = pub_date.get('PubStatus', "unknown")
                    year = pub_date.findtext('Year', "")
                    month = pub_date.findtext('Month', "").zfill(2)
                    day = pub_date.findtext('Day', "").zfill(2)
                    hour = pub_date.findtext('Hour', "00").zfill(2)
                    minute = pub_date.findtext('Minute', "00").zfill(2)
                    formatted_date = f"{year}/{month}/{day} {hour}:{minute}"
                    if status == "received":
                        row["PubMedPubDateReceived"] = formatted_date
                    elif status == "accepted":
                        row["PubMedPubDateAccepted"] = formatted_date
                    elif status == "entrez": 
                        row["PubMedPubDateEntrez"] = formatted_date
                    elif status == "pubmed":
                        row["PubMedPubDatePubmed"] = formatted_date
                    elif status == "medline":
                        row["PubMedPubDateMedline"] = formatted_date

                # PublicationStatus
                row["PublicationStatus"] = article.findtext('.//PublicationStatus', "Unknown")

                # Country
                row["Country"] = article.findtext('.//MedlineJournalInfo/Country', "Unknown")

                # MedlineTA
                row["MedlineTA"] = article.findtext('.//MedlineJournalInfo/MedlineTA', "Unknown")

                # Title
                row["Title"] = article.findtext('.//Journal/Title', "Unknown")

                # NlmUniqueID
                row["NlmUniqueID"] = article.findtext('.//MedlineJournalInfo/NlmUniqueID', "Unknown")

                # CitationSubset
                row["CitationSubset"] = article.findtext('.//CitationSubset', "Unknown")
               
                row["MeshHeadingList"] = process_mesh_headings(article)

                 # OT
                keyword_list = article.find('.//KeywordList')
                if keyword_list is not None:
                    row["Keyword"] = keyword_list.get("Owner", "Unknown")
                else:
                    row["Keyword"] = "Unknown"

                keywords = []
                for keyword in article.findall('.//Keyword'):
                    keyword_value = keyword.text.strip() if keyword.text else "Unknown"
                    major_topic_yn = keyword.get("MajorTopicYN", "Unknown")
                    keywords.append(f"{keyword_value}")

                # Adicionar ao campo KeywordList
                row["KeywordList"] = "; ".join(keywords)

                # ArticleIdList PMC
                row["ArticleIdListPMC"] = article.findtext('.//ArticleId[@IdType="pmc"]', "Unknown")

                # Language and PublicationType
                row["Language"] = article.findtext('.//Language', "Unknown")
                row["PublicationType"] = "; ".join(
                    [pt.text for pt in article.findall('.//PublicationType') if pt.text]
                )

                # Author list
                # Author list
                authors = []
                authors_dtl = []

               # Inicializando listas para armazenar informações dos autores
                authors = []
                authors_dtl = []

                # Iterando pela lista de autores
                for author in article.findall('.//Author'):
                    # Extraindo detalhes básicos
                    fore_name = author.findtext('ForeName', "").strip()
                    last_name = author.findtext('LastName', "").strip()
                    initials = author.findtext('Initials', "").strip()
                    full_name = f"{last_name}, {fore_name}".strip(", ")
                    authors.append(full_name)

                    # Extraindo ORCID (se disponível)
                    orcid = author.findtext(".//Identifier[@Source='ORCID']", "").strip()

                    # Extraindo afiliações
                    affiliations = [
                        aff.text.strip() for aff in author.findall(".//AffiliationInfo/Affiliation") if aff.text
                    ]

                    # Formatando a string detalhada do autor
                    author_detail = f"FAU:{full_name}|AU:{last_name} {initials}"
                    if orcid:
                        author_detail += f"|AUID:{orcid}"
                    if affiliations:
                        author_detail += f"|AD:{' |AD: '.join(affiliations)}"
                    authors_dtl.append(author_detail)

                    # Salvando as informações em um dicionário ou DataFrame
                    row["AuthorListAuthor"] = "| ".join(authors)
                    row["AuthorListDTL"] = "| ".join(authors_dtl)

                    # Exibindo o resultado
                    #print("Autores Simples:", row["AuthorListAuthor"])
                    #print("Autores Detalhados:", row["AuthorListDTL"])

                # CoiStatement
                row["CoiStatement"] = article.findtext('.//CoiStatement', "Unknown")

                #print(xml_data)
                logging.info(row)
                rows.append(row)

            except Exception as e:
                logging.error(f"Error parsing article: {e}")
        
        
        logging.info("Adicionando Row in DF: %s",rows)
        new_df = pd.DataFrame(rows)
        df = pd.concat([df, new_df], ignore_index=True)
        
        logging.info("Parsing completed successfully.")
        return df

    except ET.ParseError as e:
        logging.error(f"Error parsing XML data: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise