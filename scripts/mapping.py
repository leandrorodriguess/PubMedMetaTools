import xml.etree.ElementTree as ET
import pandas as pd

"""
mapping.py

This module converts the data from a DataFrame to the desired final formats.
"""

import pandas as pd
import re
import logging
import os
import pandas as pd
import textwrap
import textwrap


def quebra_texto_com_identificador(texto, comprimento_max, espacos_iniciais=6):
    linhas_originais = texto.splitlines()
    linhas_quebradas = []

    try:

        for linha in linhas_originais:
            # Preservar os primeiros 6 caracteres como identificador
            identificador = linha[:6]
            conteudo = linha[6:].strip()

            if len(linha) > comprimento_max:
                palavras = conteudo.split()
                linha_atual = ""
                primeira_linha = True
                for palavra in palavras:
                    if len(linha_atual) + len(palavra) + 1 <= comprimento_max - espacos_iniciais:
                        linha_atual += (palavra + " ") if linha_atual else palavra
                    else:
                        if primeira_linha:
                            linhas_quebradas.append(identificador + linha_atual.strip())
                            primeira_linha = False
                        else:
                            linhas_quebradas.append(" " * espacos_iniciais + linha_atual.strip())
                        linha_atual = palavra
                if linha_atual:
                    if primeira_linha:
                        linhas_quebradas.append(identificador + linha_atual.strip())
                    else:
                        linhas_quebradas.append(" " * espacos_iniciais + linha_atual.strip())
            else:
                linhas_quebradas.append(linha)
    except Exception as e:
        logging.error(f"An error occurred mapping.py: {e}") 
        print(f"An error occurred mapping.py: {e}")

    return "\n".join(linhas_quebradas)



