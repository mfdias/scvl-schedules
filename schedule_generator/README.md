# SCVL Schedule Generator

This folder contains a python script (and supporting files) that can be used to generate a new
HTML filterabl schedule by parsing the downloaded CSV version of a schedule in google sheets.
The generated HTML filterable schedule is a single HTML file called "generated_schedule.html",
which contains everything needed (CSS, HTML and Javascript) in a single file. This file can
be hosted as a static webpage on any web hosting service (e.g. GitHub Pages).

# How to run the script (on Windows)

- First you'll need to install python for windows (https://docs.python.org/3/using/windows.html)
- Next you'll need to download the google sheet version of the scheudle in CSV format
NOTE: An example csv can be found in the "sample_csvs" folder
- Clone a copy of this repo locally (e.g. using GitHub Desktop)
- Open a terminal window (recommend using PowerShell) and navigate to the "schedule_generator" folder
- Run the script on the command line, specifying the csv file as a parameter. Here is an example:
```
PS C:\Users\mfdias> cd .\Documents\GitHub\scvl-schedules\schedule_generator\
PS C:\Users\mfdias\Documents\GitHub\scvl-schedules\schedule_generator> py.exe .\generator.py '.\sample_csvs\Live Postings - Fall 2021 Season Schedule.csv'
```

The script will create (or overwrite if exists) a file called "generated_schedule.html". You can
load this file in a browser locally to view the result and if it looks good you can upload it to
your web hosting folder!

# Other notes

- This script has only been tested in windows but it should work on linux too.
- Currently has only been tested using a downloaded CSV of the fall 2021 schedule. May need further adjustments if the schedule format changes.
- Feel free to copy/modify/use this code as you wish (no licensing or usage restrictions apply).