# Resharper-CI

This action runs JetBrains Resharper InspectCode, prints human-readable output and writes it to `inspection.txt` as well as original output to `inspection.xml`

## Inputs

### `solution`

  **Required** Path to your solution file, e.g. MyProject.sln"

### `profile`

  Path to your `.DotSettings` file

### `severity`

  Set minimal reported severity level to [INFO, HINT, SUGGESTION, WARNING, ERROR]. Default to WARNING
  default: "WARNING"

### `include`

  Semicolon-separated list of relative paths or wildcards that define the files to include during the inspection

### `exclude`

  Semicolon-separated list of relative paths or wildcards that define the
  files to exclude during the inspection

### `discard-issues`

  Semicolon-separated list of IssueType Ids that will be ignored

### `build`

  Should project be builded before checks, defaults to true

### `hide-output`

  Hides output of build ('dotnet build') and resharper ('jb inspectcode ...'), defautls to true

## Example

```yaml
name: InspectMaster

on:
  push:
    branches: [ master ]

jobs:
  self-test:
   runs-on: ubuntu-latest
   name: Self Test
   steps:
     - name: Checkout
       uses: actions/checkout@v2
     - name: Inspect
       uses: florius0/resharper-ci
       with:
          solution: './MyProject.sln'
```

------
Inspired by <https://github.com/nbadal/inspectcode-action>
