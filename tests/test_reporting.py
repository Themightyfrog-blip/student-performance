"""Tests for Comprehensive Academic PDF and HTML Report Generation."""
import pytest
from database.warehouse import DataWarehouse
from src.etl import AcademicETLPipeline
from src.data_generator import AcademicDataGenerator
from src.reporting import ProjectReportGenerator


@pytest.fixture
def populated_report_generator(tmp_path):
    db_file = tmp_path / "test_report_wh.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)

    gen = AcademicDataGenerator(seed=42)
    sample_data = gen.generate_dataset(num_students=25)
    pipeline = AcademicETLPipeline(wh)
    pipeline.run(sample_data["combined"])

    return ProjectReportGenerator(wh)


def test_generate_pdf_report_valid_pdf_stream(populated_report_generator):
    pdf_bytes = populated_report_generator.generate_pdf_report(anonymize=False)
    
    # Must be non-empty bytes
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    # Standard PDF magic header check
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_pdf_report_with_anonymization(populated_report_generator):
    pdf_bytes_anon = populated_report_generator.generate_pdf_report(anonymize=True)
    assert isinstance(pdf_bytes_anon, bytes)
    assert len(pdf_bytes_anon) > 2000
    assert pdf_bytes_anon.startswith(b"%PDF")


def test_generate_html_report_contains_all_sections(populated_report_generator):
    html = populated_report_generator.generate_html_summary_report()
    assert "<html" in html.lower()
    assert "Star Schema" in html or "Storage Summary" in html
    assert "Questions 61" in html
    assert "PBL Evaluation" in html
