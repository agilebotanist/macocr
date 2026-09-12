"""Unit tests for macocr.ocr — Vision is mocked at the request/handler boundary."""

import pytest

from macocr import ocr as ocr_module


class _FakeCandidate:
    def __init__(self, text):
        self._text = text

    def string(self):
        return self._text


class _FakeTopCandidates:
    def __init__(self, candidate):
        self._candidate = candidate

    def firstObject(self):
        return self._candidate


class _FakeObservation:
    def __init__(self, text):
        self._text = text

    def topCandidates_(self, _n):
        return _FakeTopCandidates(_FakeCandidate(self._text))


class _NoCandidateObservation:
    def topCandidates_(self, _n):
        return _FakeTopCandidates(None)


class _FakeRequest:
    @classmethod
    def alloc(cls):
        return cls.__new__(cls)

    def init(self):
        self.languages = None
        self.level = None
        self._results = []
        return self

    def setRecognitionLanguages_(self, langs):
        self.languages = langs

    def setRecognitionLevel_(self, level):
        self.level = level

    def results(self):
        return self._results


def _make_fake_handler(success=True, texts=(), error="boom"):
    class _FakeHandler:
        @classmethod
        def alloc(cls):
            return cls.__new__(cls)

        def initWithURL_options_(self, url, _options):
            self.source = url
            return self

        def initWithData_options_(self, data, _options):
            self.source = data
            return self

        def performRequests_error_(self, requests, _err):
            if success:
                requests[0]._results = [_FakeObservation(t) for t in texts]
                return True, None
            return False, error

    return _FakeHandler


@pytest.fixture(autouse=True)
def fake_recognize_request(monkeypatch):
    monkeypatch.setattr(ocr_module.Vision, "VNRecognizeTextRequest", _FakeRequest)
    monkeypatch.setattr(ocr_module.Vision, "VNRequestTextRecognitionLevelAccurate", "accurate")


def test_run_vision_joins_top_candidates():
    handler = _make_fake_handler(texts=["Hello", "World"])()
    assert ocr_module._run_vision(handler) == "Hello\nWorld"


def test_run_vision_skips_missing_candidates():
    handler = _make_fake_handler()()

    def perform(requests, _err):
        requests[0]._results = [_NoCandidateObservation()]
        return True, None

    handler.performRequests_error_ = perform
    assert ocr_module._run_vision(handler) == ""


def test_run_vision_raises_on_failure():
    handler = _make_fake_handler(success=False, error="broke")()
    with pytest.raises(RuntimeError, match="broke"):
        ocr_module._run_vision(handler)


def test_ocr_image_builds_handler_from_url(monkeypatch):
    captured = {}

    class _FakeHandlerCls:
        @classmethod
        def alloc(cls):
            return cls.__new__(cls)

        def initWithURL_options_(self, url, _options):
            captured["url"] = url
            return self

        def performRequests_error_(self, requests, _err):
            requests[0]._results = [_FakeObservation("hi")]
            return True, None

    monkeypatch.setattr(ocr_module.Vision, "VNImageRequestHandler", _FakeHandlerCls)
    result = ocr_module.ocr_image("/tmp/example.png")
    assert result == "hi"
    assert captured["url"] is not None


def test_ocr_pdf_reports_pages_and_separators(tmp_path, monkeypatch, capsys):
    import fitz

    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    for text in ("Page One", "Page Two"):
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(str(pdf_path))
    doc.close()

    page_texts = iter(["Page One", "Page Two"])

    class _FakeHandlerCls:
        @classmethod
        def alloc(cls):
            return cls.__new__(cls)

        def initWithData_options_(self, data, _options):
            return self

        def performRequests_error_(self, requests, _err):
            requests[0]._results = [_FakeObservation(next(page_texts))]
            return True, None

    monkeypatch.setattr(ocr_module.Vision, "VNImageRequestHandler", _FakeHandlerCls)

    result = ocr_module.ocr_pdf(pdf_path)
    assert result == "<!-- Page 1 -->\nPage One\n\n---\n\n<!-- Page 2 -->\nPage Two"

    out = capsys.readouterr().out
    assert "page 1/2" in out
    assert "page 2/2" in out
