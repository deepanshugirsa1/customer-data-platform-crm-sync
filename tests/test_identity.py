from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.transform import domain_from_email


def test_domain_from_email():
    assert domain_from_email("alex@acme.io") == "acme.io"
    assert domain_from_email(None) is None
