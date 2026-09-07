import io
import zipfile

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


def test_fake_pdf_rejected():
    fake_pdf = b"This is not actually a PDF."

    with pytest.raises(ValueError) as excinfo:
        parse_file(fake_pdf, "resume.pdf")

    assert "not a valid PDF" in str(excinfo.value)


def test_fake_docx_rejected():
    fake_docx = b"This is not actually a DOCX file."

    with pytest.raises(ValueError) as excinfo:
        parse_file(fake_docx, "resume.docx")

    assert "not a valid DOCX" in str(excinfo.value)


def test_malformed_docx_rejected():
    malformed_docx = b"PK\x03\x04this is not a valid zip archive"

    with pytest.raises(ValueError) as excinfo:
        parse_file(malformed_docx, "resume.docx")

    assert "not a valid DOCX" in str(excinfo.value)


def test_invalid_docx_structure_rejected():
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("random.txt", "not a DOCX")

    with pytest.raises(ValueError) as excinfo:
        parse_file(buffer.getvalue(), "resume.docx")

    assert "not a valid DOCX" in str(excinfo.value)