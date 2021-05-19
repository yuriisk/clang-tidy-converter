# Clang-Tidy Converter

Python3 script to convert Clang-Tidy output to [Code Climate JSON](https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md#issue).

## Usage

`python3 -m clang_tidy_converter [-h] [-r PROJECT_ROOT] [-l]`

Reads Clang-Tidy output from `STDIN` and prints Code Climate JSON to `STDOUT`.

### Arguments

* `-h, --help` - show help message and exit.
* `-r PROJECT_ROOT, --project_root PROJECT_ROOT` - output file paths relative to `PROJECT_ROOT`. E.g. Clang-Tidy outputs '/home/user/projects/A/src/main.cpp' file path and `PROJECT_ROOT` is set to '/home/user/projects/A' then Code Climate JSON mentions the file as 'src/main.cpp'.
* `-l, --use_location_lines` - use _line-based_ locations instead of _position-based_ as defined in _Locations_ section of Code Climate specification.
* `-j, --as_json_array` - output as JSON array instead of ending each issue with \0.

## Example

GitLab code quality report is a JSON file that implements a subset of the Code Climate specification, so this script can be used to convert Clang-Tidy output to GitLab code quality report. The following command does it:

```bash
clang-tidy /path/to/my/project/file.cpp \
  | python3 -m clang_tidy_converter --project_root /path/to/my/project \
                                    --use_location_lines \
  > gl-code-quality-report.json
```