def map_to_pubmed_format(df_pubmed, output_file):
    """
    Processa os dados de um arquivo PubMed e grava o resultado formatado no caminho de saída especificado.
    
    Args:
        input_file (str): Caminho para o arquivo de entrada.
        output_path (str): Caminho para salvar o arquivo de saída.
    """

    # Nome do arquivo de saída
    #output_file = "formatted_pubmed_output.txt"

    # Inicializar a lista de linhas formatadas
    formatted_rows = []
    formatted_rows_AUX = []

    # Definindo a ordem e estrutura dos campos conforme o arquivo mcda_pubmed.txt
    field_order = [
        "PMID", "OWN", "STAT", "DCOM", "LR", "IS", "VI", "IP", "DP",
        "TI", "PG", "LID", "AB", "CI", "FAU", "AU", "AUID", "AD", "LA", "SI",
        "PT", "DEP", "PL", "TA", "JT", "JID", "RN", "SB", "MH", "PMC", "COIS", "OTO",
        "OT", "EDAT", "MHDA", "CRDT", "PHST", "AID", "PST", "SO"
    ]
    variables = ["AB", "TI"]
    # Dicionário de mapeamento dos campos
    field_mapping = {
        "PMID": "PMID",                         # Identificador único do artigo no PubMed.
        "OWN": "Owner",                         # Entidade que possui ou gerencia o registro do artigo no PubMed.
        "STAT": "MedlineCitation.Status",       # Status do artigo no banco de dados (e.g., publicado, em revisão).
        "DCOM": "DateCompleted",                # Data de conclusão do processamento do artigo no PubMed.
        "LR": "DateRevised",                    # Última data de revisão ou atualização do registro no PubMed.
        "IS": "ISSN",                           # Código ISSN (International Standard Serial Number) da publicação.
        "VI": "JournalIssue.Volume",            # Volume da edição do periódico onde o artigo foi publicado.
        "IP": "JournalIssue.Issue",             # Número da edição do periódico.
        "DP": "PubDate.Year",                   # Ano de publicação do artigo.
        "TI": "ArticleTitle",                   # Título do artigo.
        "PG": "MedlinePgn",                     # Páginas do artigo na publicação.
        "LID": "ArticleIdListDOI",              # DOI (Digital Object Identifier) do artigo.
        "AB": "Abstract.AbstractText",          # Texto do resumo do artigo.
        "CI": "CopyrightInformation",           # Informações de direitos autorais do artigo.
        "FAU": "AuthorList.Author",             # Lista de autores do artigo (nome completo).
        "AU": "AuthorList.Author",              # Lista de autores do artigo (abreviado).
        "AUID": "AuthorList.Identifier",        # Identificador único dos autores.
        "AD": "AffiliationInfo.Affiliation",    # Informações de afiliação dos autores (instituições).
        "LA": "Language",                       # Idioma do artigo.
        "SI": "AccessionNumber",                # Número de acesso, usado para identificar registros relacionados.
        "PT": "PublicationType",                # Tipo de publicação (e.g., revisão, artigo original).
        "DEP": "ArticleDate",                   # Data de publicação eletrônica do artigo (se disponível).
        "PL": "Country",                        # País de origem do periódico.
        "TA": "MedlineTA",                      # Abreviação do título do periódico.
        "JT": "Title",                          # Título completo do periódico.
        "JID": "NlmUniqueID",                   # Identificador único do periódico no banco de dados.
        "RN": "RN",                             # Número de registro de substâncias químicas citadas no artigo (CAS Registry Number).
        "SB": "CitationSubset",                 # Subconjunto de citações ou áreas temáticas associadas ao artigo.
        "MH": "MeshHeadingList",                # Termos MeSH (Medical Subject Headings) associados ao artigo.
        "PMC": "ArticleIdListPMC",              # Identificador do artigo no PubMed Central.
        "COIS": "CoiStatement",                 # Declaração de conflitos de interesse dos autores.
        "OT": "KeywordList",                    # Lista de palavras-chave associadas ao artigo.
        "EDAT": "PubMedPubDatePubmed",          # Data em que o artigo foi adicionado ao PubMed.
        "MHDA": "PubMedPubDateMedline",         # Data em que o artigo foi indexado no Medline.
        "CRDT": "PubMedPubDateEntrez",          # Data em que o registro foi adicionado ao banco de dados Entrez.
        "PHST": "PubMedPubDateReceived",        # Histórico de datas do processo editorial (e.g., recebido, aceito).
        "AID": "ArticleIdListDOI",              # DOI do artigo (campo duplicado com LID).
        "SO": "Title",                          # Fonte do artigo (título do periódico).
        "PST": "PublicationStatus",             # Status da publicação (e.g., online, impresso).
        "OTO": "Keyword"                        # Palavra-chave adicional associada ao artigo.
    }

    try:

        # Abrir o arquivo para escrita
        with open(output_file, "w") as file:
            # Iterar sobre as linhas do DataFrame (apenas a primeira linha)
            
            for _, row in df_pubmed.iterrows():

                # Caso 'row' seja uma string e você espere um dicionário:
                # Processar campos de autores detalhados (AuthorListDTL)
                author_list_dtl = row.get("AuthorListDTL", None)
                if author_list_dtl:
                    author_blocks = author_list_dtl.split("FAU:")
                    author_blocks = [f"FAU:{block}" for block in author_blocks if block.strip()]
                    formatted_rows_AUX.clear()
                    formatted_rows.clear()

                    for block in author_blocks:
                        fields = block.split("|")
                        for field in fields:
                            field = field.strip()
                            if field.startswith("FAU:"):
                                formatted_rows_AUX.append(f"FAU - {field.replace('FAU:', '').strip()}")
                            elif field.startswith("AU:") and field.replace("AU:", "").strip() != "Unknown":
                                formatted_rows_AUX.append(f"AU  - {field.replace('AU:', '').strip()}")
                            elif field.startswith("AUID:") and field.replace("AUID:", "").strip() != "Unknown":
                                formatted_rows_AUX.append(f"AUID- ORCID: {field.replace('AUID:', '').strip()}")
                            elif field.startswith("AD:") and field.replace("AD:", "").strip() != "Unknown":
                                formatted_rows_AUX.append(f"AD  - {field.replace('AD:', '').strip()}")

                # Processar campos restantes na ordem definida
                for field in field_order:
                    source_field = field_mapping.get(field, "Unknown")
                    value = row.get(source_field, "Unknown")

                    if field == "FAU" and formatted_rows_AUX:
                        formatted_rows.append("\n".join(formatted_rows_AUX))
                        continue
            

                    # Processar Mesh Heading
                    if field == "MH":
                        mesh_terms = str(value).split("; ") if value else []
                        for term in mesh_terms:
                            term = term.strip()
                            formatted_rows.append(f"MH  - {term}")
                        continue

                    # Processar campo SI
                    processed_entries = set()
                    if field == "SI":
                        entry = f'SI  - {row.get("DataBankName", None)}/{value}'

                    if field == "PT":
                        pt_terms = str(value).split("; ") if value else []
                        for term in pt_terms:
                            term = term.strip()
                            formatted_rows.append(f"PT  - {term}")
                        continue
                    
                    if field == "DP":
                        # Obtém o PublicationSeason e verifica se é diferente de "Unknown"
                        publication_season = row.get("PublicationSeason", "Unknown")
                        if publication_season != "Unknown":
                            entry = f'DP  - {value} {publication_season}'
                        else:
                            entry = f'DP  - {value}'  # Caso PublicationSeason seja "Unknown"
                        formatted_rows.append(entry)  # Certifique-se de onde entry deve ser armazenado
                        continue


                    if value == "Unknown" or pd.isnull(value):
                        continue  # Ignorar campos com valor "Unknown" ou nulos

                    if field == "PHST":
                        phst_mappings = {
                            "PubMedPubDateReceived": "received",
                            "PubMedPubDateAccepted": "accepted",
                            "PubMedPubDateEntrez": "entrez",
                            "PubMedPubDatePubmed": "pubmed",
                            "PubMedPubDateMedline": "medline",
                        }
                        for phst_field, status in phst_mappings.items():
                            date_value = row.get(phst_field, "Unknown")
                            if date_value != "Unknown":
                                formatted_rows.append(f"PHST- {date_value} [{status}]")
                        continue

                    # Processar campo AID
                    if field == "AID":
                        phst_mappings = {
                            "ArticleIdListPII": "pii",
                            "ArticleIdListDOI": "doi",
                        }
                        for phst_field, status in phst_mappings.items():
                            date_value = row.get(phst_field, "Unknown")
                            if date_value != "Unknown":
                                formatted_rows.append(f"AID - {date_value} [{status}]")
                        continue

                    # Processar campo OTO
                    if field == "OT":
                        pt_terms = str(value).split("; ") if value else []
                        for term in pt_terms:
                            term = term.strip()
                            formatted_rows.append(f"OT  - {term}")
                        continue

                    if field == "LID" and value != "Unknown":
                        phst_mappings = {
                            "ELocationDOI": "doi",
                            "ELocationPII": "pii",
                        }
                        for phst_field, status in phst_mappings.items():
                            date_value = row.get(phst_field, "Unknown")
                            if date_value != "Unknown":
                                formatted_rows.append(f"LID - {date_value} [{status}]")
                        continue

                        #formatted_rows.append(f"LID - {value} [doi]")
                        #MedlinePgn = row.get("MedlinePgn", None)
                        #if ArticleIdListPII:
                        #    value_pii = row.get(ArticleIdListPII, "Unknown")
                        #    formatted_rows.append(f"LID - {value_pii} [pii]")
                        #continue
                    
                    if field == "IS":
                        issn_electronic = row.get("ISSN", None)
                        issn_linking = row.get("ISSNLinking", None)
                        if issn_electronic:
                            formatted_rows.append(f"IS  - {issn_electronic} (Electronic)")
                        if issn_linking:
                            formatted_rows.append(f"IS  - {issn_linking} (Linking)")
                        continue
                    
                    if field == "SO":    
                        # Processar o campo SO com base no field_mapping
                        journal_name = row.get(field_mapping["TA"], "Unknown")  # Nome do periódico (TA)
                        publication_date = row.get(field_mapping["DP"], "Unknown")  # Data de publicação (DP)
                        
                        # Processar mês e dia, se existirem
                        if "PubDate.Month" in row:  # Usa o mapeamento se o campo estiver presente
                            publication_date += f" {row.get('PubDate.Month', '')} "
                        if "PubDate.Day" in row:
                            publication_date += f" {row.get('PubDate.Day', '')}"

                        volume = row.get(field_mapping["VI"], "Unknown")  # Volume (VI)
                        issue = row.get(field_mapping["IP"], "Unknown")  # Número (IP)
                        page_or_article_id = row.get(field_mapping["PG"], row.get(field_mapping["LID"], "Unknown"))  # Página ou ID (PG, LID)
                        doi = row.get(field_mapping["AID"], "Unknown")  # DOI (AID)
                        publication_season =  row.get("PublicationSeason", "Unknown")  

                        # Construir o campo SO com os componentes disponíveis
                        so_components = [
                            f"{journal_name}.",
                            f"{publication_date} {publication_season};" if publication_date != "Unknown" and publication_season != "Unknown" else f"{publication_date};" if publication_date != "Unknown" else "",
                            f"{volume}({issue}):" if volume != "Unknown" and issue != "Unknown" else "",
                            f"{page_or_article_id}.",
                            f"doi: {doi}." if doi != "Unknown" else ""
                        ]
                        formatted_so = " ".join(filter(None, so_components)).strip()

                        # Adicionar o campo SO ao resultado formatado
                        formatted_rows.append(f"SO  - {formatted_so}")

                        # Marcar como processado
                        processed_entries.add("SO")
                        continue

                    formatted_rows.append(f"{field[:4].ljust(4)}- {value.strip()}")
                    formatted_rows = [quebra_texto_com_identificador(row, 87) for row in formatted_rows]

                #wrapped_rows = format_pubmed_entry2(formatted_rows, max_width=86, prefix_width=4)
                
                # Escrever as linhas formatadas no arquivo
                file.write("\n".join(formatted_rows) + "\n\n")
        
        logging.info(f"Data converted:") 

    except Exception as e:
        logging.error(f"An error occurred mapping.py: {e}") 
        print(f"An error occurred mapping.py: {e}")

    



