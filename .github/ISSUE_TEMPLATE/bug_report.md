---
name: Bug report
about: Create a report to help us improve Metisara
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With configuration '...'
3. CSV file contains '...'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
What actually happened instead.

**Error messages/logs**
If applicable, paste any error messages or relevant log output:

```
Paste error messages here
```

**Environment (please complete the following information):**
 - OS: [e.g. macOS 13.0, Fedora 38]
 - Python version: [e.g. 3.9.1]
 - Metisara version: [e.g. 1.0.0]
 - JIRA version: [e.g. Cloud, Server 8.5]

**Configuration**
Please share your configuration (remove sensitive information):

**metisara.conf:**
```ini
[jira]
url = https://your-jira-instance.com/
username = user@example.com

[files]
csv_file_input = workspace/input/Metisara Template - Import.csv
csv_file_output = workspace/output/project-tickets-processed.csv

[project]
default_project = PROJ
```

**CSV structure:**
If the issue is related to CSV processing, please describe the structure or provide a sample (remove sensitive data).

**Additional context**
Add any other context about the problem here.

**Diagnostic information**
If possible, run `./metis --report-issue` and attach the generated zip file (⚠️ **remove all sensitive information first**).

**Screenshots**
If applicable, add screenshots to help explain your problem.