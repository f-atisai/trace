# TRACE Reviewer Examples

These examples show how a reviewer can read TRACE as execution evidence rather than as an API demonstration.

They correspond to the executable examples under [`../../examples/`](../../examples/). The current examples use small synthetic datasets for convenience. They are temporary scaffolding: a later revision should replace them with publicly available open-source clinical or statistical datasets and regenerate the logs from those programs.

The log excerpts below are representative rather than canonical golden files. Program-level provenance is shown conceptually even where the current prototype does not yet emit it automatically.

## 1. Demographics table

Program: [`demographics_table.py`](../../examples/demographics_table.py)

```text
TRACE EXECUTION
Program:  T14_01
Run ID:   <run-id>
Started:  <UTC timestamp>
Ended:    <UTC timestamp>
Input:    analysis/adsl.parquet
Output:   example-output/demographics_table.csv

INFO [START] [T14_01] execution started
INFO [READ] [ADSL] loaded – source=analysis/adsl.parquet, N=12, Vars=6
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=12 → 10
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE, method=AGE < 65 vs AGE >= 65
INFO [AGGREGATE] [ADSL] summarized – by=TRT01A,SEX,AGEGR1, result=demographics_summary, method=distinct subjects
INFO [VALIDATE] [demographics_summary] expected treatment groups present – PASS, treatment_groups=2
INFO [OUTPUT] [T14_01] written – example-output/demographics_table.csv, format=csv
INFO [END] [T14_01] execution completed – <duration>
```

### What a reviewer can infer

The program used `ADSL`, restricted the analysis to `SAFFL == 'Y'`, derived the planned age grouping, summarized by treatment/sex/age group, confirmed that both expected treatment groups were represented, and wrote the table output.

The `12 → 10` transition makes population attrition visible. It does not establish that `SAFFL` itself was derived correctly; that still requires specification and source review.

---

## 2. Adverse-events table

Program: [`adverse_events_table.py`](../../examples/adverse_events_table.py)

```text
TRACE EXECUTION
Program:  T14_03
Run ID:   <run-id>
Input:    analysis/adsl.parquet
Input:    analysis/adae.parquet
Output:   example-output/adverse_events_table.csv

INFO [READ] [ADSL] loaded – source=analysis/adsl.parquet, N=8, Vars=3
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=8 → 7
INFO [READ] [ADAE] loaded – source=analysis/adae.parquet, N=12, Vars=4
INFO [FILTER] [ADAE] TRTEMFL == 'Y' applied – N=12 → 10
INFO [MERGE] [ADAE + ADSL] merged – on=USUBJID, how=inner, result=TEAE_SAFETY, left N=10, right N=7, result N=9, unmatched_subjects=1
INFO [AGGREGATE] [TEAE_SAFETY] summarized – by=TRT01A,AEBODSYS,AEDECOD, result=ae_summary, method=distinct subjects
INFO [VALIDATE] [ae_summary] expected treatment groups present – PASS, treatment_groups=2
INFO [OUTPUT] [T14_03] written – example-output/adverse_events_table.csv, format=csv
```

### What a reviewer can infer

The program selected the Safety Population and treatment-emergent AEs before combining them. The important diagnostic is the merge contraction from **10 TEAE records to 9 analysis records**, with one unmatched participant.

That does not automatically indicate an error. It tells the reviewer exactly where to reconcile population membership and intended merge cardinality with the program and analysis specification.

---

## 3. Subject listing

Program: [`subject_listing.py`](../../examples/subject_listing.py)

```text
TRACE EXECUTION
Program:  L16_01
Run ID:   <run-id>
Input:    analysis/adsl.parquet
Output:   example-output/subject_listing.csv

INFO [READ] [ADSL] loaded – source=analysis/adsl.parquet, N=6, Vars=6
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=6 → 5
INFO [SORT] [Safety Population] sorted – by=TRT01A,USUBJID
INFO [TRANSFORM] [Safety Population] reporting columns selected – result=subject_listing
INFO [OUTPUT] [L16_01] written – example-output/subject_listing.csv, format=csv, N=5
```

### What a reviewer can infer

The listing was restricted to five Safety Population participants, ordered by treatment and participant ID, reduced to the intended reporting columns, and written as the listing output.

TRACE does not attempt to log every presentation-formatting statement. The reviewer receives the material analytical and reporting transitions without line-by-line noise.

---

## 4. Kaplan-Meier figure

Program: [`kaplan_meier_figure.py`](../../examples/kaplan_meier_figure.py)

```text
TRACE EXECUTION
Program:  F14_01
Run ID:   <run-id>
Input:    analysis/adtte.parquet
Output:   example-output/kaplan_meier_figure.png

INFO [READ] [ADTTE] loaded – source=analysis/adtte.parquet, N=12, Vars=6
INFO [FILTER] [ADTTE] PARAMCD == 'OS' and ITTFL == 'Y' applied – N=12 → 11
INFO [SORT] [ADTTE] sorted – by=TRT01A,AVAL
INFO [ANALYZE] [Overall Survival] analyzed – source=ADTTE, method=Kaplan-Meier, population=ITT, result=km_curve
INFO [VALIDATE] [km_curve] survival probabilities remain within [0, 1] – PASS
INFO [OUTPUT] [F14_01] written – example-output/kaplan_meier_figure.png, format=png
```

