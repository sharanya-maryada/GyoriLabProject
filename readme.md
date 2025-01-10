# Download and Annotate PubMed Abstracts

This repository contains two main files:

1. **`download_and_annotate.py`**: A Python script that:
   - Fetches PubMed XML by a given PMID (PubMed ID)
   - Extracts the article’s abstract text
   - Sends it to the Gilda entity recognition web service
   - Saves the Gilda annotations into a JSON file
   - (Optionally) prints some statistics about the annotations

2. **`test_download_and_annotate.py`**: A Python unit test suite (using `pytest`) to validate core functionalities of the script.

---

## Contents

- [Overview](#overview)
- [Usage](#usage)
- [Functions in `download_and_annotate.py`](#functions-in-download_and_annotatepy)
- [Unit Tests](#unit-tests)
- [License](#license)

---

## Overview

`download_and_annotate.py` takes a PubMed ID (PMID) as input, downloads the XML record for that article, extracts the abstract text, sends it to [Gilda](https://grounding.indra.bio/apidocs) for named entity recognition, and saves the resulting annotations in a JSON file named `<PMID>.json` in the output folder. 

---

## Usage

### Command-Line

```bash
python download_and_annotate.py <PMID>
```

# Functions and Unit Tests

This document provides an overview of the main functions available in the `download_and_annotate.py` script and a brief explanation of the accompanying unit tests located in `test_download_and_annotate.py`.

---

## Functions in `download_and_annotate.py`

1. **`fetch_pubmed_xml(pmid: str) -> str`**  
   - **Purpose**:  
     Fetch the PubMed XML entry for a given PubMed ID (PMID) using the [NCBI EFetch API](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch).
   - **Parameters**:  
     - `pmid` (str): The PubMed ID of the article, such as `"28546431"`.
   - **Returns**:  
     - (str) The full XML response from PubMed as a string.
   - **Notes**:  
     - Uses `requests.get()` to retrieve the XML from PubMed.
     - Throws an exception if the response code is not successful (`200`).

2. **`extract_abstract_text(pubmed_xml: str) -> str`**  
   - **Purpose**:  
     Parse the PubMed XML and extract the article’s abstract text.
   - **Parameters**:  
     - `pubmed_xml` (str): The PubMed XML content as a string.
   - **Returns**:  
     - (str) The article’s abstract text, or an empty string if no abstract was found.
   - **Notes**:  
     - Some articles have multiple `<AbstractText>` tags. This function will gather them all and concatenate them with a newline separator.
     - Uses Python’s built-in `xml.etree.ElementTree` for parsing.

3. **`annotate_text_with_gilda(text: str, gilda_url: str = "https://grounding.indra.bio/annotate") -> dict`**  
   - **Purpose**:  
     Send text to the [Gilda](https://grounding.indra.bio/apidocs) named entity recognition service for annotation.
   - **Parameters**:  
     - `text` (str): The text to be annotated (usually the abstract from PubMed).
     - `gilda_url` (str, optional): The Gilda endpoint to send the request to. Defaults to `"https://grounding.indra.bio/annotate"`.
   - **Returns**:  
     - (dict) The JSON response from Gilda, parsed into a Python dictionary.
   - **Notes**:  
     - Uses `requests.post()` to send a JSON payload containing the text.
     - Throws an exception if the POST request fails.

4. **`save_annotations_as_json(annotations: dict, output_file: str)`**  
   - **Purpose**:  
     Save the Gilda annotations to a file in JSON format.
   - **Parameters**:  
     - `annotations` (dict): The dictionary containing annotation results from Gilda.
     - `output_file` (str): The file path where the JSON should be saved (e.g., `"28546431.json"`).
   - **Returns**:  
     - None. Writes data to the file system.

5. **`print_annotation_stats(annotations: dict)`**  
   - **Purpose**:  
     Print some basic statistics about the recognized entities in the Gilda annotations.
   - **Parameters**:  
     - `annotations` (dict): The dictionary containing the annotation results.
   - **Returns**:  
     - None. Prints to the console.
   - **Notes**:  
     - Displays the total number of entities recognized.
     - Optionally counts and shows how many times different namespaces/databases (like CHEBI, MESH, HGNC, etc.) appeared in the annotations.

6. **`main()`**  
   - **Purpose**:  
     Acts as the entry point for the command-line script, orchestrating the above functions in sequence.
   - **Process**:  
     1. Parses command-line arguments (`PMID`).  
     2. Fetches the PubMed XML from the EFetch API.  
     3. Extracts the abstract text from the XML.  
     4. Calls Gilda to annotate the abstract.  
     5. Saves the annotations to `<PMID>.json`.  
     6. Prints stats if `--print-stats` is used.

---

## Unit Tests in `test_download_and_annotate.py`

The unit tests are designed to validate the core functions of `download_and_annotate.py`. They rely on the `pytest` framework, which simplifies writing and running tests.

1. **`test_extract_abstract_text`**
   - Uses a sample PubMed XML fixture to ensure that `extract_abstract_text` correctly parses the abstract from XML.

2. **`test_fetch_pubmed_xml`**
   - Mocks the `requests.get` call to simulate retrieving PubMed XML data.  
   - Verifies that `fetch_pubmed_xml` handles and returns the correct XML content.

3. **`test_annotate_text_with_gilda`**
   - Mocks the `requests.post` call to simulate an external request to Gilda.  
   - Ensures that `annotate_text_with_gilda` returns the expected JSON structure.

4. **`test_save_annotations_as_json`**  
   - Creates a temporary file path using `pytest`’s `tmp_path` fixture.
   - Checks that `save_annotations_as_json` properly writes the annotation dictionary to disk in JSON format.

### How to Run the Tests

1. Install `pytest` if not already installed:
   ```bash
   pip install pytest
   ```
2. Run 
   ```bash
   pytest -v