def map_pubmed_to_bibliometrix(df_pubmed, output_file):
    """
    Processa um DataFrame PubMed e salva no formato Excel.

    Parâmetros:
        df_pubmed (pd.DataFrame): DataFrame contendo os dados do PubMed.
        output_file (str): Caminho do arquivo de saída no formato Excel.
    """
    # Map PubMed XML names to bibliometrix format
    mapping = {
        "Authors": "AU",
        "Affiliations": "C1",
        "ArticleTitle": "TI",
        "JournalTitle": "SO",
        "Country": "SO_CO",
        "Language": "LA",
        "DocumentTypes": "DT",
        "Keywords": "DE",
        "ChemicalSubstances": "ID",
        "MeshTerms": "MESH",
        "AbstractText": "AB",
        "ISOAbbreviation": "JI",
        "ISSN": "SN",
        "Pages": "PG",
        "Volume": "VL",
        "DOI": "DI",
        "PublicationYear": "PY",
        "GrantIDs": "GRANT_ID",
        "GrantOrganizations": "GRANT_ORG",
        "PMID": "PMID"
    }

    import pandas as pd
    import re

    # Funções auxiliares
    def clean_affiliation(affiliation):
        if not affiliation:
            return ""
        affiliation = re.sub(r"\[.*?\]", "", affiliation)
        return re.sub(r"\s+", " ", affiliation.strip())

    def extract_universities(affiliation):
        if not affiliation:
            return "NOTREPORTED"
        affiliations = affiliation.split(";")
        universities = [aff for aff in affiliations if any(keyword in aff.upper() for keyword in university_keywords)]
        return ";".join(universities) if universities else "NOTREPORTED"

    def extract_countries(affiliation):
        if not affiliation:
            return ""
        for country, abbr in country_mappings.items():
            if country in affiliation.upper():
                return abbr
        return ""

    def generate_short_reference(row):
        first_author = row["Authors"].split(";")[0].strip() if "Authors" in row and pd.notna(row["Authors"]) else "NA"
        year = str(int(row["PublicationYear"])) if "PublicationYear" in row and pd.notna(row["PublicationYear"]) else "NA"
        source = row["JournalTitle"] if "JournalTitle" in row and pd.notna(row["JournalTitle"]) else "NA"
        return f"{first_author}, {year}, {source}"

    def deduplicate_sr(data):
        duplicates = data.duplicated(subset=["SR"], keep=False)
        duplicate_count = {}
        for idx, is_duplicate in enumerate(duplicates):
            if is_duplicate:
                sr_value = data.at[idx, "SR"]
                if sr_value not in duplicate_count:
                    duplicate_count[sr_value] = 1
                else:
                    duplicate_count[sr_value] += 1
                data.at[idx, "SR"] = f"{sr_value}-{chr(96 + duplicate_count[sr_value])}"

    def clean_surrogates(text):
        if isinstance(text, str):
            return text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        return text

    # Palavras-chave para identificação de universidades
    university_keywords = ["UNIV", "COLL", "SCH", "INST", "ACAD", "CTR", "SCI", "HOSP", "ASSOC", "FOUNDAT", "LAB", "TECH", "RES", "FAC", "CENTER"]

    # Mapeamento de países para abreviações
    country_mappings = {
        "UNITED STATES": "USA",
        "RUSSIAN FEDERATION": "RUSSIA",
        "TAIWAN": "CHINA",
        "ENGLAND": "UNITED KINGDOM",
        "SCOTLAND": "UNITED KINGDOM",
        "WALES": "UNITED KINGDOM",
        "NORTH IRELAND": "UNITED KINGDOM"
    }

    # Trabalhar com o DataFrame df_pubmed diretamente
    data = df_pubmed.copy()
    data.fillna("", inplace=True)

    # Normalização de campos
    data["Affiliations_cleaned"] = data["Affiliations"].apply(clean_affiliation)
    data["AU_UN"] = data["Affiliations_cleaned"].apply(extract_universities)
    data["AU_CO"] = data["Affiliations_cleaned"].apply(extract_countries)
    data["AU_UN_NR"] = data["AU_UN"].apply(lambda x: "NOTREPORTED" if x == "NOTREPORTED" else "")
    data["SR_FULL"] = data.apply(generate_short_reference, axis=1)
    data["SR"] = data["SR_FULL"]

    # Remover duplicatas em SR
    deduplicate_sr(data)

    # Remover caracteres inválidos
    data = data.applymap(clean_surrogates)

    # Rename columns in the DataFrame
    df_mapped = data.rename(columns=mapping)

    # Add default fields if they do not exist
    for col in ["TC", "DB", "AU_UN", "PY_IS", "J9", "UT"]:
        if col not in df_mapped.columns:
            df_mapped[col] = None

    # Fill additional fields with default values
    df_mapped["DB"] = "PUBMED"
    df_mapped["UT"] = df_mapped["PMID"]

    # Salvar no formato Excel
    df_mapped.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Arquivo processado salvo em: {output_file}")





