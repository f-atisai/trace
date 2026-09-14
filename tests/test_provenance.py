import inspect

from trace_tlf import Trace


def test_constructor_signature_is_unchanged():
    parameters = inspect.signature(Trace).parameters

    assert list(parameters) == ["program", "study", "log_file", "level"]


def test_events_stream_before_context_exit(tmp_path, capsys):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt", rows=254)
        streamed = capsys.readouterr().err
        assert "INFO [START] [T14_01] execution started" in streamed
        assert "INFO [READ] [ADSL] loaded" in streamed
        assert not log_file.exists()


def test_final_log_places_provenance_before_events(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt", rows=254)
        trace.filter("ADSL", "SAFFL == 'Y'", before=254, after=249)
        trace.output("T14_01", "outputs/tlf_population.rtf")

    output = log_file.read_text(encoding="utf-8")

    assert output.startswith("TRACE EXECUTION\n\nProgram:  T14_01\n")
    assert f"Run ID:   {trace.run_id}" in output
    assert "Executed: " in output
    assert "Input artifacts:\n  data/adsl.xpt" in output
    assert "Output artifacts:\n  outputs/tlf_population.rtf" in output
    assert output.index("TRACE EXECUTION") < output.index("INFO [START]")
    assert output.index("INFO [START]") < output.index("INFO [READ]")
    assert output.index("INFO [READ]") < output.index("INFO [FILTER]")
    assert output.index("INFO [FILTER]") < output.index("INFO [OUTPUT]")
    assert output.index("INFO [OUTPUT]") < output.index("INFO [END]")


def test_artifact_paths_are_deduplicated_in_first_seen_order(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt")
        trace.read("ADSL_COPY", source="data/adsl.xpt")
        trace.read("ADAE", source="data/adae.xpt")
        trace.output("TABLE", "outputs/table.rtf")
        trace.output("TABLE_COPY", "outputs/table.rtf")

    output = log_file.read_text(encoding="utf-8")
    provenance = output.split("\n\nINFO [START]", maxsplit=1)[0]

    assert provenance.count("data/adsl.xpt") == 1
    assert provenance.count("outputs/table.rtf") == 1
    assert provenance.index("data/adsl.xpt") < provenance.index("data/adae.xpt")


def test_no_log_file_creates_no_persistent_provenance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with Trace("T14_01") as trace:
        trace.read("ADSL", source="data/adsl.xpt")

    assert list(tmp_path.iterdir()) == []


def test_event_rendering_is_unchanged_in_final_log(tmp_path, capsys):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.filter("ADSL", "SAFFL == 'Y'", before=10, after=8)

    streamed_lines = capsys.readouterr().err.strip().splitlines()
    final_lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    event_lines = [
        line
        for line in final_lines
        if line.startswith(("DEBUG ", "INFO ", "WARNING ", "ERROR ", "CRITICAL "))
    ]

    assert event_lines == streamed_lines
