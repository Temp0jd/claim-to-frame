PYTHON ?= python3

.PHONY: test validate examples compile preflight qa release-check

test:
	$(PYTHON) -m pytest

examples:
	$(PYTHON) scripts/validate_examples.py

preflight:
	$(PYTHON) scripts/preflight_model.py examples/transformer/project.json --registry assets/model-registry.example.json

qa:
	$(PYTHON) scripts/qa_video.py examples/transformer/render/final.mp4 --project transformer-example \
		--storyboard examples/transformer/storyboard.json --captions examples/transformer/captions.srt --require-audio --out /tmp/qa.json

validate: examples preflight qa
	$(PYTHON) scripts/check_artifact.py --kind dir examples/transformer

compile:
	$(PYTHON) -m compileall -q scripts tests

release-check:
	$(PYTHON) scripts/check_release.py --strict
