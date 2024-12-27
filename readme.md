
# PubMedMetaTool: PubMed Metadata Extraction Tool Based on DOI and/or Title for Composing Metadata for Bibliometric Analysis

**Version**: 1.0  
**Authors**: Souza, Leandro Rodrigues da Silva et al.  
**License**: GPLv2 License  

---


## Overview

This repository provides tools to extract, process, and format files used in bibliometric analyses in an automated manner. Typically, metadata acquisition happens through portals like PubMed or APIs, which require a certain level of programming knowledge. Additionally, converting metadata between various formats and structures tailored to specific bibliometric software is often a laborious task, limited to file-specific formats.

To address these challenges, this project offers a tool that automates both the search for titles and/or DOIs of articles and the conversion of the results into formats required by software such as VosViewer, Bibliometrix, and Bibix. This entire process is conducted transparently and automated, leveraging search terms provided in an input file.

---


## **Directory Descriptions**

### `config/`

Contains project configuration files, such as `config.yaml`. This file stores important information like directory paths, file naming conventions, and other relevant processing configurations.

| Variable                   | Description                                                      | Example/Default Value                                     |
|----------------------------|------------------------------------------------------------------|-----------------------------------------------------------|
| **api_key**                | API key used to authenticate requests to the service.            | `09921aadccbafb8e5913ae1c99e2fafbe00a`                    |
| **api_email**              | Email associated with the API for identification.                | `leandrorodrigues.s@gmail.com`                            |
| **config.search_type**     | Type of search to perform. `1` for DOI-based search, `2` for term-based. | `1` (DOI search)                                           |
| **config.time_sleep**      | Delay (in seconds) between PubMed queries to avoid rate-limits.  | `0.1`                                                     |
| **config.file_save_periodically** | Frequency (in terms of number of iterations) to save intermediate results. | `10`                                      |
| **config.save_xml**        | Whether to save the raw XML responses (`true` or `false`).       | `true`                                                    |
| **config.search**          | A search parameter threshold or setting (context-dependent).     | `0.1`                                                     |
| **config.search_article_one** | Whether to limit the search to a single article per query (`true` or `false`). | `true`                              |
| **directories.output**     | Directory where processed output files are stored.              | `./data/processed`                                        |
| **directories.xml**        | Directory for saving downloaded XML files.                       | `./data/processed/xml`                                    |
| **directories.input**      | Directory where input files are located.                         | `./data/input`                                            |
| **directories.logs**       | Directory for saving log files.                                  | `./logs`                                                  |
| **directories.type_files** | Directory for converted file types.                              | `./data/processed/files_type`                             |
| **files.file_data_error**  | CSV file for recording encountered errors.                       | `error.csv`                                               |
| **files.file_data_input**  | The input CSV file to be processed.                              | `References_MJFF_15122024.csv`                            |
| **files.file_parsing_pubmed** | CSV file for storing extracted PubMed metadata.               | `./metadata/PubMed_Metadata.csv`                          |
| **files.file_parsing_bibliometrix** | CSV file for storing extracted Bibliometrix metadata.   | `./metadata/Bibliometrix_Metadata.csv`                    |
| **files.file_data_pubmed** | Text file formatted for PubMed software usage.                   | `./files_type/PubMed_format.txt`                          |
| **files.file_bibliometrix**| XLSX file formatted for Bibliometrix usage.                      | `./files_type/Bibliometrix_format.xlsx`                   |
| **files.file_vsviewer**    | RIS file formatted for VosViewer software.                       | `VosViewer.ris`                                           |
| **files.file_bibtex**      | BibTeX file containing references.                               | `bibtex.bib`                                              |
| **files.file_web_of_science** | TXT file formatted for Web of Science.                       | `web_of_science.txt`                                      |
| **logging.log_file**       | The path to the log file for execution details.                  | `./logs/execution.log`                                    |
| **logging.level**          | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).           | `INFO`                                                    |
| **logging.format**         | Format string for log messages.                                 | `%(asctime)s - %(levelname)s - %(message)s`               |
| **logging.date_format**    | Format string for timestamps in log messages.                    | `%Y-%m-%d %H:%M:%S`                                       |

---

### `data/`

Holds input and output files for processing:  

- **`/input/`**: Contains the input file with titles and DOIs for processing.  
- **`/processed/`**: Stores the files generated during processing:  
  - **`/processed/files_type`**: Files formatted for VosViewer and Bibliometrix.  
  - **`/processed/metadata`**: Metadata extracted from PubMed API responses for further mapping into different file formats.  
  - **`/processed/xml`**: Stores XML responses from the PubMed API if configured in `config.yaml`.  

---

### `logs/`

Contains execution logs. Use these logs to track execution status and debug errors. The main file is `execution.log`.

