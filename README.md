# Clang-Tidy Converter

Python3 script to convert Clang-Tidy output to different formats.
Supported formats are [Code Climate JSON](https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md#issue) and HTML report similar to `scan-build` utility.

## Usage

`python3 -m clang_tidy_converter [-h] [-r PROJECT_ROOT] FORMAT ...`

Reads Clang-Tidy output from `STDIN` and prints it in selected format to `STDOUT`.

### Arguments

Optional arguments:
* `-h, --help` - show help message and exit.
* `-r PROJECT_ROOT, --project_root PROJECT_ROOT` - output file paths relative to `PROJECT_ROOT`.

Output format:
* `cc` - Code Climate JSON.
* `html` - HTML report.

Optinal arguments for Code Climate format:
* `-h, --help` - show help message and exit.
* `-l, --use_location_lines` - use _line-based_ locations instead of _position-based_ as defined in _Locations_ section of Code Climate specification.
* `-j, --as_json_array` - output as JSON array instead of ending each issue with \0.

Optional arguments for HTML report format:
* `-h, --help` - show help message and exit.
* `-s SOFTWARE_NAME, --software_name SOFTWARE_NAME` - software name to display in generated report.

## Example

GitLab code quality report is a JSON file that implements a subset of the Code Climate specification, so this script can be used to convert Clang-Tidy output to GitLab code quality report. The following command does it:

```bash
clang-tidy /path/to/my/project/file.cpp \
  | python3 -m clang_tidy_converter --project_root /path/to/my/project \
                                    cc --use_location_lines --as_json_array \
  > gl-code-quality-report.json
```