import pandas as pd
import re

def map_pubmed_to_bibliometrix_extended(df_pubmed, output_file, additional_columns):
    """
    Process PubMed DataFrame and save in Excel format with extended columns.

    Parameters:
        df_pubmed (pd.DataFrame): DataFrame with PubMed data.
        output_file (str): Path for the output Excel file.
        additional_columns (list): List of additional columns to ensure they are included.
    """
    # Lista de campos extraídos para análise bibliométrica
    # Cada campo representa uma informação específica da base de dados utilizada (e.g., Web of Science, Scopus):
    # AU: Nome(s) do(s) autor(es) do artigo.
    # AF: Nome completo do(s) autor(es), conforme aparece na publicação.
    # CR: Referências citadas no artigo (citações listadas no estilo usado na publicação).
    # AB: Resumo do artigo, descrevendo os principais objetivos e descobertas.
    # C1: Endereços institucionais afiliados ao(s) autor(es), com nomes de instituições e departamentos.
    # DE: Palavras-chave do autor, indicando os principais tópicos abordados no artigo.
    # DI: DOI (Digital Object Identifier), identificador digital único para o artigo.
    # DT: Tipo de documento (e.g., artigo, revisão, conferência).
    # FU: Fontes de financiamento ou agências de fomento que apoiaram o trabalho.
    # FX: Informações adicionais fornecidas no campo de agradecimentos.
    # ID: Palavras-chave atribuídas por indexadores (diferentes das palavras-chave do autor).
    # IS: Número da edição do periódico onde o artigo foi publicado.
    # J9: Nome abreviado do periódico (abreviação padrão).
    # JI: ISSN do periódico (International Standard Serial Number).
    # LA: Idioma em que o artigo foi publicado.
    # OA: Indica se o artigo é de acesso aberto (open access).
    # PU: Editora responsável pela publicação do periódico ou conferência.
    # PY: Ano de publicação do artigo.
    # RP: Endereço de correspondência do autor principal.
    # SO: Nome completo do periódico onde o artigo foi publicado.
    # TC: Número total de citações recebidas pelo artigo.
    # TI: Título do artigo.
    # UT: Número de registro único atribuído pela base de dados (e.g., Web of Science).
    # VL: Volume do periódico onde o artigo foi publicado.
    # C1raw: Campo bruto contendo informações não processadas sobre endereços institucionais (antes da normalização).
    # DB: Base de dados de onde os dados bibliométricos foram extraídos (e.g., Web of Science, Scopus).
    # AU_UN: Instituições afiliadas ao(s) autor(es), após normalização.
    # AU1_UN: Instituição afiliada ao primeiro autor, após normalização.
    # AU_UN_NR: Número de instituições únicas afiliadas ao(s) autor(es).
    # SR_FULL: Referência completa (Source Reference), incluindo título, autor(es), periódico e outros detalhes da publicação.
    # SR: Referência abreviada (citação simplificada usada na análise).

    # Map PubMed XML names to bibliometrix format
    mapping = {
        "Authors": "AU",
        "Authors": "AF",
        "Citations": "CR",
        "AbstractText": "AB",
        "Affiliations": "C1",
        "Keywords": "DE",
        "DOI":"DI",
        "DocumentTypes": "DT",
        "GrantOrganizations":"FU",
        "": "FX",                       ##
        "ChemicalSubstances": "ID",
        "Volume":"IS",
        "ISOAbbreviation": "J9",
        "ISSN": "JI",
        "Language": "LA",        
        "":"OA",                        ##
        "":"PU",                        ##
        "PublicationYear": "PY",
        "":"RP",                        ##
       "JournalTitle": "SO",
        "":"TC",                        ##
        "ArticleTitle": "TI",
        "PMID":"UT",
        "Volume": "VL",
        "PUBMED":"DB",
        "Country": "SO_CO",
        "MeshTerms": "MESH",
        "ISSN": "SN",
        "Pages": "PG",
        "GrantIDs": "GRANT_ID",
        "GrantOrganizations": "GRANT_ORG"
    }

    # Functions for cleaning and processing data
    def clean_affiliation(affiliation):
        if not affiliation:
            return ""
        affiliation = re.sub(r"\[.*?\]", "", affiliation)
        return re.sub(r"\s+", " ", affiliation.strip())

    def generate_short_reference(row):
        first_author = row["Authors"].split(";")[0].strip() if "Authors" in row and pd.notna(row["Authors"]) else "NA"
        #year = str(int(row["PublicationYear"])) if "PublicationYear" in row and pd.notna(row["PublicationYear"]) else "NA"
        year = (
            str(int(row["PublicationYear"])) 
            if "PublicationYear" in row and pd.notna(row["PublicationYear"]) and str(row["PublicationYear"]).strip().isdigit()
            else "NA"
        )
        #year = str(int(row["PublicationYear"])) if "PublicationYear" in row and pd.notna(row["PublicationYear"]) else "NA"
        source = row["JournalTitle"] if "JournalTitle" in row and pd.notna(row["JournalTitle"]) else "NA"
        return f"{first_author}, {year}, {source}"

    def clean_surrogates(text):
        if isinstance(text, str):
            return text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        return text

    # Normalize data
    data = df_pubmed.copy()
    data.fillna("", inplace=True)
    data["Affiliations_cleaned"] = data["Affiliations"].apply(clean_affiliation)
    data["SR_FULL"] = data.apply(generate_short_reference, axis=1)
    data["SR"] = data["SR_FULL"]

    # Remove invalid characters
    data = data.applymap(clean_surrogates)

    # Rename columns in the DataFrame
    df_mapped = data.rename(columns=mapping)

    # Ensure additional columns are included
    for col in additional_columns:
        if col not in df_mapped.columns:
            df_mapped[col] = None

    # Fill default fields
    #df_mapped["DB"] = "PUBMED"
    #df_mapped["UT"] = df_mapped["PMID"]

    # Filtrar e organizar as colunas
    df_filtered = df_mapped.reindex(columns=additional_columns, fill_value=None)

    # Save to Excel
    df_filtered.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Arquivo processado salvo em: {output_file}")