---

### `notebooks/`

Contains Jupyter notebooks for interactive analysis and documentation of workflows:  

1. **`0_sample_extract_term.ipynb`**: Queries PubMed API by DOI or title and generates a CSV file with parsed data.  
2. **`1_mapping.ipynb`**: Maps parsed metadata to formats required by bibliometric software.

---

### `scripts/`

Contains the core logic of the project:  

- **`mapping.py`**: Maps metadata into desired output formats.  
- **`ncbi.py`**: Integrates with the NCBI platform.  
- **`parsing.py`**: Parses XML responses to extract relevant information.  
- **`utils.py`**: Auxiliary functions to support other scripts.  

---

### Other Files  

- **`.gitignore`**: Defines ignored files/directories for Git.  
- **`README.md`**: Main project documentation (this file).  

---


## **How to Use**

### 1. Clone the Repository
  ```bash
  https://github.com/leandrorodriguess/PubMedMetaTools.git
  ```

### 2. Create a Virtual Environment
  #### Windows 
  ```bash
    python -m venv venv
  ```
  #### Linux/macOS:
  ```bash
    python3 -m venv venv
  ```

### 3. Activate the Virtual Environment
  #### Windows:
  ```bash
    .\venv\Scripts\activate
  ```
  #### Linux/macOS:
  ```bash
    source venv/bin/activate
  ```
### 4. Install dependencies from `requirements.txt`:  
   ```bash
   pip install -r requirements.txt
   ```


### Configuration Variables

The project configuration is defined in a YAML file. Below is an overview of the key variables and their purposes.
Make sure to update these descriptions and values as needed, and refer to the codebase or additional documentation for more details on the meaning and usage of each variable.

1. Update paths in `config/config.yaml`.  
2. Update the paths in `config/config.yaml` to match your local environment.
3. Ensure that the directories inside `data/` and `logs/` exist, or verify that they will be automatically created during execution.


### **Using the Notebooks**

- Open the `notebook` directory and run the scripts.

1) `notebook/0_sample_extract_term.ipynb`: This notebook accesses the PubMed API and performs a query using the article's DOI. If no reference is found, it attempts a query using the article title. After processing, it provides a CSV file containing the parsed data from the API/XML, mapping the information of interest.

2) `notebook/1_mapping.ipynb`: This notebook maps the extracted parsing data into the formats required by PubMed and Bibliometrix files.

---


## **Contributing**

1. Fork this repository.
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature
   
3. Submit a pull request describing your modifications.


---
## License

This project is licensed under the GNU General Public License version 2 (GPLv2) or later. Please see the LICENSE file for full details, including citation requirements.


## Support
If you encounter any issues or have questions, please open an issue on GitHub or contact us at leandrorodrigues.s@gmail.com


## Citation

Published Article:
SOUSA, Leandro Rodrigues da Silva; SILVA, Daniel Hilario da; RIBEIRO, Caio Tonus; SILVA, Alves Daiane, MILKEN, Pedro Henrique Bernardes Caetano; NASUTO, Slawomir J.; SWEENEY-REED, Catherine M.; ANDRADE, Adriano de Oliveira; PEREIRA, Adriano Alves. A bibliometric study on Parkinson's disease based on the open access data of the Michael J. Fox Foundation. In: XXIX BRAZILIAN CONGRESS OF BIOMEDICAL ENGINEERING, Ribeirão Preto, September 2-6, 2024. Proceedings IFMBE. Ribeirão Preto: SBEB, 2024. ISSN: 1433-9277 (digital); 1680-0737 (printed).
---


If you use this software in your research, please cite it as indicated below. This encourages us to continue sharing and improving our work:<hr />

- Leandro Rodrigues da Silva Souza, Daniel Hilário da Silva, Caio Tonus Ribeiro, Daiane Alves da Silva, Slawomir J. Nasuto, Catherine M. Sweeney-Reed, Adriano Alves Pereira, Adriano de Oliveira Andrade**  
* *  
Software Impacts, Elsevier BV, 2024, [pages], ISSN [issn], [volume], https://doi.org/[doi]

### BibTeX

```
@article{silvaBIB2024,
  author = {Leandro Rodrigues da Silva Souza and Daniel Hilário da Silva and Caio Tonus Ribeiro and Daiane Alves da Silva and Pedro Henrique Bernardes Caetano Milken, Slawomir J. Nasuto, Catherine M. Sweeney-Reed, Adriano Alves Pereira and Adriano de Oliveira Andrade},
  title = { },
  journal = {Software Impacts},
  pages = {}, 
  year = {2024},
  issn = {}, 
  volume = {}, 
  publisher = {Elsevier BV},
  doi = {},
  url = {},
  keywords = {Exploratory data analysis, }
}
```
## 
