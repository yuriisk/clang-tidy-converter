from ..parser import ClangMessage

from collections import defaultdict
from datetime import date
import html
import re


NEWLINE = '\n';


class HTMLReportFormatter:
    def __init__(self):
        pass

    def format(self, messages, args):
        by_level = _group_messages(messages)

        title = "Static Analysis Results"
        if len(args.software_name) > 0:
            title = f"{args.software_name} - {title}"

        return f"""<html>
<head>
{_style()}
{_script()}
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>

<table>
<tbody>
<tr><th>Date:</th><td>{date.today()}</td></tr>
</tbody></table>

<h2>Bug Summary</h2>
<table>
<thead><tr><td>Diagnostic Name</td><td>Quantity</td><td>Display?</td></tr></thead>
<tbody>
{NEWLINE.join(_format_level_group(level, msgs) for level, msgs in by_level.items())}
</tbody>
</table>

<h2>Reports</h2>
<table style="table-layout:auto">
<thead><tr>
  <td>Bug Severity</td>
  <td>Diagnostic Name</td>
  <td>Bug Description</td>
  <td>File</td>
  <td class="Q">Line</td>
  <td class="Q">Column</td>
  <td class="Q">Notes</td>
</tr></thead>
<tbody>
{NEWLINE.join(_format_message(msg) for msg in messages)}
</tbody>
</table>

</body></html>
"""


def _group_messages(messages):
    groupped = _group_messages_by_level(messages)
    return {k: _group_messages_by_diagnostic_name(m) for k, m in groupped.items()}


def _group_messages_by_level(messages):
    groupped = defaultdict(list)
    for m in messages:
        groupped[m.level].append(m)
    return groupped


def _group_messages_by_diagnostic_name(messages):
    groupped = defaultdict(list)
    for m in messages:
        groupped[m.diagnostic_name].append(m)
    return groupped


def _format_level_group(level, messages):
    return f"""<tr>
    <th class="SUMM_DESC">{_level_name(level)}</th>
    <th class="Q">{sum(len(msgs) for msgs in messages.values())}</th>
    <th><center><input type="checkbox" class="{_mangle_group(level, '')}" onclick="CopyCheckedStateToCheckButtons(this);" checked=""></center></th>
</tr>
{NEWLINE.join(_format_diagnostic_group(level, name, msgs) for name, msgs in messages.items())}"""


def _level_name(level):
    if level == ClangMessage.Level.NOTE:
        return "Note"
    elif level == ClangMessage.Level.REMARK:
        return "Remark"
    elif level == ClangMessage.Level.WARNING:
        return "Warning"
    elif level == ClangMessage.Level.ERROR:
        return "Error"
    elif level == ClangMessage.Level.FATAL:
        return "Fatal"
    else:
        return "Unknown"


def _format_diagnostic_group(level, diagnostic_name, messages):
    return f"""<tr>
    <td class="SUMM_DESC">{diagnostic_name}</td>
    <td class="Q">{len(messages)}</td>
    <td><center><input type="checkbox" class="{_mangle_group(level, diagnostic_name)}" onclick="ToggleDisplay(this); CopyCheckedStateFromCheckButtons('{_mangle_group(level, '')}');" checked=""></center></td>
</tr>"""


def _mangle_group(level, diagnostic_name):
    diagnostic_name = re.sub(r"[,.;@#?!&$]+\ *", " ", diagnostic_name)
    diagnostic_name = re.sub(r"\s+", "_", diagnostic_name)
    return f'bt_{_level_name(level)}_{diagnostic_name}'.lower()


def _format_message(message):
    return f"""<tr class="{_mangle_group(message.level, message.diagnostic_name)}">
    <td class="DESC">{_level_name(message.level)}</td>
    <td class="DESC">{message.diagnostic_name}</td>
    <td>{html.escape(message.message, quote=True)}</td><td class="SMASH">{message.filepath}</td>
    <td class="Q">{message.line}</td><td class="Q">{message.column}</td>
    <td></td>
</tr>"""


def _style():
    return """<style>
body { color:#000000; background-color:#ffffff }
body { font-family: Helvetica, sans-serif; font-size:9pt }
h1 { font-size: 14pt; }
h2 { font-size: 12pt; }
table { font-size: 9pt }
table { border-spacing: 0px; border: 1px solid black }
th, table thead {
  background-color: #eee; color: #666666;
  cursor: default;
  text-align: center;
  font-weight: bold; font-family: Verdana;
  white-space: nowrap;
}
.W { font-size: 0px }
th, td { padding: 5px; padding-left: 8px; text-align: left }
td.SUMM_DESC { padding-left: 12px }
td.DESC { white-space: pre }
td.SMASH { min-width: 30ch; overflow-wrap: anywhere }
th.Q, td.Q { text-align: right }
td { text-align: left }
tbody.scrollContent { overflow: auto }

/* Tooltip container */
.tooltip {
    position: relative;
    display: inline-block;
    color: #f00;
}

/* Tooltip text */
.tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: black;
    color: #fff;
    text-align: center;
    padding: 5px 0;
    border-radius: 6px;

    /* Position the tooltip text - see examples below! */
    position: absolute;
    z-index: 1;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
    visibility: visible;
}
</style>"""


def _script():
    return """<script language="javascript" type="text/javascript">
function SetDisplay(rowClass, displayVal)
{
  var rows = document.getElementsByTagName("tr");
  for (var i = 0 ; i < rows.length; ++i) {
    if (rows[i].className == rowClass) {
      rows[i].style.display = displayVal;
    }
  }
}

function CopyCheckedStateToCheckButtons(summaryCheckButton) {
  var inputs = document.getElementsByTagName("input");
  for (var i = 0 ; i < inputs.length; ++i) {
    if (inputs[i].type == "checkbox" &&
        inputs[i] != summaryCheckButton &&
        inputs[i].className.startsWith(summaryCheckButton.className)) {
      inputs[i].checked = summaryCheckButton.checked;
      ToggleDisplay(inputs[i]);
    }
  }
}

function CopyCheckedStateFromCheckButtons(summaryButtonClass) {
  var inputs = document.getElementsByTagName("input");
  var numOfButtons = 0;
  var numOfCheckedButtons = 0;
  var summaryButton = undefined;
  for (var i = 0 ; i < inputs.length; ++i) {
    if (inputs[i].type == "checkbox") {
      if (inputs[i].className == summaryButtonClass) {
        summaryButton = inputs[i];
      } else if (inputs[i].className.startsWith(summaryButtonClass)) {
        ++numOfButtons;
        if (inputs[i].checked) {
          ++numOfCheckedButtons;
        }
      }
    }
  }

  if (summaryButton) {
    if (numOfButtons == numOfCheckedButtons) {
      summaryButton.indeterminate = false;
      summaryButton.checked = true;
    } else if (numOfCheckedButtons == 0) {
      summaryButton.indeterminate = false;
      summaryButton.checked = false;
    } else {
      summaryButton.indeterminate = true;
    }
  }
}

function GetObjById( id ) {
    if (document.getElementById) {
        return document.getElementById(id);
    } else if (document.all) {
        return document.all[id];
    } else if (document.layers) {
        return document.layers[id];
    }
    return undefined;
}

function ToggleDisplay(checkButton) {
  if (checkButton.checked) {
    SetDisplay(checkButton.className, "");
  }
  else {
    SetDisplay(checkButton.className, "none");
  }
}
</script>"""
