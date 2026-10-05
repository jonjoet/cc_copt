"""Real browser uploads/downloads and optimization; optional dependencies."""
import csv
from pathlib import Path
import subprocess
import time
import urllib.request

import pytest
import yaml

pytest.importorskip("streamlit")
pw = pytest.importorskip("playwright.sync_api")
from conftest import APP_ROOT, SERVER_ARGV, artifact_index

@pytest.fixture
def browser_page(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    log = (artifacts / "server.log").open("w")
    server = subprocess.Popen(SERVER_ARGV, cwd=APP_ROOT, stdout=log, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic() + 40
        while True:
            try:
                with urllib.request.urlopen("http://127.0.0.1:8501/_stcore/health", timeout=1) as r:
                    assert r.status == 200
                break
            except Exception:
                if server.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("Streamlit server failed; see artifacts/server.log")
                time.sleep(0.2)
        with pw.sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(accept_downloads=True)
            page.goto("http://127.0.0.1:8501")
            pw.expect(page.get_by_role("heading", name="2. Settings")).to_be_visible(timeout=30000)
            wait_idle(page)
            yield page, artifacts
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        log.close()
        artifact_index(artifacts)


def wait_idle(page):
    pw.expect(page.locator('[data-testid="stApp"]')).to_have_attribute("data-test-script-state", "notRunning", timeout=30000)


def edit_text(page, label, value):
    field = page.get_by_role("textbox", name=label, exact=True)
    field.fill(value)
    field.press("Enter")
    # Wait until this committed edit has finished its script run.
    page.wait_for_timeout(350)
    wait_idle(page)


def download(page, label, path):
    with page.expect_download() as item:
        page.get_by_role("button", name=label, exact=True).click()
    item.value.save_as(path)
    return Path(path)


def test_latest_yaml_download(browser_page):
    page, artifacts = browser_page
    edit_text(page, "Species", "12345")
    saved = download(page, "Download Config as YAML", artifacts / "latest.yaml")
    assert yaml.safe_load(saved.read_text())["species"] == "12345"


def upload(page, label, path):
    page.get_by_role("region", name=label, exact=True).locator('input[type="file"]').set_input_files(str(path))
    page.wait_for_timeout(350)
    wait_idle(page)


def apply(page, path):
    upload(page, "Upload a YAML config file", path)
    page.get_by_role("button", name="Apply Config", exact=True).click()
    page.wait_for_timeout(350)
    wait_idle(page)


def test_import_edit_reapply_cli_and_gui_optimization(browser_page, synthetic):
    from test_cli import run_cli, check_outputs
    page, artifacts = browser_page
    edit_text(page, "Species", "12345")
    cfg = yaml.safe_load((synthetic / "config.yaml").read_text())
    cfg["constraints"].append(dict(type="AvoidPattern", pattern="BsaI_site"))
    first = artifacts / "first.yaml"
    first.write_text(yaml.safe_dump(cfg))
    apply(page, first)
    pw.expect(page.get_by_role("textbox", name="Species", exact=True)).to_have_value(cfg["species"])
    pw.expect(page.get_by_role("textbox", name="Start codon", exact=True)).to_have_value("")
    edit_text(page, "Pattern", "EcoRI_site")
    iters = page.get_by_role("spinbutton", name="Max random iters", exact=True)
    iters.fill("10000")
    iters.press("Enter")
    page.wait_for_timeout(350)
    wait_idle(page)
    edited = download(page, "Download Config as YAML", artifacts / "edited.yaml")
    data = yaml.safe_load(edited.read_text())
    assert data["max_random_iters"] == 10000
    assert data["constraints"][1]["pattern"] == "EcoRI_site"
    second_cfg = dict(cfg, input_type="protein", stop_codon="TGA", max_random_iters=12000)
    second = artifacts / "second.yaml"
    second.write_text(yaml.safe_dump(second_cfg))
    apply(page, second)
    pw.expect(page.get_by_role("textbox", name="Pattern", exact=True)).to_have_value("BsaI_site")
    pw.expect(iters).to_have_value("12000")
    current = download(page, "Download Config as YAML", artifacts / "current.yaml")
    current_data = yaml.safe_load(current.read_text())
    assert current_data["stop_codon"] == "TGA" and current_data["input_type"] == "protein"
    unsupported = artifacts / "unsupported.yaml"
    unsupported.write_text(yaml.safe_dump(dict(second_cfg, species="unapplied", objectives=[dict(type="MaximizeCAI")])))
    apply(page, unsupported)
    pw.expect(page.get_by_text("Nothing was applied.", exact=False)).to_be_visible()
    rejected = download(page, "Download Config as YAML", artifacts / "after-rejection.yaml")
    assert yaml.safe_load(rejected.read_text()) == current_data
    invalid = artifacts / "invalid.yaml"
    invalid.write_text("constraints: [")
    apply(page, invalid)
    pw.expect(page.get_by_text("Could not read this YAML configuration. Nothing was applied.", exact=True)).to_be_visible()
    assert yaml.safe_load(download(page, "Download Config as YAML", artifacts / "after-invalid.yaml").read_text()) == current_data
    # Fresh session proves the actual served download is importable.
    context = page.context.browser.new_context(accept_downloads=True)
    try:
        fresh = context.new_page()
        fresh.goto("http://127.0.0.1:8501")
        pw.expect(fresh.get_by_role("heading", name="2. Settings")).to_be_visible(timeout=30000)
        wait_idle(fresh)
        apply(fresh, current)
        pw.expect(fresh.get_by_role("textbox", name="Species", exact=True)).to_have_value(cfg["species"])
        pw.expect(fresh.get_by_role("textbox", name="Pattern", exact=True)).to_have_value("BsaI_site")
        assert yaml.safe_load(download(fresh, "Download Config as YAML", artifacts / "fresh.yaml").read_text()) == current_data
    finally:
        context.close()
    fasta, summary = run_cli(synthetic, synthetic / "protein.faa", current, prefix="download-cli")
    check_outputs(synthetic / "protein.faa", fasta, summary)
    upload(page, "Upload a sequence file", synthetic / "protein.faa")
    page.get_by_role("button", name="Run Optimization", exact=True).click()
    pw.expect(page.get_by_text("3 sequence(s) optimized successfully.", exact=True)).to_be_visible(timeout=90000)
    wait_idle(page)
    pw.expect(page.get_by_text("synthetic_1 — PASS", exact=True)).to_be_visible()
    page.get_by_text("synthetic_1 — PASS", exact=True).click()
    pw.expect(page.get_by_role("heading", name="Objectives", exact=True)).to_be_visible()
    assert page.locator('[data-testid="stException"]').count() == 0
    gui_fasta = download(page, "Download Optimized FASTA", artifacts / "optimized.fna")
    gui_summary = download(page, "Download Summary TSV", artifacts / "summary.tsv")
    check_outputs(synthetic / "protein.faa", gui_fasta, gui_summary)
    with gui_summary.open() as f:
        first_row = next(csv.DictReader(f, delimiter="\t"))
    # Match the visible first result to the values in its actual served TSV.
    for column, value in first_row.items():
        if column.startswith("constraint:"):
            label = column.removeprefix("constraint:")
            display_name = label.split("[", 1)[0].split("(", 1)[0]
            pw.expect(page.get_by_text(f"✅ {display_name}", exact=False).first).to_be_visible()
        elif column.startswith("objective:"):
            label = column.removeprefix("objective:")
            pw.expect(page.get_by_text(f"{label}: {float(value):.4f}", exact=True).first).to_be_visible()


def test_missing_species_table_is_safe(browser_page, synthetic):
    page, artifacts = browser_page
    cfg = yaml.safe_load((synthetic / "config.yaml").read_text())
    cfg["species"] = str(artifacts / "missing.json")
    path = artifacts / "missing-table.yaml"
    path.write_text(yaml.safe_dump(cfg))
    apply(page, path)
    upload(page, "Upload a sequence file", synthetic / "protein.faa")
    page.get_by_role("button", name="Run Optimization", exact=True).click()
    pw.expect(page.get_by_text("Could not load the species or codon table.", exact=False)).to_be_visible(timeout=30000)
    wait_idle(page)
    assert page.locator('[data-testid="stException"]').count() == 0
