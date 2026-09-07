import pytest
from parser import parse_file

def test_unsupported_format():
    with pytest.raises(ValueError) as excinfo:
        parse_file(b"some dummy bytes", "resume.txt")
    assert "Unsupported file format" in str(excinfo.value)

def test_empty_file():
    with pytest.raises(ValueError) as excinfo:
        parse_file(b"", "resume.pdf")
    assert "file is empty" in str(excinfo.value)

def test_oversized_file():
    oversized_content = b"a" * (5 * 1024 * 1024 + 1)
    with pytest.raises(ValueError) as excinfo:
        parse_file(oversized_content, "resume.pdf")
    assert "exceeds the maximum limit" in str(excinfo.value)
