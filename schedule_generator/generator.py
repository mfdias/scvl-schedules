#!/usr/bin/env python3

import argparse
import csv


class Schedule:
    class SingleGameInfo:
        def __init__(self):
            self.is_skills_clinic = False
            self.is_open_play = False
            court_name = ''
            self.team_1 = ''
            self.team_2 = ''
            self.ref_team = ''

    class SingleTimeSlotSchedule:
        def __init__(self):
            self.time_slot_title = ''
            self.time_slot_games = {}

    class SingleWeekSchedule:
        def __init__(self):
            self.is_tba = False
            self.time_slots = []
            self.time_slot_skeds = {}
            self.bye_week_teams = []

    def __init__(self):
        self.title = 'Unknown Season'
        self.num_rec_teams = 0
        self.num_int_teams = 0
        self.num_com_teams = 0
        self.num_pow_teams = 0
        self.num_pow_plus_teams = 0
        self.court_titles = []
        self.week_titles = []
        self.weekly_skeds = {}
        self.no_play_weeks = []
        self.bye_week_col_num = -1

    def update_team_counts(self, team_name):
        if team_name.startswith('REC'):
            team_number = int(team_name[3:])
            if team_number > self.num_rec_teams:
                self.num_rec_teams = team_number
        elif team_name.startswith('INT'):
            team_number = int(team_name[3:])
            if team_number > self.num_int_teams:
                self.num_int_teams = team_number
        elif team_name.startswith('COM'):
            team_number = int(team_name[3:])
            if team_number > self.num_com_teams:
                self.num_com_teams = team_number
        elif team_name.startswith('POW'):
            team_number = int(team_name[3:])
            if team_number > self.num_pow_teams:
                self.num_pow_teams = team_number
        elif team_name.startswith('P+'):
            team_number = int(team_name[2:])
            if team_number > self.num_pow_plus_teams:
                self.num_pow_plus_teams = team_number

    def parse_rows(self, csv_reader):
        curr_week = ''
        for row in csv_reader:
            if any(row): # ignore empty spacer rows
                if not row[0]: # this is a header row
                    if not row[1]: # This is a week title row
                        curr_week = row[2]
                        self.week_titles.append(curr_week)
                        self.weekly_skeds[curr_week] = self.SingleWeekSchedule()
                        # Find the column number for bye weeks (if not yet found)
                        if self.bye_week_col_num == -1:
                            for idx in range(len(row)):
                                if row[idx] == 'BYE':
                                    self.bye_week_col_num = idx + 1
                    elif row[1].startswith('SCVL'): # This is the overall title row (only one at the start)
                        self.title = row[1]
                        continue
                    elif row[1].startswith('Court'): # Row for list of courts (can appear multiple times)
                        self.court_titles = list(filter(None, row))
                    elif row[1].startswith('SCHEDULE'): # Row for weeks where schedule is still TBA (to be announced)
                        self.weekly_skeds[curr_week].is_tba = True
                    else: # This is a no-play week (or playoff week, but we treat both the same)
                        self.no_play_weeks.append({'title': row[1], 'prev_week': curr_week})
                else: # this is a time slot row
                    # Extract the schedule for this time slot on this week
                    time_slot_title = row[0]
                    time_slot_sked = self.SingleTimeSlotSchedule()
                    time_slot_sked.time_slot_title = time_slot_title
                    for court_idx in range(len(self.court_titles)):
                        game_info = self.SingleGameInfo()
                        game_info.court_name = self.court_titles[court_idx]
                        court_col_num = (court_idx * 3) + 2
                        # Check if this court is open play or skills clinic for this time slot
                        if row[court_col_num].startswith('SKILLS CLINIC'):
                            game_info.is_skills_clinic = True
                        elif row[court_col_num].startswith('OPEN PLAY'):
                            game_info.is_open_play = True
                        else:
                            opponents = row[court_col_num].split(' v ')
                            game_info.team_1 = opponents[0]
                            game_info.team_2 = opponents[1]
                            ref_str = row[court_col_num + 1]
                            game_info.ref_team = ref_str[5:]
                            # Use opponents from each game to determine total number of teams in each division
                            self.update_team_counts(opponents[0])
                            self.update_team_counts(opponents[1])
                        time_slot_sked.time_slot_games[game_info.court_name] = game_info
                    self.weekly_skeds[curr_week].time_slot_skeds[time_slot_title] = time_slot_sked
                    # check for any bye week teams in this row
                    if row[self.bye_week_col_num]:
                        bye_teams = [x.strip() for x in row[self.bye_week_col_num].split()]
                        self.weekly_skeds[curr_week].bye_week_teams.extend(bye_teams)

    def generate_html(self, filename):
        print('TITLE: ', self.title)
        print('Courts: ', self.court_titles)
        print('Weeks: ', self.week_titles)
        print('No play weeks: ', self.no_play_weeks)
        print('bye team col num: ', self.bye_week_col_num)
        print('Team Counts:')
        print('  REC: ', self.num_rec_teams)
        print('  INT: ', self.num_int_teams)
        print('  COM: ', self.num_com_teams)
        print('  POW: ', self.num_pow_teams)
        print('  P+: ', self.num_pow_plus_teams)
        print('=======================================')
        for wk, wk_sked in self.weekly_skeds.items():
            print(wk, ' | BYE TEAMS: ', wk_sked.bye_week_teams)
            for ts, ts_sked in wk_sked.time_slot_skeds.items():
                print(ts)
                for ct, game in ts_sked.time_slot_games.items():
                    if game.is_skills_clinic:
                        print(ct, ': SKILLS CLINIC')
                    elif game.is_open_play:
                        print(ct, ': OPEN PLAY')
                    else:
                        print(ct, ': ', game.team_1, ' vs ', game.team_2, ' | ref: ', game.ref_team)


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
