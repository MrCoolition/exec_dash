from app.integrations.ado.endpoints import base_url, normalize_organization


def test_normalize_organization_from_plain_name():
    assert normalize_organization("cgna-stg") == "cgna-stg"


def test_normalize_organization_from_visualstudio_url():
    assert normalize_organization("https://cgna-stg.visualstudio.com/") == "cgna-stg"


def test_normalize_organization_from_dev_azure_url():
    assert normalize_organization("https://dev.azure.com/cgna-stg") == "cgna-stg"


def test_normalize_organization_from_double_prefixed_dev_azure_url():
    value = "https://dev.azure.com/https://cgna-stg.visualstudio.com/"
    assert normalize_organization(value) == "cgna-stg"


def test_base_url_uses_normalized_organization():
    value = "https://cgna-stg.visualstudio.com/"
    assert base_url(value) == "https://dev.azure.com/cgna-stg"
