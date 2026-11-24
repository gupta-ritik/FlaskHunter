# Local CI history format

Run `flakehunter history <path>` with the path to a directory of local pytest JUnit reports.

```text
history/
  100-1/
    metadata.json
    results.xml
  100-2/
    metadata.json
    results.xml
    shard-2.xml
```

Name each attempt directory `<run_id>-<attempt>`. Put one or more `*.xml`
reports and a UTF-8 `metadata.json` directly inside it. For example:

```json
{
  "repo": "example/project",
  "head_sha": "a1b2c3d4",
  "workflow": "CI",
  "job": "unit",
  "env": {
    "python": "3.12.8",
    "os": "ubuntu-24.04"
  },
  "run_id": 100,
  "attempt": 1,
  "artifact_url": "https://example.test/runs/100/attempts/1"
}
```

`run_id` and `attempt` are positive integers and must agree with the directory
name. The other fields are nonempty strings except `env`, which holds the `python`
and `os` strings. Use consistent names and versions across comparable attempts
and use distinct `job` values for matrix variants that differ beyond Python and OS.
`artifact_url` is retained as the source reference. The command reads local files only.

The loader reconstructs pytest node IDs from JUnit `classname` and `name`,
including classes and parameter suffixes. Pytest's default JUnit format flattens
directories and classes into a dotted string, so the loader assumes class
names start with an uppercase letter when only `classname` is available. A
JUnit `file` attribute from `junit_family=xunit1` identifies the module path
explicitly. A `nodeid` testcase property, when present, supplies the exact ID.

A candidate has at least one passing and one failing attempt for the same node
ID, commit, repository, workflow, job, Python version, and OS. Each distinct
`(run_id, attempt)` counts once per test. Skips, errors, and attempts with
conflicting outcomes supply no pass or fail evidence. Signatures use the
exception type when available and the first line of the failure message.

Missing or invalid metadata, missing reports, and unreadable XML produce
warnings. The CLI prints the table and warnings and exits with status 0.
