#!/usr/bin/env python3

import argparse
import csv


class Schedule:
    def __init__(self):
        self.title = 'Unknown Season'
        self.num_rec_teams = 0
        self.num_int_teams = 0
        self.num_com_teams = 0
        self.num_pow_teams = 0
        self.num_pow_plus_teams = 0
        self.court_titles = []

    def parse_rows(csv_reader):
        for row in csv_reader:
            if any(row): # ignore empty spacer rows
                if not row[0]: # this is a header row
                    if not row[1]:
                        
                    elif row[1].startswith('SCVL'):
                        # Only one title row at the start
                        self.title = row[1]
                        continue
                    elif row[1].startswith('Court'):
                        # Row for list of courts, can appear multiple times
                        self.court_titles = list(filter(None, row))
                else: # this is a time slot row
                    print(', '.join(row))

    def generate_html(filename):
        pass


def main():
    # Get the input csv filename from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    # Create a schedule object to use for reading the input csv and generating the schedule html
    sked = Schedule()

    # Open the file and collect info about the schedule to be generated
    with open(args.filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        sked.parse_rows(csv_reader)

    # Generate the filterable html schedule
    html_filename = 'index.html'
    sked.generate_html(html_filename)


if __name__ == "__main__":
    main()