def map_pubmed_to_bibliometrix_old(df):
    """
    Maps a DataFrame containing PubMed article data to the format expected by bibliometrix.

    Bibliometrix is a bibliometric analysis tool that uses a specific field format.
    This function renames the DataFrame columns according to the bibliometrix format
    and adds default fields if they are missing.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the original PubMed data.

    Returns:
        pd.DataFrame: A DataFrame mapped and adapted to the bibliometrix format.

    Field Mapping:
        - "Authors" → "AU": Article authors.
        - "Affiliations" → "C1": Institutional affiliations.
        - "ArticleTitle" → "TI": Article title.
        - "JournalTitle" → "SO": Journal title.
        - "Country" → "SO_CO": Country associated with the article.
        - "Language" → "LA": Language of the article.
        - "DocumentTypes" → "DT": Document types.
        - "Keywords" → "DE": Keywords.
        - "ChemicalSubstances" → "ID": Mentioned chemical substances.
        - "MeshTerms" → "MESH": Associated MeSH terms.
        - "AbstractText" → "AB": Abstract text.
        - "ISOAbbreviation" → "JI": Journal's ISO abbreviation.
        - "ISSN" → "SN": Journal's ISSN.
        - "Pages" → "PG": Article pages.
        - "Volume" → "VL": Journal volume.
        - "DOI" → "DI": Article DOI.
        - "PublicationYear" → "PY": Publication year.
        - "GrantIDs" → "GRANT_ID": Grant identifiers.
        - "GrantOrganizations" → "GRANT_ORG": Granting organizations.
        - "PMID" → "PMID": PubMed unique identifier.

    Main Steps:
        1. Rename the DataFrame columns using the mapping dictionary.
        2. Add missing required fields with default values (e.g., "TC", "DB", "AU_UN").
        3. Fill the "DB" field with the value "PUBMED".
        4. Copy the "PMID" value to the "UT" field (global unique identifier).

    Usage Example:
        mapped_df = map_pubmed_to_bibliometrix(original_df)
    """
    
    # Map PubMed XML names to bibliometrix format
    mapping = {
        "Authors": "AU",
        "Affiliations": "C1",
        "ArticleTitle": "TI",
        "JournalTitle": "SO",
        "Country": "SO_CO",
        "Language": "LA",
        "DocumentTypes": "DT",
        "Keywords": "DE",
        "ChemicalSubstances": "ID",
        "MeshTerms": "MESH",
        "AbstractText": "AB",
        "ISOAbbreviation": "JI",
        "ISSN": "SN",
        "Pages": "PG",
        "Volume": "VL",
        "DOI": "DI",
        "PublicationYear": "PY",
        "GrantIDs": "GRANT_ID",
        "GrantOrganizations": "GRANT_ORG",
        "PMID": "PMID"
    }

    # Rename columns in the DataFrame
    df_mapped = df.rename(columns=mapping)

    # Add default fields if they do not exist
    for col in ["TC", "DB", "AU_UN", "PY_IS", "J9", "UT"]:
        if col not in df_mapped.columns:
            df_mapped[col] = None

    # Fill additional fields with default values
    df_mapped["DB"] = "PUBMED"
    df_mapped["UT"] = df_mapped["PMID"]

    return df_mapped



