import sys
import argparse
import requests
import xml.etree.ElementTree as ET
import json
from pathlib import Path


def fetch_pubmed_xml(pmid: str) -> str:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text


def extract_abstract_text(pubmed_xml: str) -> str:
    root = ET.fromstring(pubmed_xml)

    # We will combine them into a single string.
    abstracts = []
    for article in root.findall(".//PubmedArticle"):
        abstract_texts = article.findall(".//AbstractText")
        if not abstract_texts:
            continue
        # Collect text from all AbstractText tags (they might be in separate paragraphs)
        for abs_node in abstract_texts:
            # AbstractText can sometimes have subtags or attributes,
            # so we use .text if it exists, or an empty string.
            if abs_node.text:
                abstracts.append(abs_node.text.strip())
    return "\n\n".join(abstracts)


def annotate_text_with_gilda(text: str, gilda_url: str = "https://grounding.indra.bio/annotate") -> dict:
    # Prepare JSON payload
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}

    # Send POST request
    response = requests.post(gilda_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def save_annotations_as_json(annotations: dict, output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2)


def print_annotation_stats(annotations: dict):
    entity_count = len(annotations)
    print(f"Number of entities extracted: {entity_count}")
    if not annotations:
        return

    # Gather the namespaces (e.g. CHEBI, NCBITaxon, MESH, HGNC, etc.)
    from collections import Counter
    namespaces = []
    for ann in annotations:
        if "term" in ann and "db" in ann["term"]:
            namespaces.append(ann["term"]["db"])
    namespace_counts = Counter(namespaces)

    print("Namespaces extracted (db):")
    for ns, count in namespace_counts.items():
        print(f"  {ns}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Download a PubMed abstract and annotate with Gilda.")
    parser.add_argument("pmid", help="PubMed ID of the article")
    args = parser.parse_args()

    pmid = args.pmid

    # 1. Fetch the PubMed article XML
    pubmed_xml = fetch_pubmed_xml(pmid)

    # 2. Extract the abstract text from the XML
    abstract_text = extract_abstract_text(pubmed_xml)
    if not abstract_text:
        print("No abstract found for this PMID.")
        sys.exit(0)

    # 3. Annotate the text using Gilda
    gilda_annotations = annotate_text_with_gilda(abstract_text)

    # 4. Save the result to <PMID>.json in output folder
    output_filename = f"output/{pmid}.json"
    save_annotations_as_json(gilda_annotations, output_filename)
    print(f"Annotations saved to {output_filename}")

    # 5. Optionally print stats 
    print_annotation_stats(gilda_annotations)


if __name__ == "__main__":
    main()


