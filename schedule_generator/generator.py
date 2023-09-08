#!/usr/bin/env python3

import argparse
import csv


class Schedule:
    class SingleGameInfo:
        def __init__(self):
            self.is_skills_clinic = False
            self.skills_clinic_title = ''
            self.is_open_play = False
            self.open_play_title = ''
            self.court_name = ''
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

    def parse_rows(self, csv_reader, start_col, debug):
        curr_week = ''
        for row in csv_reader:
            if any(row): # ignore empty spacer rows
                if not row[start_col]: # this is a header row
                    if not row[start_col + 1]: # This is a week title row
                        curr_week = row[start_col + 2]
                        self.week_titles.append(curr_week)
                        self.weekly_skeds[curr_week] = self.SingleWeekSchedule()
                        # Find the column number for bye weeks (if not yet found)
                        if self.bye_week_col_num == -1:
                            for idx in range(len(row)):
                                if row[idx] == 'BYE':
                                    self.bye_week_col_num = idx + 1
                    elif row[start_col + 1].startswith('SCVL'): # This is the overall title row (only one at the start)
                        self.title = row[start_col + 1]
                        continue
                    elif row[start_col + 1].startswith('Court'): # Row for list of courts (can appear multiple times)
                        self.court_titles = list(filter(None, row))
                    elif row[start_col + 1].startswith('SCHEDULE'): # Row for weeks where schedule is still TBA (to be announced)
                        self.weekly_skeds[curr_week].is_tba = True
                    else: # This is a no-play week (or playoff week, but we treat both the same)
                        self.no_play_weeks.append({'title': row[start_col + 1], 'prev_week': curr_week})
                else: # this is a time slot row
                    # Extract the schedule for this time slot on this week
                    time_slot_title = row[start_col]
                    time_slot_sked = self.SingleTimeSlotSchedule()
                    time_slot_sked.time_slot_title = time_slot_title
                    if debug:
                        print(curr_week, ' ', time_slot_title)
                    for court_idx in range(len(self.court_titles)):
                        game_info = self.SingleGameInfo()
                        game_info.court_name = self.court_titles[court_idx]
                        court_col_num = (court_idx * 3) + start_col + 2
                        # Check if this court is open play or skills clinic for this time slot
                        if 'SKILLS CLINIC' in row[court_col_num]:
                            if debug:
                                print(self.court_titles[court_idx], ': ', row[court_col_num])
                            game_info.is_skills_clinic = True
                            game_info.skills_clinic_title = row[court_col_num]
                            if row[court_col_num + 1]:
                                game_info.skills_clinic_title += ' (' + row[court_col_num + 1] + ')'
                        elif 'OPEN PLAY' in row[court_col_num]:
                            if debug:
                                print(self.court_titles[court_idx], ': ', row[court_col_num])
                            game_info.is_open_play = True
                            game_info.open_play_title = row[court_col_num]
                            if row[court_col_num + 1]:
                                game_info.open_play_title += ' (' + row[court_col_num + 1] + ')'
                        else:
                            opponents = row[court_col_num].split(' v ')
                            if debug:
                                print(self.court_titles[court_idx], ': ', opponents)
                            game_info.team_1 = opponents[0].replace('*', '')
                            game_info.team_2 = opponents[1].replace('*', '')
                            ref_str = row[court_col_num + 1]
                            game_info.ref_team = ref_str[5:]
                            # Use opponents from each game to determine total number of teams in each division
                            self.update_team_counts(game_info.team_1)
                            self.update_team_counts(game_info.team_2)
                        time_slot_sked.time_slot_games[game_info.court_name] = game_info
                    self.weekly_skeds[curr_week].time_slots.append(time_slot_title)
                    self.weekly_skeds[curr_week].time_slot_skeds[time_slot_title] = time_slot_sked
                    # check for any bye week teams in this row
                    if row[self.bye_week_col_num]:
                        bye_teams = [x.strip() for x in row[self.bye_week_col_num].split()]
                        self.weekly_skeds[curr_week].bye_week_teams.extend(bye_teams)

    def add_spacer_row(self, outfile):
        outfile.write('  <tr class="spacer">\n')
        outfile.write('    <td colspan="26" class="spacer_row"><div style="height: 20px;"></div></td>\n')
        outfile.write('  </tr>\n\n')

    def write_court_headers(self, outfile):
        outfile.write('  <tr class="header">\n')
        outfile.write('    <th colspna="1" style="width:7%;"></th>\n')
        court_col_width_pct = 75 / len(self.court_titles)
        for court_title in self.court_titles:
            outfile.write('    <th colspan="5" style="width:' + str(court_col_width_pct) + '%;">' + court_title + '</th>\n')
        outfile.write('  </tr>\n\n')

    def get_team_division(self, team_name):
        if team_name.startswith('REC'):
            return 'rec'
        elif team_name.startswith('INT'):
            return 'int'
        elif team_name.startswith('COM'):
            return 'com'
        elif team_name.startswith('POW'):
            return 'pow'
        elif team_name.startswith('P+'):
            return 'pow_plus'
        else:
            return 'unknown'

    def add_no_play_week(self, outfile, no_play_week_title):
        outfile.write('  <tr class="week">\n')
        outfile.write('    <td colspan="26" class="no_play_week">' + no_play_week_title + '</td>\n')
        outfile.write('  </tr>\n\n')

    def generate_html(self, outfile):
        # write initial header lines
        outfile.write('<!DOCTYPE html>\n')
        outfile.write('<html>\n')
        outfile.write('<head>\n')
        outfile.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
        outfile.write('<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n')
        outfile.write('<style>\n')
        # Add styles from styles.css
        with open('style.css', 'r') as css_file:
            styles = css_file.read()
        outfile.write(styles + '\n')
        # write the remainder of the header lines
        outfile.write('</style>\n')
        outfile.write('</head>\n')

        # Next we start the html body
        outfile.write('<body>\n\n')

        # Start by writing the title
        outfile.write('<h2>' + self.title + '</h2>\n\n')

        # Next we create the drop down for team selection
        outfile.write('<p>Select a team to filter the schedule:&nbsp;&nbsp;\n')
        outfile.write('  <select id="firstTeamSelect" onchange="handleFirstTeamSelectChange()" autocomplete="off">\n')
        outfile.write('    <option selected value="SHOWALL"> -- ALL TEAMS -- </option>\n')
        for i in range(1, self.num_rec_teams + 1):
            outfile.write('    <option class="rec">REC' + str(i) + '</option>\n')
        for i in range(1, self.num_int_teams + 1):
            outfile.write('    <option class="int">INT' + str(i) + '</option>\n')
        for i in range(1, self.num_com_teams + 1):
            outfile.write('    <option class="com">COM' + str(i) + '</option>\n')
        for i in range(1, self.num_pow_teams + 1):
            outfile.write('    <option class="pow">POW' + str(i) + '</option>\n')
        for i in range(1, self.num_pow_plus_teams + 1):
            outfile.write('    <option class="pow_plus">P+' + str(i) + '</option>\n')
        outfile.write('  </select>\n')
        outfile.write('</p>\n')

        # Next we create the optional filters div
        outfile.write('<div class="optional_filters_div" id="optional_filters_div">\n')
        outfile.write('  <p class="optional_filters_hedaer">Optional Filters:</p>\n')
        outfile.write('  <div class="optional_filters_sub_div_left">\n')
        outfile.write('    <p>\n')
        outfile.write('      <label for="secondTeamSelect">Select Second Team:&nbsp;&nbsp;</label>\n')
        outfile.write('      <select id="secondTeamSelect" onchange="handleOptionalFiltersChange()" autocomplete="off" disabled>\n')
        outfile.write('	     </select>\n')
        outfile.write('    </p>\n')
        outfile.write('  </div>\n')
        outfile.write('  <div class="optional_filters_sub_div_right">\n')
        outfile.write('    <label for="showOpenPlay">Show <span class="open_play">OPEN PLAY</span> slots:&nbsp;&nbsp;</label>\n')
        outfile.write('    <input id="showOpenPlay" type="checkbox" onchange="handleOptionalFiltersChange()" disabled>\n')
        outfile.write('    <br /><br />\n')
        outfile.write('    <label for="showSkillsClinic">Show <span class="skills_clinic">SKILLS CLINIC</span> slots:&nbsp;&nbsp;</label>\n')
        outfile.write('    <input id="showSkillsClinic" type="checkbox" onchange="handleOptionalFiltersChange()" disabled>\n')
        outfile.write('  </div>\n')
        outfile.write('</div>\n')
        outfile.write('<br /><br />\n\n')

        # Next is the table for the actual schedule
        outfile.write('<table id="myTable">\n')
        # First table row is the court titles
        self.write_court_headers(outfile)
        self.add_spacer_row(outfile)

        # Now we can write the rows for each week in the schedule
        prev_week_title = ''
        for week_title in self.week_titles:
            # First check to see if we need to write one of the no-play week rows
            for npw in self.no_play_weeks:
                if npw['prev_week'] == prev_week_title:
                    self.add_no_play_week(outfile, npw['title'])
                    self.add_spacer_row(outfile)
            prev_week_title = week_title
            # Write the week title row
            week_sked = self.weekly_skeds[week_title]
            outfile.write('  <tr class="week">\n')
            outfile.write('    <td></td>\n')
            if week_sked.is_tba:
                outfile.write('    <td colspan="5" class="playoff_week">' + week_title + '</td>\n')
                outfile.write('	   <td colspan="20"></td>\n')
            else:
                outfile.write('    <td colspan="25" class="week_row">' + week_title + '</td>\n')
            outfile.write('  </tr>\n')
            # Write rows for each timeslot in this week's schedule
            if week_sked.is_tba:
                # First check if there is a "no-play-week" title for this TBA week and add that here
                for npw in self.no_play_weeks:
                    if npw['prev_week'] == week_title:
                        self.add_no_play_week(outfile, npw['title'])
                        self.add_spacer_row(outfile)
                        prev_week_title = ''  # reset prev week to avoid writing this twice
                self.write_court_headers(outfile)
                outfile.write('  <tr class="spacer">\n')
                outfile.write('    <td colspan="26" class="tba_row">SCHEDULE TO BE ANNOUNCED SOON</div></td>\n')
                outfile.write('  </tr>\n\n')
            else:
                for time_slot in week_sked.time_slots:
                    outfile.write('  <tr>\n')
                    outfile.write('    <td class="time">' + time_slot + '</td>\n\n')
                    ts_sked = week_sked.time_slot_skeds[time_slot]
                    for court in self.court_titles:
                        game = ts_sked.time_slot_games[court]
                        if game.is_skills_clinic:
                            outfile.write('    <td colspan="5" class="skills_clinic">' + game.skills_clinic_title + '</td>\n\n')
                        elif game.is_open_play:
                            outfile.write('    <td colspan="5" class="open_play">' + game.open_play_title + '</td>\n\n')
                        else:
                            team_div = self.get_team_division(game.team_1)
                            outfile.write('    <td class="team1 ' + team_div + '">' + game.team_1 + '</td>\n')
                            outfile.write('    <td class="vs ' + team_div + '">vs</td>\n')
                            outfile.write('    <td class="team2 ' + team_div + '">' + game.team_2 + '</td>\n')
                            outfile.write('    <td class="ref ' + team_div + '">ref:</td>\n')
                            outfile.write('    <td class="team_ref ' + team_div + '">' + game.ref_team + '</td>\n\n')
                # Add the row showing bye teams for this week (if there are any)
                if len(week_sked.bye_week_teams) > 0:
                    outfile.write('  <tr>\n')
                    outfile.write('    <td class="bye_week">Bye Week</td>\n')
                    for bye_team in week_sked.bye_week_teams:
                        team_div = self.get_team_division(bye_team)
                        outfile.write('    <td colspan="2" class="bye ' + team_div + '">' + bye_team + '</td>\n')
                    remaining_colspan = 25 - len(week_sked.bye_week_teams)
                    outfile.write('    <td colspan="' + str(remaining_colspan) + '" class="empty_row"></td>\n')
                    outfile.write('  </tr>\n\n')
                # Add a spacer row after each week
                if len(week_sked.time_slots) > 0:
                    self.add_spacer_row(outfile)

        # Check if there is one last no-play-week at the end
        for npw in self.no_play_weeks:
            if npw['prev_week'] == prev_week_title:
                self.add_no_play_week(outfile, npw['title'])
                self.add_spacer_row(outfile)

        # Finally we can close the table and add the scripts
        outfile.write('</table>\n')
        outfile.write('<br /><br /><br />\n\n')
        outfile.write('<script>\n')

        # We need to update the team counts before writing the script
        with open('filter_funcs.js', 'r') as js_file:
            js_lines = js_file.readlines()
        js_lines[2] = '    "REC": ' + str(self.num_rec_teams) + ',\n'
        js_lines[3] = '    "INT": ' + str(self.num_int_teams) + ',\n'
        js_lines[4] = '    "COM": ' + str(self.num_com_teams) + ',\n'
        js_lines[5] = '    "POW": ' + str(self.num_pow_teams) + ',\n'
        js_lines[6] = '    "P+": ' + str(self.num_pow_plus_teams) + '\n'
        outfile.writelines(js_lines)

        # Close out the html tags and we are done!
        outfile.write('</script>\n\n')
        outfile.write('</body>\n')
        outfile.write('</html>\n')

    def print_extracted_sked(self):
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
                time_slot_teams = set()
                for ct, game in ts_sked.time_slot_games.items():
                    if game.is_skills_clinic:
                        print(ct, ': ', game.skills_clinic_title)
                    elif game.is_open_play:
                        print(ct, ': ', game.open_play_title)
                    else:
                        print(ct, ': ', game.team_1, ' vs ', game.team_2, ' | ref: ', game.ref_team)
                        if game.team_1 in time_slot_teams:
                            print('######## CONFLICT DETECTED: Duplicate team: ', game.team_1)
                        else:
                            time_slot_teams.add(game.team_1)
                        if game.team_2 in time_slot_teams:
                            print('######## CONFLICT DETECTED: Duplicate team: ', game.team_2)
                        else:
                            time_slot_teams.add(game.team_2)
                        if game.ref_team in time_slot_teams:
                            print('######## CONFLICT DETECTED: Duplicate team: ', game.ref_team)
                        else:
                            time_slot_teams.add(game.ref_team)


def main():
    # Get the input csv filename from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-s', '--start-col', help='first column in csv that is not blank', default=0, type=int)
    parser.add_argument('-d', '--debug', help='print debugging output', action='store_true')
    args = parser.parse_args()

    # Create a schedule object to use for reading the input csv and generating the schedule html
    sked = Schedule()

    # Open the file and collect info about the schedule to be generated
    with open(args.filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        sked.parse_rows(csv_reader, args.start_col, args.debug)

    # Print extracted schedule if debug output enabled
    if args.debug:
        sked.print_extracted_sked()

    # Generate the filterable html schedule
    html_filename = 'generated_schedule.html'
    with open(html_filename, 'w') as htmlfile:
        sked.generate_html(htmlfile)


if __name__ == "__main__":
    main()