# Define a function to convert the data to BibTeX format
def map_pubmed_to_bibtex(df):
    bib_entries = []
    for _, row in df.iterrows():
        # Identify the type of document
        doc_type = row['DT'].lower().replace(' ', '') if pd.notnull(row['DT']) else 'article'
        
        # Start the BibTeX entry
        entry = [f"@{doc_type}{{"]
        
        if pd.notnull(row['PMID']):
            entry.append(f"{row['PMID']},")
        
        if pd.notnull(row['AU']):
            authors = ' and '.join([author.strip() for author in row['AU'].split(';')])
            entry.append(f"  author = {{{authors}}},")
        
        if pd.notnull(row['TI']):
            entry.append(f"  title = {{{row['TI']}}},")
        
        if pd.notnull(row['SO']):
            entry.append(f"  journal = {{{row['SO']}}},")
        
        if pd.notnull(row['DI']):
            entry.append(f"  doi = {{{row['DI']}}},")
        
        if pd.notnull(row['PG']):
            entry.append(f"  pages = {{{row['PG']}}},")
        
        if pd.notnull(row['LA']):
            entry.append(f"  language = {{{row['LA']}}},")
        
        if pd.notnull(row['DE']):
            keywords = ', '.join([kw.strip() for kw in row['DE'].split(';')])
            entry.append(f"  keywords = {{{keywords}}},")
        
        entry.append("}")
        bib_entries.append("\n".join(entry))
    
    return "\n\n".join(bib_entries)




