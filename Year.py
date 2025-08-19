import random

from Week import Week
import os

class Year:
    def __init__(self, year_number, simulation, user_team_players, weeks_per_year, sim_stats, salary_cap, stadium, fans, strategies, coaches, staffers, sponsors, debug_mode):
        self.year_number = year_number
        self.simulation = simulation
        self.user_team_players = user_team_players
        self.weeks_per_year = weeks_per_year
        self.sim_stats = sim_stats
        self.salary_cap = salary_cap
        self.stadium = stadium
        self.fans = fans
        self.strategies = strategies
        self.coaches = coaches
        self.staffers = staffers
        self.sponsors = sponsors
        self.debug_mode = debug_mode

        self.coach_carousel = 3
        self.players_per_free_agency = 3
        self.trades_per_year = 1
        self.players_per_trade = 3
        self.strategies_per_offseason = 3
        self.tactics_used = 0
        self.trades_made = 0
        self.strategies_per_week = 1
        self.players_per_draft = 3
        self.development_points = 1
        self.max_sponsors = 1
        self.national_revenue = 5
        self.times_scouted = 0
        self.weeks_per_scout = 3

        self.bye_threshold = 0.75
        self.playoff_threshold = 0.55
        self.draft_threshold = 0.3

        self.week_number = 1
        self.wins = 0
        self.playoff_wins = None
        self.current_week = None
        self.opponents = {}
        self.playoff_bracket = {}

    def run_events(self):
        """Placeholder for events like matches, drafts, injuries, etc."""
        self.clear_console()
        print(f"Running events for Year {self.year_number}...")
        # Example logic
        self.handle_offseason()        
        self.handle_regular_season()

        self.view_schedule()
        print(f"\nFinal record is {self.wins}-{self.week_number-self.wins-1}")
        input("\nPress Enter to continue to the playoffs...")

        self.handle_playoffs()
        self.sim_stats['yearly_results'].append({
            'year': self.year_number,
            'wins': self.wins,
            'losses': self.week_number - self.wins - 1,
            'playoff_wins': self.playoff_wins if self.playoff_wins is not None else 'DNQ',
        })

        self.handle_postseason()

    def handle_regular_season(self):
        """Handle regular season events."""  
        self.clear_console()
        print(f"\n--- Regular Season Activities for Year {self.year_number} ---")

        while self.week_number <= self.weeks_per_year:
            self.clear_console()
            print(f"\n--- Week {self.week_number} ---")
            print(f"\nTeam record is {self.wins}-{self.week_number-self.wins-1}")
            print(f"Cash available: ${self.sim_stats['cash']}")
            print("\nChoose an activity:")
            print("1. View Team Roster")
            print("2. View Strategies")
            print("3. View Schedule")
            print("4. Make a Trade")
            print("5. Scout Opponents")
            print("6. Play Match")
            choice = input("Enter your choice (1-5): ").strip() if not self.debug_mode else '6'
            if choice == '1':
                self.display_team_roster()  
            elif choice == '2':
                self.display_strategies()
            elif choice == '3':
                self.view_schedule()
            elif choice == '4':
                self.make_trade()
            elif choice == '5':
                self.scout_opponents()
            elif choice == '6':
                tactic_ct = self.handle_tactic_ct()
                self.current_week = Week(self.week_number, self.simulation, self.user_team_players, self.opponents, self.strategies, tactic_ct, self.debug_mode)
                win = self.current_week.run_events()
                self.wins += win
                self.week_number += 1

                input("\nPress Enter to continue to the next week...")

    def decrement_contracts(self):
        """Decrement player contracts at the end of the year."""
        for player in self.user_team_players:
            player['contract'] -= 1

    def compute_contract_value(self, player):
        """Compute a new contract value for a player."""
        attr_total = sum(int(player.get(attr, 0)) for attr in ['power run', 'spread', 'west coast', 'vertical'])
        attr_total += 2*int(player.get('clutch', 0))
        return max(int(player['salary'])+1, attr_total)

    def handle_contracts(self):
        """Handle player contracts and salary cap."""

        if not self.user_team_players:
            return

        self.clear_console()
        print(f"\n--- Contract Management for Year {self.year_number} ---")
        total_salary = self.display_team_roster(display_attribute=False)
        self.decrement_contracts()

        cutlist = []

        for team_player in self.user_team_players:
            if team_player['contract'] <= 0:
                player_id = team_player['player_name']
                player = self.simulation.players.get(player_id)
                print(f"[Notice] Player {player_id} has no contract left")
                new_value = self.compute_contract_value(player)
                increased_salary = new_value - int(player['salary'])
                print(f"[Update] Player {player_id} new salary is ${new_value} and teams total salary is now ${total_salary + increased_salary}")

                extend = input(f"Do you want to extend {player_id} (y/n)? ").strip().lower()
                player['salary'] = new_value
                if extend == 'y':
                    team_player['contract'] = 2
                    print(f"[Notice] Player {player_id} has been extended.")
                    total_salary += increased_salary
                else:
                    cutlist.append(team_player)
                    print(f"[Notice] Player {player_id} has been cut.")

        for player in cutlist:
            self.user_team_players.remove(player)

        input("\nPress Enter to continue...")

    def handle_sponsors(self):
        if not self.sponsors:
            return
        
        """Handle sponsorships for the team."""
        self.clear_console()
        print(f"\n--- Sponsorship Management for Year {self.year_number} ---")
        collected_amount = sum(int(self.simulation.sponsors.get(sponsor, {}).get('value', 0)) for sponsor in self.sponsors)
        self.sim_stats['cash'] = int(self.sim_stats['cash']) + collected_amount
        print(f"[Notice] Collected ${collected_amount} from sponsors.")
        for sponsor_id in self.sponsors:
            sponsor = self.simulation.sponsors.get(sponsor_id)
            sponsor['contract'] = int(sponsor['contract']) - 1
            if sponsor['contract'] <= 0:
                self.sponsors.remove(sponsor_id)
                print(f"[Notice] Sponsor {sponsor['company']} has ended their sponsorship.")
        
        input("\nPress Enter to continue...")

    def collect_revenue(self):
        """Collect revenue from fans based on their type."""
        total_revenue = self.national_revenue

        for fan_id in self.fans:
            fan = self.simulation.fans.get(fan_id)
            total_revenue += int(fan['revenue'])

        self.sim_stats['cash'] += total_revenue
        print(f"[Notice] Collected ${total_revenue} in revenue from national revenue and fans.")
        input("\nPress Enter to continue...")

    def develop_players(self):
        """Develop players by spending development points."""

        if not self.user_team_players:
            return

        dev_points = 0

        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            dev_points += int(coach['development'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['development']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['development']} development points? (y/n)")
                if choice == 'y':
                    dev_points += int(staffer['development'])
                    self.staffers.remove(staffer_id)
                    
        if dev_points <= 0:
            return

        dev_points += self.development_points

        self.clear_console()
        print(f"\n--- Player Development for Year {self.year_number} ---")
        print(f"You have {dev_points} development points to spend.")

        while dev_points > 0:
            self.display_team_roster()

            for pid, player in enumerate(self.user_team_players, start=1):
                print(f"{pid}. {player['player_name']}")

            p_num = input("Enter the player number to develop (or 'done' to finish): ").strip()

            if p_num.lower() == 'done':
                break

            player_id = self.user_team_players[int(p_num) - 1]['player_name']
            player = self.simulation.players.get(player_id)
            if not player:
                print(f"Player ID {player_id} not found.")
                continue
            
            if int(player['dev points']) <= 0:
                print(f"Player {player['player_name']} has no development points left.")
                continue

            print(f"Developing player: {player['player_name']}")
            print("Available attributes to develop:")
            for attr in ['power run', 'spread', 'west coast', 'vertical', 'clutch']:
                print(f"  {attr}: {player.get(attr, 0)}")

            attr_to_develop = input("Enter the attribute to develop: ").strip()
            if attr_to_develop not in player:
                print(f"Attribute {attr_to_develop} not found.")
                continue

            player[attr_to_develop] = int(player[attr_to_develop]) + 1
            player['dev points'] = int(player['dev points']) - 1
            dev_points -= 1
            print(f"Developed {attr_to_develop}. Remaining points: {dev_points}")

        input("\nPress Enter to continue...")

    def replace_head_coach(self):
        self.clear_console()
        eligible_coaches = [c for c in self.simulation.coaches.values() if c['type'] == 'coach' and c['name'] != self.coaches[0] and int(c['salary']) > 0]
        if not eligible_coaches:
            print("No other coaches available to hire.")
            input("\nPress Enter to continue...")
            return
        options = random.sample(eligible_coaches, k=min(self.coach_carousel, len(eligible_coaches)))
        print("Available Coaches:")
        for i, coach in enumerate(options, start=1):
            print(f"  {i}. {coach['name']}")
            for key, value in coach.items():
                print(f"    {key}: {value}")

        print(f"Available Cash: ${self.sim_stats['cash']}")

        choice = input("Enter the number of the coach to hire: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            if int(self.sim_stats['cash']) < int(options[int(choice) - 1]['salary']):
                print("You do not have enough cash to hire this coach.")
                input("\nPress Enter to continue...")
                return
            new_coach = options[int(choice) - 1]['name']
            self.coaches[0] = new_coach
            print(f"[Update] Head Coach changed to {new_coach}.")

    def add_staffer(self):
        eligible_staffers = [c for c in self.simulation.coaches.values() if c['type'] == 'staffer']
        if not eligible_staffers:
            print("No staffers available to hire.")
            input("\nPress Enter to continue...")
            return
        
        print("\nAvailable Staffers:")
        for idx, staffer in enumerate(eligible_staffers, start=1):
            print(f"{idx}. {staffer['name']}")
            for key, value in staffer.items():
                print(f"  {key}: {value}")

        print(f"Available Cash: ${self.sim_stats['cash']}")
        choices = input("Enter the indices of the staffer(s) to hire: ").strip()
        if choices:
            indices = choices.split(',')
            for index in indices:
                if index.isdigit() and 1 <= int(index) <= len(eligible_staffers):
                    staffer = eligible_staffers[int(index) - 1]
                    if int(self.sim_stats['cash']) < int(staffer['salary']):
                        print(f"You do not have enough cash to hire {staffer['name']}.")
                        continue
                    self.staffers.append(staffer['name'])
                    self.sim_stats['cash'] = int(self.sim_stats['cash']) - int(staffer['salary'])
                    print(f"[Update] Staffer {staffer['name']} has been hired.")
                else:
                    print(f"Invalid choice: {index}. Please enter a valid index.")

    def view_staff(self):
        """View current staff including head coach and staffers."""

        if not self.coaches and not self.staffers:
            return 
        
        print(f"\n--- Current Staff for Year {self.year_number} ---")
        
        if not self.coaches:
            print("No coaches hired yet.")
            return
        
        print(f"Head Coach: {self.coaches[0]}")
        for key, value in self.simulation.coaches.get(self.coaches[0], {}).items():
            print(f"  {key}: {value}")
        for staffer in self.staffers:
            print(f"Staffer: {staffer}")
            for key, value in self.simulation.coaches.get(staffer, {}).items():
                print(f"  {key}: {value}")

        input("\nPress Enter to continue...")

    def manage_coaches(self):
        """Manage coaches for the team."""
        self.clear_console()
        print(f"\n--- Coach Management for Year {self.year_number} ---")

        self.view_staff()

        ready_to_proceed = False
        while not ready_to_proceed:
            self.clear_console()
            print(f"\n--- Coach Management for Year {self.year_number} ---")
            print("Choose an action:")
            print("1. View Current Staff")
            print("2. Hire New Head Coach")
            print("3. Add Staffer")
            print("4. Exit Coach Management")

            choice = input("Enter your choice (1-4): ").strip() #if not self.debug_mode else '4'
            if choice == '1':
                self.view_staff()
            elif choice == '2':
                self.replace_head_coach()
            elif choice == '3':
                self.add_staffer()
            elif choice == '4':
                ready_to_proceed = True
            else:
                print("Invalid choice, please try again.")

        coach = self.simulation.coaches.get(self.coaches[0], {})
        if int(coach['salary']) > self.sim_stats['cash']:
            self.coach = ['Base Coach']
            print("You do not have enough cash for current coach, replacing with Base Coach.")

        self.sim_stats['cash'] = int(self.sim_stats['cash']) - int(coach.get('salary', 0))

        input("\nPress Enter to continue...")

    def handle_tactic_ct(self):
        
        tactic_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            tactic_pt += int(coach['tactics'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['tactics']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['tactic']} tactics points? (y/n)")
                if choice == 'y':
                    tactic_pt += int(staffer['recruiting'])
                    self.staffers.remove(staffer_id)
                    
        if tactic_pt < self.tactics_used:
            return 0
        
        self.tactics_used += 1
        return 3

    def handle_offseason(self):
        """Handle offseason activities like adding players and strategies."""
        added_players = False
        managed_coaches = False
        added_strategies = False
        ready_to_proceed = False
        self.collect_revenue()
        self.handle_sponsors()
        self.handle_contracts()
        self.schedule_matches()

        while not ready_to_proceed:
            self.clear_console()
            print(f"\n--- Offseason Activities for Year {self.year_number} ---")
            print("\nChoose an offseason activity:")
            print("1. Add Players")
            print("2. Manage Coaches")
            print("3. Manage Strategies")
            print("4. Develop Players")
            print("5. View Team Roster")
            print("6. View Strategies")
            print("7. View Schedule")
            print("8. Exit Offseason")

            choice = input("Enter your choice (1-8): ").strip() #if not self.debug_mode else '8'
            if choice == '1':
                if not added_players:
                    added_players = True
                    self.add_players()
                else:
                    print("You have already added players this offseason.")
                    input("Press enter to continue...")
            elif choice == '2':
                if not managed_coaches:
                    managed_coaches = True
                    self.manage_coaches()
                else:
                    print("You have already managed coaches offseason.")
                    input("Press enter to continue...")
            elif choice == '3':
                if not added_strategies:
                    added_strategies = True
                    self.add_strategies()
                else:
                    print("You have already added strategies this offseason")
                    input("Press enter to continue...")
            elif choice == '4':
                self.develop_players()
            elif choice == '5':
                self.display_team_roster()
            elif choice == '6':
                self.display_strategies()
            elif choice == '7':
                self.view_schedule()
            elif choice == '8':
                ready_to_proceed = True
            else:
                print("Invalid choice, please try again.")

    def handle_playoffs(self):
        """Handle NFL-like 12-team playoff bracket."""
        self.clear_console()
        print(f"\n--- Playoff Activities for Year {self.year_number} ---")

        total_games = self.weeks_per_year
        win_pct = self.wins / total_games if total_games else 0
        made_playoffs = win_pct >= self.playoff_threshold

        if not made_playoffs:
            print("Your team did not qualify for the playoffs this year.")
            input("\nPress Enter to continue...")
            return
        
        has_bye = win_pct >= self.bye_threshold
        games_needed = 3 if has_bye else 4

        playoff_round = 1 if not has_bye else 2  # Start at Divisional if bye
        self.playoff_wins = 0

        self.schedule_playoffs()

        def view_playoff_bracket():
            self.clear_console()
            print(f"\n🏆 Year {self.year_number} Playoff Bracket:")

            for i, round_info in self.playoff_bracket.items():
                if has_bye and i == 1:
                    print(f"{round_info['name']}: Bye")
                elif round_info['team'] is None:
                    print(f"{round_info['name']}: Not Played")
                else:
                    print(f"{round_info['name']} vs {round_info['team']['team_name']}: {round_info['result']}")

            input("\nPress Enter to continue...")

        while self.playoff_wins < games_needed:
            self.clear_console()
            print(f"\n--- Playoff Round: {self.playoff_bracket[playoff_round]['name']} ---")
            print("\nChoose an activity:")
            print("1. View Team Roster")
            print("2. View Strategies")
            print("3. View Playoff Bracket")
            print("4. Scout Playoff Opponents")
            print("5. Play Playoff Game")
            choice = input("Enter your choice (1-4): ").strip() if not self.debug_mode else '5'
            if choice == '1':
                self.display_team_roster()
            elif choice == '2':
                self.display_strategies()
            elif choice == '3':
                view_playoff_bracket()
            elif choice == '4':
                self.scout_playoff_opponents()
            elif choice == '5':
                # Simulate a playoff game
                # You can customize opponent logic as needed
                print("\nPlaying playoff game...")
                
                tactic_ct = self.handle_tactic_ct()
                self.current_week = Week(playoff_round, self.simulation, self.user_team_players, self.playoff_bracket, self.strategies, tactic_ct, self.debug_mode)
                win = self.current_week.run_events()

                if win < 0.5:
                    print("You lost the playoff game.")
                    break

                self.playoff_wins += 1
                playoff_round += 1
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice, please try again.")

        view_playoff_bracket()
        if self.playoff_wins == games_needed:
            print("🎉 Congratulations! You won the Super Bowl!")
            self.sim_stats['sb_wins'] += 1
        else:
            print("🏈 Your playoff run has ended.")
        input("\nPress Enter to finish the playoffs...")

    def handle_postseason(self):
        """Handle postseason activities after playoffs."""
        self.clear_console()
        print(f"\n--- Postseason Activities for Year {self.year_number} ---")
        print("You can now review your season and prepare for the next year.")
        
        # Example logic: Display final stats, reset for next year, etc.
        total_games = self.weeks_per_year
        success = (self.wins + 2*self.playoff_wins) / total_games if self.playoff_wins else self.wins / total_games
        stadium = self.simulation.stadiums.get(self.stadium[0])
        
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            success += int(coach['outreach'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['outreach']) > 0:
                choice = print(f"Would you like to use {staffer_id} this offseason for {staffer['outreach']} outreach points? (y/n)")
                if choice == 'y':
                    success += int(staffer['outreach'])
                    self.staffers.remove(staffer_id)
        
        self.handle_fans(success, stadium)

        input("\nPress Enter to continue to the draft (if eligible)...")
        self.draft_players()
        input("\nPress Enter to continue to sponsorship (if eligible)...")
        self.add_sponsors()
        input("\nPress Enter to finish the postseason...")

    def handle_fans(self, performance_rating, stadium):
        """Handle fan reactions based on team performance."""
        flag_removal = []
        filled_box_seats = 0

        self.clear_console()
        print(f"\n--- Fan Engagement for Year {self.year_number} ---")

        ticket_ct = 0
        for fan_id in self.fans:
            fan = self.simulation.fans.get(fan_id)
            ticket_ct += int(fan['ticket_count'])
            if fan['type'] == 'box':
                filled_box_seats += 1
            if ticket_ct > performance_rating:
                print(f"[Notice] Fan {fan_id} has been removed due to low performance.")
                input("Press Enter to continue...")
                flag_removal.append(fan_id)
                
        for fan_id in flag_removal:
            self.fans.remove(fan_id)
                
        if ticket_ct < performance_rating:
            adding_fans = True
            
            while adding_fans:
                random_fan_key = random.choice(list(self.simulation.fans.keys()))
                random_fan = self.simulation.fans[random_fan_key]
                
                if len(self.fans) >= int(stadium['general_seating']) + int(stadium['box_seating']):
                    print("Stadium is at full capacity, cannot add more fans.")
                    break
                
                if random_fan['type'] == 'box' and filled_box_seats + 1 > int(stadium['box_seating']):
                    continue
                
                if ticket_ct + int(random_fan['ticket_count']) <= performance_rating:
                    self.fans.append(random_fan_key)
                    ticket_ct += int(random_fan['ticket_count'])
                    if random_fan['type'] == 'box':
                        filled_box_seats += 1
                    print(f"[Notice] Fan {random_fan_key} has been added to the team.")
                    input("Press Enter to continue...")
                else:
                    adding_fans = False

        self.display_stadium()

    def clear_console(self):
        """Clear the console for better readability."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def scout_opponents(self):
        
        self.clear_console()
        print(f"\n--- Scouting Opponents for Year {self.year_number} ---")
        scout_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            scout_pt += int(coach['scouting'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['scouting']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['scouting']} scouting points? (y/n)")
                if choice == 'y':
                    scout_pt += int(staffer['scouting'])
                    self.staffers.remove(staffer_id)
        
        if scout_pt <= self.times_scouted:
            print("[Notice] No more scouting points available this year.")
            input("\nPress Enter to continue...")
            return

        for week_num in range(self.week_number, min(self.week_number + self.weeks_per_scout, self.weeks_per_year + 1)):
            opponent = self.opponents.get(week_num)
            if opponent and opponent['result'] == 'Not Played':
                print(f"Scouting Week {week_num} opponent: {opponent['team']['team_name']}")
                print("Attributes:")
                for attr, value in opponent['team'].items():
                    print(f"  {attr}: {value}")
        
        input("\nPress Enter to continue...")
        self.times_scouted += 1

    def scout_playoff_opponents(self):
        
        self.clear_console()
        print(f"\n--- Scouting Playoff Opponents for Year {self.year_number} ---")
        scout_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            scout_pt += int(coach['scouting'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['scouting']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['scouting']} scouting points? (y/n)")
                if choice == 'y':
                    scout_pt += int(staffer['scouting'])
                    self.staffers.remove(staffer_id)
        
        if scout_pt <= self.times_scouted:
            print("[Notice] No more scouting points available this year.")
            input("\nPress Enter to continue...")
            return

        for week_num in range(1, 5):
            opponent = self.playoff_bracket.get(week_num)
            if opponent and opponent['result'] == 'Not Played':
                print(f"Scouting Playoff Week {week_num} opponent: {opponent['team']['team_name']}")
                print("Attributes:")
                for attr, value in opponent['team'].items():
                    print(f"  {attr}: {value}")
        
        input("\nPress Enter to continue...")
        self.times_scouted += 1
                
    def view_schedule(self):
        """Display the schedule for the year."""
        self.clear_console()
        print(f"\n📅 Year {self.year_number} Schedule:")
        for week in range(1, self.weeks_per_year + 1):
            print(f"Week {week} vs {self.opponents[week]['team']['team_name']}: {self.opponents[week]['result']}")

        input("\nPress Enter to continue...")

    def schedule_matches(self):
        """Select unique opponent teams for the year."""
        all_teams = list(self.simulation.teams.values())  # Assuming teams is a dict
        selected = random.sample(all_teams, k=self.weeks_per_year)
        for week in range(1, self.weeks_per_year + 1):
            self.opponents[week] = {
                'team': selected[week - 1],
                'result': 'Not Played'
            }

    def schedule_playoffs(self):
        """Select unique opponent teams for the playoffs."""
        all_teams = list(self.simulation.teams.values())  # Assuming teams is a dict
        round_names = ["Wildcard", "Divisional", "Conference", "Super Bowl"]
        selected = random.sample(all_teams, k=4)
        for week in range(1, 5):
            self.playoff_bracket[week] = {
                'name': round_names[week - 1],
                'team': selected[week - 1],
                'result': 'Not Played'
            }

    def display_team_roster(self, display_attribute=True):

        if not self.user_team_players:
            return None
        
        self.clear_console()

        print("\n📋 Your Team Roster:")
        for team_player in self.user_team_players:
            pid = team_player.get('player_name')
            player = self.simulation.players.get(pid)
            if player:
                print(f"\nPlayer ID: {pid}")
                for key, value in player.items():
                    print(f"  {key}: {value}")
                print(f"  contract: {team_player.get('contract', 'N/A')}")
            else:
                print(f"⚠️ Player ID {pid} not found in simulation database.")

        # Sum calculations
        total_salary = 0
        total_clutch = 0
        offense_sums = {'power run': 0, 'spread': 0, 'west coast': 0, 'vertical': 0}
        defense_sums = {'power run': 0, 'spread': 0, 'west coast': 0, 'vertical': 0}

        for team_player in self.user_team_players:
            pid = team_player.get('player_name')
            player = self.simulation.players.get(pid)
            if player:
                total_salary += int(player.get('salary', 0))
                total_clutch += int(player.get('clutch', 0))
                side = player.get('side', '').lower()
                for attr in offense_sums:
                    val = player.get(attr, 0)
                    if side == 'offense':
                        offense_sums[attr] += int(val)
                    elif side == 'defense':
                        defense_sums[attr] += int(val)

        if display_attribute:
            print("\nTeam Attributes:")
            print(f"Total Salary: ${total_salary}")
            print(f"Total Clutch: {total_clutch}")
            print("Offense Attribute Sums:")
            for attr, val in offense_sums.items():
                print(f"  {attr}: {val}")
            print("Defense Attribute Sums:")
            for attr, val in defense_sums.items():
                print(f"  {attr}: {val}")

        input("\nPress Enter to continue...")

        return total_salary

    def display_strategies(self):
        if not self.strategies:
            return
        
        self.clear_console()

        print("\n📋 Your Current Strategies:")
        for tid in self.strategies:
            strategy = self.simulation.strategies.get(tid)
            if strategy:
                print(f"\Strategy Name: {tid}")
                for key, value in strategy.items():
                    print(f"  {key}: {value}")

        input("\nPress Enter to continue...")
    
    def display_stadium(self):
        self.clear_console()
        stadium = self.simulation.stadiums.get(self.stadium[0])
        if not stadium:
            print("\n📭 You have no stadium assigned.")
            input("\nPress Enter to continue...")
            return

        print("\n🏟️ Your Stadium Details:")
        for key, value in stadium.items():
            print(f"  {key}: {value}")

        print("Fans in your stadium:")
        for fan_id in self.fans:
            fan = self.simulation.fans.get(fan_id)
            if fan:
                print(f"  {fan['name']} Type: {fan['type']}, Interest: {fan['interest']}, Loyalty: {fan['loyalty']}")
            else:
                print(f"⚠️ Fan ID {fan_id} not found in simulation database.")

        input("\nPress Enter to continue...")

    def cut_players(self):
        """Command-line prompt to cut players from your team."""

        if not self.user_team_players:
            return 0

        team_cost = self.display_team_roster(display_attribute=False)

        if not self.user_team_players:
            print("[Notice] Your team has no players to cut.")
            return team_cost
        
        print(f"\nCurrent Team Cost: ${team_cost}, Salary Cap: ${self.salary_cap}, and Cash on Hand: ${self.sim_stats['cash']}")
        print("\nEnter the number(s) of the player(s) you want to cut (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= len(self.user_team_players)}

        if not selected_indices:
            print("[Notice] No valid player IDs selected.")
            return team_cost
        for pid in selected_indices:
            player_id = self.user_team_players[pid - 1]  # Convert to actual player
            self.user_team_players.remove(player_id)
            
        team_cost = self.display_team_roster(display_attribute=False)
        return team_cost

    def player_name_exists(self, player_name): 
        """Check if a player_name exists in user_team_players."""
        return any(player.get('player_name') == player_name for player in self.user_team_players)

    def make_trade(self):
        """Command-line prompt to make trades with other teams."""
        self.clear_console()
        print(f"\n--- Trade Management for Year {self.year_number} ---")

        if not self.user_team_players:
            print("[Notice] Your team has no players to trade.")
            input("\nPress Enter to continue...")
            return

        trade_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            trade_pt += int(coach['trading'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['trading']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['trading']} trading points? (y/n)")
                if choice == 'y':
                    trade_pt += int(staffer['trading'])
                    self.staffers.remove(staffer_id)
        
        if trade_pt <= self.trades_made:
            print("[Notice] No more trading points available this year.")
            input("\nPress Enter to continue...")
            return

        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players and int(p.get('salary', 0)) > 0]
        
        if not eligible_players:
            print("[Notice] No eligible players available for trade.")
            input("\nPress Enter to continue...")
            return
        
        options = random.sample(eligible_players, k=min(self.players_per_trade, len(eligible_players)))
        
        print("\nAvailable Players for Trade:")
        for idx, player in enumerate(options, start=1):
            print(f"\nPlayer {idx}:")
            for key, value in player.items():
                print(f"  {key}: {value}")
                
        print("\nEnter the number of the player you want to trade for:")
        choice = input(">> ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            
            trade_complete = False
            
            while not trade_complete:
                print("\nSelect player(s) from your team to trade away:")
                for idx, team_player in enumerate(self.user_team_players, start=1):
                    pid = team_player.get('player_name')
                    player = self.simulation.players.get(pid)
                    if player:
                        print(f"\nPlayer {idx}:")
                        for key, value in player.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"⚠️ Player ID {pid} not found in simulation database.")
                        
                trade_choice = input("Enter the number(s) of the player(s) to trade away (e.g. 1 or 1,3): ").strip()
                selected_trade_indices = {int(i) for i in trade_choice.split(",") if i.isdigit() and 1 <= int(i) <= len(self.user_team_players)}

                print(f"\nCurrent Cash on Hand: ${self.sim_stats['cash']}")
                added_money = int(input("Enter any additional money you want to include in the trade (positive) or ask for in exchange (negative): ").strip())

                if added_money > int(self.sim_stats['cash']):
                    print(f"[Error] Only ${self.sim_stats['cash']} available on hand.")
                    continue

                cumulative_salary = sum(int(self.simulation.players.get(self.user_team_players[i - 1].get('player_name'), {}).get('salary', 0)) for i in selected_trade_indices)
                
                if added_money + cumulative_salary < int(options[int(choice) - 1].get('salary', 0)):
                    print("[Error] Trade offer was rejected.")
                    continue
                
                # Execute trade
                new_player = {
                    'player_name': options[int(choice) - 1]['player_name'],
                    'contract': 2
                }
                self.user_team_players.append(new_player)
                
                for i in selected_trade_indices:
                    pid = self.user_team_players[i - 1]  # Convert to actual player
                    self.user_team_players.remove(pid)
                
                self.sim_stats['cash'] = int(self.sim_stats['cash']) - added_money
                self.trades_made += 1
                print(f"[Success] Trade completed! You acquired {new_player['player_name']}.")
                trade_complete = True
        else:
            print("[Error] Invalid choice for player to trade for.")
        
        input("\nPress Enter to continue...")

    def add_players(self):
        """Command-line prompt to add players from simulation."""        

        recruit_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            recruit_pt += int(coach['recruiting'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['recruiting']) > 0:
                choice = print(f"Would you like to use {staffer_id} this offseason for {staffer['recruiting']} recruiting points? (y/n)")
                if choice == 'y':
                    recruit_pt += int(staffer['recruiting'])
                    self.staffers.remove(staffer_id)

        if recruit_pt <= 0:
            return

        team_cost = self.display_team_roster() or 0  # Step 1: Show team before selection

        # Only show players not already on the team and greater than 0 salary
        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players and int(p.get('salary', 0)) > 0]

        recruit_ct = self.players_per_free_agency

        if len(eligible_players) < recruit_ct:
            print("[Notice] Not enough eligible players.")
            return

        options = random.sample(eligible_players, k=recruit_ct)

        self.clear_console()
        print("\n🎯 Choose a player to add to your team:")
        for idx, player in enumerate(options, start=1):
            attrs = ', '.join(f"{key}: {value}" for key, value in player.items())
            print(f"Player {idx}: {attrs}")

        print("\nEnter the number(s) of the player(s) you want to add (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= recruit_ct}

        for i in selected_indices:
            player_id = options[i - 1]['player_name']
            if not self.player_name_exists(player_id):
                if team_cost + int(options[i - 1].get('salary', 0)) > self.salary_cap:
                    print(f"[Skipped] Adding {player_id} would exceed salary cap.")
                    input("Press Enter to continue")
                    continue
                if team_cost + int(options[i - 1].get('salary', 0)) > int(self.sim_stats['cash']):
                    print(f"[Skipped] Adding {player_id} would exceed money on hand.")
                    input("Press Enter to continue")
                    continue
                player = {
                    'player_name': player_id,
                    'contract': 2
                }
                self.user_team_players.append(player)
                print(f"[Added] Player {player_id} to your team!")
            else:
                print(f"[Skipped] Player {player_id} is already on your team.")

        team_cost = self.display_team_roster() or 0  # Step 2: Show team after updates
        
        if team_cost > self.salary_cap or team_cost > int(self.sim_stats['cash']):
            print(f"[Warning] Your team salary exceeds the salary cap of ${self.salary_cap} or cash on hand of ${self.sim_stats['cash']}.")
            print("You will need to cut players to stay under the cap.")
            while team_cost > self.salary_cap or team_cost > int(self.sim_stats['cash']):
                team_cost = self.cut_players()
        self.sim_stats['cash'] = int(self.sim_stats['cash']) - team_cost

    def add_strategies(self):

        strategy_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            strategy_pt += int(coach['strategy'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['strategy']) > 0:
                choice = print(f"Would you like to use {staffer_id} this offseason for {staffer['strategy']} strategy points? (y/n)")
                if choice == 'y':
                    strategy_pt += int(staffer['strategy'])
                    self.staffers.remove(staffer_id)  

        eligible_strategies = [t for tid, t in self.simulation.strategies.items() if tid not in self.strategies and t['type'] == 'base']
        if strategy_pt >= 2:
            eligible_strategies += [t for tid, t in self.simulation.strategies.items() if tid not in self.strategies and t['type'] == 'intermediate']
            advanced_strategies = [t for tid, t in self.simulation.strategies.items() if tid not in self.strategies and t['type'] == 'advanced']
            eligible_strategies += random.sample(advanced_strategies, k=min(3, len(advanced_strategies)))
        elif strategy_pt >= 1:
            intermediate_strategies = [t for tid, t in self.simulation.strategies.items() if tid not in self.strategies and t['type'] == 'intermediate']
            eligible_strategies += random.sample(intermediate_strategies, k=min(3, len(intermediate_strategies)))

        options = random.sample(eligible_strategies, k=self.strategies_per_offseason)

        self.clear_console()
        print("\n🎯 Choose a strategy to add:")
        for idx, strategy in enumerate(options, start=1):
            attrs = ', '.join(f"{key}: {value}" for key, value in strategy.items())
            print(f"Strategy {idx}: {attrs}")

        print("\nEnter the number of the strategy you want to add:")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= self.strategies_per_offseason}

        for i in selected_indices:
            strategy_id = options[i - 1]['name']
            if strategy_id not in self.strategies:
                self.strategies.append(strategy_id)
                print(f"[Added] Strategy {strategy_id} to your team!")
            else:
                print(f"[Skipped] Strategy {strategy_id} is already on your team.")

        self.display_strategies()  # Step 2: Show team after updates

    def draft_players(self):
        self.clear_console()
        
        draft_pt = 0
        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            draft_pt += int(coach['drafting'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['drafting']) > 0:
                choice = print(f"Would you like to use {staffer_id} this offseason for {staffer['drafting']} drafting points? (y/n)")
                if choice == 'y':
                    draft_pt += int(staffer['drafting'])
                    self.staffers.remove(staffer_id)  
        
        # Compute win percentage
        total_games = self.weeks_per_year
        win_pct = self.wins / total_games if total_games else 0

        # Determine draft eligibility based on win percentage
        if win_pct > self.draft_threshold or draft_pt <= 0:
            return
        
        print("[Draft Eligibility] You are eligible to draft players.")
        self.display_team_roster()
        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players and int(p.get('salary', 0)) == 0]
        if not eligible_players:
            print("[Notice] No eligible players available for drafting.")
            input("\nPress Enter to continue...")
            return
        
        draft_ct = self.players_per_draft

        options = random.sample(eligible_players, k=min(draft_ct, len(eligible_players)))

        print("\n🎯 Choose a player to draft:")
        for idx, player in enumerate(options, start=1):
            attrs = ', '.join(f"{key}: {value}" for key, value in player.items())
            print(f"Player {idx}: {attrs}")

        print("\nEnter the number of the player you want to draft:")
        choice = input(">> ").strip()
        selected_index = int(choice)

        if selected_index < 1 or selected_index > len(options):
            print("[Error] Invalid player selection.")
            input("\nPress Enter to continue...")
            return

        player_to_draft = options[selected_index - 1]

        player = {
            'player_name': player_to_draft['player_name'],
            'contract': 2
        }
        self.user_team_players.append(player)
        print(f"[Added] Player {player_to_draft['player_name']} to your team!")

        self.display_team_roster()

    def add_sponsors(self):
        """Add sponsors to the team."""
        sponsor_pt = self.max_sponsors

        for coach_id in self.coaches:
            coach = self.simulation.coaches.get(coach_id,{})
            sponsor_pt += int(coach['fundraising'])

        for staffer_id in self.staffers:
            staffer = self.simulation.coaches.get(staffer_id,{})
            if int(staffer['fundraising']) > 0:
                choice = print(f"Would you like to use {staffer_id} this year for {staffer['fundraising']} fundraising points? (y/n)")
                if choice == 'y':
                    sponsor_pt += int(staffer['fundraising'])
                    self.staffers.remove(staffer_id)

        self.clear_console()
        print(f"\n--- Sponsor Management for Year {self.year_number} ---")
        
        if sponsor_pt <= 0 or len(self.sponsors) >= self.max_sponsors:
            return
        
        print("You can add sponsors to your team to increase revenue.")

        eligible_sponsors = [s for s in self.simulation.sponsors.values() if s['company'] not in self.sponsors and int(s['contract']) > 0]

        if not eligible_sponsors:
            print("[Notice] No eligible sponsors available.")
            input("\nPress Enter to continue...")
            return

        print("Available Sponsors:")
        win_pct = self.wins / self.weeks_per_year if self.weeks_per_year else 0
        num_choices = 1
        if win_pct >= self.playoff_threshold:
            num_choices = 3
        elif win_pct >= self.draft_threshold:
            num_choices = 2

        choices = random.sample(list(self.simulation.sponsors.values()), k=min(num_choices, len(self.simulation.sponsors)))

        for idx, sponsor in enumerate(choices, start=1):
            print(f"\nSponsor {idx}:")
            for key, value in sponsor.items():
                print(f"  {key}: {value}")

        choice = input("Enter the number(s) of the sponsor you want to add (or 'done' to finish): ").strip()
        if choice.lower() == 'done':
            return

        selected_choices = [int(c) for c in choice.split(",") if c.isdigit()]
        if not selected_choices:
            print("[Error] Invalid choice.")
            input("\nPress Enter to continue...")
            return

        for sponsor_id in selected_choices:
            if len(self.sponsors) >= self.max_sponsors:
                print("[Notice] Maximum number of sponsors reached.")
                input("\nPress Enter to continue...")
                return
            self.sponsors.append(choices[sponsor_id - 1]['company'])
            print(f"[Added] Sponsor {choices[sponsor_id - 1]['company']}.")

        input("\nPress Enter to continue...")