.PHONY: all validate test provenance model workbook app paper pdf site template clean

PY   ?= python3
NODE ?= node
BUILD = build

# Deliverable filenames carry major.minor, read from the model so they can never
# drift from it. Hard-coding the version here is how the build broke before.
VER := $(shell $(PY) -c "import yaml;print('.'.join(yaml.safe_load(open('model/meta.yaml'))['model']['version'].split('.')[:2]))")

WORKBOOK = $(BUILD)/TID-CMM-Self-Assessment-v$(VER).xlsx
EXAMPLE  = $(BUILD)/TID-CMM-Worked-Example-v$(VER).xlsx
PAPER    = $(BUILD)/TID-CMM-White-Paper-v$(VER).docx
PAPERPDF = $(BUILD)/TID-CMM-White-Paper-v$(VER).pdf
APP      = $(BUILD)/tid-cmm-assessment.html

all: validate test model workbook app paper pdf site provenance
	@echo
	@echo "TID-CMM v$(VER) — all deliverables rebuilt in $(BUILD)/"

validate:
	$(PY) -m tidcmm validate

test:
	$(PY) -m pytest tests -q

provenance:
	$(PY) tools/check_provenance.py

model:
	@mkdir -p $(BUILD)
	$(PY) -m tidcmm export-json $(BUILD)/model.json
	$(PY) -m tidcmm score assessments/example-assessment.yaml -o $(BUILD)/example-report.json

workbook: model
	$(PY) tools/build_workbook.py $(WORKBOOK)
	$(PY) tools/fill_example.py

app: model
	$(PY) tools/build_app.py $(APP)
	@# A syntax error in the tool's inline script renders a blank page rather than
	@# erroring visibly, so the JavaScript is parsed as part of the build.
	@$(PY) -c "import pathlib;h=pathlib.Path('$(APP)').read_text();\
pathlib.Path('$(BUILD)/.app-check.js').write_text(h.split('<script>',1)[1].rsplit('</script>',1)[0])"
	@$(NODE) --check $(BUILD)/.app-check.js && rm -f $(BUILD)/.app-check.js && echo "  tool JavaScript parses"

paper: model
	$(NODE) tools/build_whitepaper.js $(PAPER)

pdf: paper
	@# Needs LibreOffice. Optional: the site builder omits the PDF download if absent.
	@command -v soffice >/dev/null 2>&1 \
		&& soffice --headless --convert-to pdf --outdir $(BUILD) $(PAPER) >/dev/null 2>&1 \
		&& echo "  $(PAPERPDF)" \
		|| echo "  soffice not found — skipping PDF (install LibreOffice to build it)"

site: app paper workbook
	$(PY) tools/build_site.py

template:
	$(PY) -m tidcmm template assessments/blank-assessment.yaml

clean:
	rm -f $(BUILD)/*.json $(BUILD)/*.xlsx $(BUILD)/*.html $(BUILD)/*.docx \
	      $(BUILD)/*.pdf $(BUILD)/*.zip $(BUILD)/.app-check.js
	rm -rf $(BUILD)/site