# Now we will convert this data to RIS format. RIS format requires specific field names, 
# so let's map the relevant fields to RIS tags.
def map_pubmed_to_ris(df):
    ris_entries = []
    for _, row in df.iterrows():
        entry = []
        if pd.notnull(row['AU']):
            for author in row['AU'].split(';'):
                entry.append(f"AU  - {author.strip()}")
        if pd.notnull(row['TI']):
            entry.append(f"TI  - {row['TI']}")
        if pd.notnull(row['SO']):
            entry.append(f"JO  - {row['SO']}")
        if pd.notnull(row['DT']):
            entry.append(f"TY  - {row['DT']}")
        if pd.notnull(row['LA']):
            entry.append(f"LA  - {row['LA']}")
        if pd.notnull(row['DE']):
            entry.append(f"KW  - {row['DE']}")
        if pd.notnull(row['DI']):
            entry.append(f"DO  - {row['DI']}")
        if pd.notnull(row['PG']):
            entry.append(f"SP  - {row['PG']}")
        if pd.notnull(row['PMID']):
            entry.append(f"ID  - {row['PMID']}")
        entry.append("ER  -")  # End of record
        ris_entries.append("\n".join(entry))
    
    return "\n\n".join(ris_entries)


import pandas as pd
import os
from datetime import datetime
import numpy as np