### What a reviewer can infer

The analysis used the OS parameter in the ITT Population, ordered the time-to-event records, executed a Kaplan-Meier analysis, checked a basic curve invariant, and generated the figure.

The log establishes that the recorded method was Kaplan-Meier and that the implemented bounds check passed. It does not establish that the estimator, censoring rules, endpoint derivation, or estimand are correct.

---

## 5. ADLB derivation

Program: [`adam_derivation.py`](../../examples/adam_derivation.py)

```text
TRACE EXECUTION
Program:  ADLB
Run ID:   <run-id>
Input:    analysis/adsl.parquet
Input:    source/adlb_input.parquet
Output:   example-output/adlb.csv

INFO [READ] [ADSL] loaded – source=analysis/adsl.parquet, N=5, Vars=4
INFO [READ] [ADLB_SOURCE] loaded – source=source/adlb_input.parquet, N=9, Vars=4
INFO [SORT] [ADLB_SOURCE] sorted – by=USUBJID,PARAMCD,ADT
INFO [FILTER] [ADLB_SOURCE] PARAMCD == 'ALT' applied – N=9 → 8
INFO [MERGE] [ADLB_SOURCE + ADSL] merged – on=USUBJID, how=left, result=ADLB_WORK, left N=8, right N=5, result N=8, unmatched_rows=0
INFO [DERIVE] [ADY] created – dataset=ADLB, source=ADT,TRTSDT
INFO [DERIVE] [ABLFL] created – dataset=ADLB, source=ADT,TRTSDT
INFO [DERIVE] [BASE] created – dataset=ADLB, source=AVAL,ABLFL
INFO [DERIVE] [CHG] created – dataset=ADLB, source=AVAL,BASE
INFO [VALIDATE] [ADLB] all records have subject-level treatment start date – PASS, missing_trtsdt_rows=0
INFO [VALIDATE] [ADLB] at most one baseline record per subject and parameter – PASS
INFO [OUTPUT] [ADLB] written – example-output/adlb.csv, format=csv, N=8
```

### What a reviewer can infer

The derivation path is visible from source laboratory records through parameter selection, subject-level enrichment, analysis day, baseline flagging, baseline value, and change from baseline.

The merge preserved the eight ALT records and produced no unmatched treatment-start dates. The validations make two important expectations explicit: treatment-date availability and uniqueness of the selected baseline record.

---

## 6. Independent QC comparison

Program: [`qc_comparison.py`](../../examples/qc_comparison.py)

```text
TRACE EXECUTION
Program:  QC_T14_01
Run ID:   <run-id>
Input:    outputs/T14_01.csv
Input:    qc/T14_01_qc.csv
Output:   example-output/qc_comparison.csv

INFO [READ] [T14_01_PRODUCTION] loaded – source=outputs/T14_01.csv, N=6, Vars=5
INFO [READ] [T14_01_QC] loaded – source=qc/T14_01_qc.csv, N=6, Vars=5
INFO [MERGE] [T14_01_PRODUCTION + T14_01_QC] merged – on=TRT01A,PARAM,STAT, how=outer, result=T14_01_COMPARISON, left N=6, right N=6, result N=6, unmatched_keys=0
INFO [VALIDATE] [T14_01] production and QC keys match – PASS, unmatched_keys=0
INFO [VALIDATE] [T14_01] production and QC statistics match – PASS, mismatched_rows=0
INFO [OUTPUT] [QC_T14_01] written – example-output/qc_comparison.csv, format=csv, N=6
```

### What a reviewer can infer

Production and independently programmed QC results were treated as separate inputs, aligned by reporting keys, and compared explicitly. No unmatched keys or statistic mismatches were recorded.

A `PASS` means these implemented comparisons passed. It does not establish correctness beyond the comparison criteria that were actually programmed.

---

## Reviewer pattern across all examples

Across the six programs, TRACE is most useful when the reviewer asks:

```text
What entered the analysis?
What population or records were selected?
Where did record counts change?
Did merges expand, contract, or preserve cardinality?
What important variables were derived?
What statistical method was executed?
Which expectations were explicitly validated?
What output was produced?
Does this execution path make sense against the code, specification, and result?
```

The examples intentionally avoid treating a clean log as proof of correctness. TRACE provides **reviewable execution evidence**; the reviewer still interprets that evidence in the context of the program and output.

## Planned follow-up

These examples should be revisited with real publicly available datasets. At that point:

1. replace the inline synthetic pandas data with public source datasets;
2. generate the TRACE logs from actual execution rather than maintaining representative excerpts manually;
3. add program-level provenance and hashes once the provenance implementation exists; and
4. use the resulting reviewer experience as input to the API-friction review.
