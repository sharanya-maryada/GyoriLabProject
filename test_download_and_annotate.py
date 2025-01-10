import pytest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from download_and_annotate import (
    fetch_pubmed_xml,
    extract_abstract_text,
    annotate_text_with_gilda,
    save_annotations_as_json
)


@pytest.fixture
def sample_pubmed_xml():
    """A sample PubMed XML with a single article containing an abstract."""
    return """<PubmedArticleSet>
                <PubmedArticle>
                    <MedlineCitation>
                        <Article>
                            <Abstract>
                                <AbstractText>This is a test abstract.</AbstractText>
                            </Abstract>
                        </Article>
                    </MedlineCitation>
                </PubmedArticle>
            </PubmedArticleSet>"""


def test_extract_abstract_text(sample_pubmed_xml):
    abstract = extract_abstract_text(sample_pubmed_xml)
    assert abstract == "This is a test abstract."


@patch('requests.get')
def test_fetch_pubmed_xml(mock_get):
    # Mock the response
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<xml>Some PubMed XML</xml>"

    pmid = "12345"
    xml_content = fetch_pubmed_xml(pmid)
    assert "<xml>Some PubMed XML</xml>" in xml_content


@patch('requests.post')
def test_annotate_text_with_gilda(mock_post):
    # Mock the response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = [{"entity": "TestEntity"}]

    text = "Test text"
    annotations = annotate_text_with_gilda(text)
    assert annotations == [{"entity": "TestEntity"}]


def test_save_annotations_as_json(tmp_path):
    annotations = [{"entity": "TestEntity"}]
    output_file = tmp_path / "test.json"

    save_annotations_as_json(annotations, str(output_file))

    with open(output_file, "r") as f:
        data = f.read()
    assert '"entity": "TestEntity"' in data