def export_to_scopus_format_v2(df, output_path):
    """
    Export a DataFrame to the detailed Scopus format with all necessary fields.

    Args:
        df (pd.DataFrame): DataFrame containing the processed data.
        output_path (str): Path where the output file will be saved.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Scopus\n")
        f.write("EXPORT DATE: 24 November 2024\n\n")

        for _, row in df.iterrows():
            # Autores
            authors = row.get('Authors', 'Unknown Authors')
            author_ids = row.get('AuthorIDs', 'Unknown IDs')
            f.write(f"{authors}\n")
            f.write(f"AUTHOR FULL NAMES: {authors} ({author_ids})\n")
            f.write(f"{author_ids}\n")

            # Título
            f.write(f"{row.get('ArticleTitle', 'No Title')}\n")

            # Publicação
            journal = row.get('JournalTitle', 'Unknown Journal')
            year = row.get('PublicationYear', 'Unknown Year')
            volume = row.get('Volume', '')
            issue = row.get('Issue', '')
            pages = row.get('Pages', 'No Pages')
            art_no = row.get('ArticleNumber', 'No Article Number')
            cited_by = row.get('Cited By', '0 times')
            f.write(f"({year}) {journal}, {volume}({issue}), {pages}, art. no. {art_no}, Cited {cited_by}.\n")

            # DOI e link
            doi = row.get('DOI', 'No DOI')
            eid = row.get('EID', 'No EID')
            link = f"https://www.scopus.com/inward/record.uri?eid={eid}&doi={doi}"
            f.write(f"DOI: {doi}\n")
            f.write(f"{link}\n\n")

            # Afiliações
            affiliations = row.get('Affiliations', 'No Affiliations')
            f.write(f"AFFILIATIONS: {affiliations}\n\n")

            # Abstract
            abstract = row.get('Abstract', 'No Abstract')
            f.write(f"ABSTRACT: {abstract}\n\n")

            # Keywords
            keywords = row.get('Keywords', 'No Keywords')
            f.write(f"AUTHOR KEYWORDS: {keywords}\n\n")

            # Index Keywords
            index_keywords = row.get('IndexKeywords', 'No Index Keywords')
            f.write(f"INDEX KEYWORDS: {index_keywords}\n\n")

            # Funding Details
            funding_details = row.get('FundingInformation', 'No Funding Information')
            f.write(f"FUNDING DETAILS: {funding_details}\n\n")

            # Publisher
            publisher = row.get('Publisher', 'No Publisher')
            f.write(f"PUBLISHER: {publisher}\n")

            # Identificadores adicionais
            pubmed_id = row.get('PMID', 'No PubMed ID')
            f.write(f"PUBMED ID: {pubmed_id}\n")

            # ISSN
            issn = row.get('ISSN', 'No ISSN')
            f.write(f"ISSN: {issn}\n")

            # Idioma
            language = row.get('Language', 'No Language')
            f.write(f"LANGUAGE OF ORIGINAL DOCUMENT: {language}\n")

            # Tipo de documento
            document_type = row.get('DocumentType', 'No Document Type')
            f.write(f"DOCUMENT TYPE: {document_type}\n")

            # Open Access
            open_access = row.get('OpenAccess', 'No Open Access Info')
            f.write(f"OPEN ACCESS: {open_access}\n\n")

            # Referências
            references = row.get('References', 'No References')
            f.write(f"REFERENCES: {references}\n\n")

            # Separador entre entradas
            f.write("------------------------------------------------------------\n\n")

    print(f"Scopus-formatted file exported successfully to {output_path}")


#OK
def map_web_of_science_file(df, output_path):
    """
    Gera um arquivo formatado de acordo com o padrão Web of Science.
    Aplica funções de limpeza e normalização antes de processar cada linha.
    """

    # Funções auxiliares encapsuladas
    def clean_text(text):
        if pd.isna(text):
            return ""
        return text.strip().replace("\n", " ").replace("\r", "")

    def split_references(refs):
        if pd.isna(refs) or refs == "":
            return []
        return [ref.strip() for ref in refs.split(";")]

    def normalize_identifier(identifier):
        if pd.isna(identifier) or identifier == "":
            return None
        return identifier.strip().lower()

    def normalize_date(date):
        if pd.isna(date) or date == "":
            return None
        try:
            return pd.to_datetime(date, errors="coerce").strftime("%Y-%m-%d")
        except Exception:
            return None

    # Limpeza e normalização dos dados
    for col in df.columns:
        df[col] = df[col].apply(clean_text)
    df["References"] = df["References"].apply(split_references)
    df["PMID"] = df["PMID"].apply(normalize_identifier)
    df["DOI"] = df["DOI"].apply(normalize_identifier)
    df["OnlinePublicationDate"] = df["OnlinePublicationDate"].apply(normalize_date)

    # Gerar o arquivo formatado
    with open(output_path, 'w', encoding='utf-8') as file:
        # Adicionar cabeçalho indicando o padrão Web of Science
        file.write("FN Clarivate Analytics Web of Science\n")
        file.write("VR 1.0\n\n")  # Versão do formato

        for _, row in df.iterrows():
            file.write(f"PT {row.get('PublicationType', 'J')}\n")
            file.write("AU " + "\n".join(row.get('Authors', '').split('; ')) + "\n")
            file.write(f"TI {row.get('DocumentTitle', '')}\n")
            file.write(f"SO {row.get('PublicationName', '')}\n")
            file.write(f"LA {row.get('Language', 'eng')}\n")
            file.write(f"DT {row.get('DocumentType', '')}\n")
            file.write(f"DE {'; '.join(row.get('Keywords', []))}\n")
            file.write(f"ID {'; '.join(row.get('MeshTerms', []))}\n")
            file.write(f"AB {row.get('Abstract', '')}\n")
            file.write(f"C1 {row.get('AuthorAddress', '')}\n")
            file.write(f"RP {row.get('ReprintAddress', '')}\n")
            file.write(f"EM {row.get('EmailAddress', '')}\n")
            file.write(f"FU {row.get('FundingAgency', '')}\n")
            file.write(f"FX {row.get('FundingText', '')}\n")
            file.write(f"CR {'; '.join(row.get('References', []))}\n")
            file.write(f"NR {len(row.get('References', []))}\n")
            file.write(f"TC {row.get('TimesCited', 0)}\n")
            file.write(f"Z9 {row.get('TotalTimesCited', 0)}\n")
            file.write(f"U1 {row.get('UsageCountLast180Days', 0)}\n")
            file.write(f"U2 {row.get('UsageCountSince2013', 0)}\n")
            file.write(f"PU {row.get('Publisher', '')}\n")
            file.write(f"PI {row.get('PublisherCity', '')}\n")
            file.write(f"PA {row.get('PublisherAddress', '')}\n")
            file.write(f"SN {row.get('ISSN', '')}\n")
            file.write(f"EI {row.get('EISSN', '')}\n")
            file.write(f"J9 {row.get('ISOAbbreviation', '')}\n")
            file.write(f"JI {row.get('SourceAbbreviation', '')}\n")
            file.write(f"PD {row.get('PublicationDate', '')}\n")
            file.write(f"PY {row.get('YearPublished', '')}\n")
            file.write(f"VL {row.get('Volume', '')}\n")
            file.write(f"IS {row.get('Issue', '')}\n")
            file.write(f"BP {row.get('BeginningPage', '')}\n")
            file.write(f"EP {row.get('EndingPage', '')}\n")
            file.write(f"DI {row.get('DOI', '')}\n")
            file.write(f"PG {row.get('PageCount', '')}\n")
            file.write(f"WC {row.get('WebOfScienceCategories', '')}\n")
            file.write(f"SC {row.get('ResearchAreas', '')}\n")
            file.write(f"GA {row.get('DocumentDeliveryNumber', '')}\n")
            file.write(f"UT {row.get('AccessionNumber', '')}\n")
            file.write(f"PM {row.get('PubMedID', '')}\n")
            file.write(f"OA {row.get('OpenAccessIndicator', '')}\n")
            file.write(f"DA {row.get('ReportGeneratedDate', '')}\n")
            file.write(f"ER\n\n")
        file.write("EF\n")

