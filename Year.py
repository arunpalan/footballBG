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
        self.strategies_per_offseason = 3
        self.strategies_per_week = 1
        self.players_per_draft = 3
        self.development_points = 3
        self.max_sponsors = 1

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
            print("4. Play Match")
            choice = input("Enter your choice (1-4): ").strip() if not self.debug_mode else '4'
            if choice == '1':
                self.display_team_roster()  
            elif choice == '2':
                self.display_strategies()
            elif choice == '3':
                self.view_schedule()
            elif choice == '4':
                self.current_week = Week(self.week_number, self.simulation, self.user_team_players, self.opponents, self.strategies, self.debug_mode)
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

        if total_salary > self.salary_cap:
            print(f"[Warning] Your team salary exceeds the salary cap of ${self.salary_cap}.")
            print("You will need to cut players to stay under the cap.")
            while total_salary > self.salary_cap:
                total_salary = self.cut_players()

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
        total_revenue = 0

        for fan_id in self.fans:
            fan = self.simulation.fans.get(fan_id)
            total_revenue += int(fan['revenue'])

        self.sim_stats['cash'] += total_revenue
        print(f"[Notice] Collected ${total_revenue} in revenue from fans.")
        input("\nPress Enter to continue...")

    def develop_players(self):
        """Develop players by spending development points."""

        if not self.user_team_players:
            return

        self.clear_console()
        print(f"\n--- Player Development for Year {self.year_number} ---")
        print(f"You have {self.development_points} development points to spend.")

        while self.development_points > 0:
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

            print(f"Developing player: {player['player_name']}")
            print("Available attributes to develop:")
            for attr in ['power run', 'spread', 'west coast', 'vertical', 'clutch']:
                print(f"  {attr}: {player.get(attr, 0)}")

            attr_to_develop = input("Enter the attribute to develop: ").strip()
            if attr_to_develop not in player:
                print(f"Attribute {attr_to_develop} not found.")
                continue

            development_amount = input("Enter the amount to develop (1-3): ").strip()
            if not development_amount.isdigit() or not (1 <= int(development_amount) <= 3):
                print("Invalid amount. Please enter a number between 1 and 3.")
                continue

            development_amount = int(development_amount)
            if development_amount > self.development_points:
                print(f"Not enough development points. You have {self.development_points} points left.")
                continue

            player[attr_to_develop] = int(player[attr_to_develop]) + development_amount
            self.development_points -= development_amount
            print(f"Developed {attr_to_develop} by {development_amount}. Remaining points: {self.development_points}")

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
        
        coach = self.simulation.coaches.get(self.coaches[0], {})
        if int(coach['salary']) > self.sim_stats['cash']:
            self.coach = ['Base Coach']
            print("You do not have enough cash for current coach, replacing with Base Coach.")

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

        self.sim_stats['cash'] = int(self.sim_stats['cash']) - int(self.simulation.coaches.get(self.coaches[0], {}).get('salary', 0))

        input("\nPress Enter to continue...")

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
                self.manage_coaches()
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
        
        has_bye = win_pct >= self
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
            print("4. Play Playoff Game")
            choice = input("Enter your choice (1-4): ").strip() if not self.debug_mode else '4'
            if choice == '1':
                self.display_team_roster()
            elif choice == '2':
                self.display_strategies()
            elif choice == '3':
                view_playoff_bracket()
            elif choice == '4':
                # Simulate a playoff game
                # You can customize opponent logic as needed
                print("\nPlaying playoff game...")

                self.current_week = Week(playoff_round, self.simulation, self.user_team_players, self.playoff_bracket, self.strategies, self.debug_mode)
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

        if success > float(stadium['expectations']) + 0.1:
            print(f"Your team greatly exceeded expectations this year!")
            self.handle_fans(2)
        elif success > float(stadium['expectations']):
            print(f"Your team exceeded expectations this year.")
            self.handle_fans(1)
        elif success < float(stadium['expectations']) - 0.1:
            print(f"Your team disappointed this year.")
            self.handle_fans(-2)
        else:
            print(f"Your team did not meet expectations this year.")
            self.handle_fans(-1)

        input("\nPress Enter to continue to the draft...")
        self.draft_players()
        input("\nPress Enter to continue to sponsorship...")
        self.add_sponsors()
        input("\nPress Enter to finish the postseason...")

    def add_fans(self):
        general_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'general']
        premium_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'premium']
        box_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'box']

        stadium = self.simulation.stadiums.get(self.stadium[0])

        if int(stadium['box_seating']) > len(box_fans):

            # Filter fans with type 'box' and interest 'low'
            filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'box' and self.simulation.fans.get(fan)['interest'] == 'low']

            if filtered:
                selected_fan = random.choice(filtered)
                self.fans.append(selected_fan)
            else:
                print("No matching fan found.")
                input("\nPress Enter to continue...")

        elif int(stadium['premium_seating']) > len(premium_fans):
            # Filter fans with type 'premium' and interest 'low'
            filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'premium' and self.simulation.fans.get(fan)['interest'] == 'low']

            if filtered:
                selected_fan = random.choice(filtered)
                self.fans.append(selected_fan)
            else:
                print("No matching fan found.")
                input("\nPress Enter to continue...")

        elif int(stadium['general_seating']) > len(general_fans):
            # Filter fans with type 'general' and interest 'low'
            filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'general' and self.simulation.fans.get(fan)['interest'] == 'low']

            if filtered:
                selected_fan = random.choice(filtered)
                self.fans.append(selected_fan)
            else:
                print("No matching fan found.")
                input("\nPress Enter to continue...")

        else:
            print("No more fans can be added, all seats are filled.")
            input("\nPress Enter to continue...")

    def upgrade_fans(self):
        general_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'general']
        premium_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'premium']
        box_fans = [fan for fan in self.fans if self.simulation.fans.get(fan)['type'] == 'box']

        for box_fan in box_fans:
            if box_fan['interest'] == 'low':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'box' and self.simulation.fans.get(fan)['interest'] == 'medium']
                
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(box_fan)
                    return
            elif box_fan['interest'] == 'medium':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'box' and self.simulation.fans.get(fan)['interest'] == 'high']
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(box_fan)
                    return

        for premium_fan in premium_fans:
            if self.simulation.fans.get(premium_fan)['interest'] == 'low':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'premium' and self.simulation.fans.get(fan)['interest'] == 'medium']
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(premium_fan)
                    return
            elif self.simulation.fans.get(premium_fan)['interest'] == 'medium':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'premium' and self.simulation.fans.get(fan)['interest'] == 'high']
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(premium_fan)
                    return

        for general_fan in general_fans:
            if self.simulation.fans.get(general_fan)['interest'] == 'low':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'general' and self.simulation.fans.get(fan)['interest'] == 'medium']
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(general_fan)
                    return

            elif self.simulation.fans.get(general_fan)['interest'] == 'medium':
                filtered = [fan for fan in self.simulation.fans if self.simulation.fans.get(fan)['type'] == 'general' and self.simulation.fans.get(fan)['interest'] == 'high']
                if filtered:
                    selected_fan = random.choice(filtered)
                    self.fans.append(selected_fan)
                    self.fans.remove(general_fan)
                    return
                
        print("No fans can be upgraded, all fans are already at the highest level.")
        input("\nPress Enter to continue...")

    def change_stadium(self):
        """Change the stadium to improve fan experience."""
        current_stadium = self.simulation.stadiums.get(self.stadium[0])

        eligible_stadiums = [s for s in self.simulation.stadiums.values() if s['name'] != current_stadium['name']]
        if not eligible_stadiums:
            print("No other stadiums available to change to.")
            input("\nPress Enter to continue...")
            return
        
        self.clear_console()
        print(f"\nAvailable Cash: ${self.sim_stats['cash']}")
        print("\nAvailable Stadiums:")
        for idx, stadium in enumerate(eligible_stadiums, start=1):
            print(f"Stadium {idx}:")
            for key, value in stadium.items():
                print(f"  {key}: {value}")

        choice = input("\nEnter the number of the stadium you want to change to: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(eligible_stadiums):
            if int(self.sim_stats['cash']) < int(eligible_stadiums[int(choice) - 1]['cost']):
                print("You do not have enough cash to change to this stadium.")
                input("\nPress Enter to continue...")
                return
            self.sim_stats['cash'] = int(self.sim_stats['cash']) - int(eligible_stadiums[int(choice) - 1]['cost'])
            new_stadium = eligible_stadiums[int(choice) - 1]['name']
            self.stadium[0] = new_stadium
            print(f"[Update] Stadium changed to {new_stadium}.")
            print(f"Available Cash: ${self.sim_stats['cash']}")
            input("\nPress Enter to continue...")

    def handle_fans(self, performance_rating):
        """Handle fan reactions based on team performance."""
        flag_removal = []

        for fan_id in self.fans:
            fan = self.simulation.fans.get(fan_id)
            if fan:
                if 2*random.randint(1,6) - performance_rating > int(fan['loyalty']):
                    print(f"[Notice] Fan {fan['name']} is unhappy with the team's performance.")
                    input(f"Press Enter to remove {fan['name']} from your fan base.")
                    flag_removal.append(fan_id)

        for fan_id in flag_removal:
            self.fans.remove(fan_id)

        self.clear_console()
        self.display_stadium()

        ready_to_proceed = False

        while not ready_to_proceed:
            print(f"\n--- Fan Engagement for Year {self.year_number} ---")
            print("Choose an activity to improve fan engagement:")
            print("1. Add fans")
            print("2. Increase loyalty of fans")
            print("3. Display stadium details")
            print("4. Change stadium")
            print("5. Exit Fan Engagement")

            choice = input("Enter your choice (1-5): ").strip() if not self.debug_mode else '5'
            if choice == '1':
                if performance_rating < 0:
                    print("You have no more performance points.")
                    input("\nPress Enter to continue...")
                    continue
                self.add_fans()
                performance_rating -= 1
            elif choice == '2':
                if performance_rating < 0:
                    print("You have no more performance points.")
                    input("\nPress Enter to continue...")
                    continue
                self.upgrade_fans()
                performance_rating -= 1
            elif choice == '3':
                self.display_stadium()
            elif choice == '4':
                self.change_stadium()
            elif choice == '5':
                ready_to_proceed = True
            else:
                print("Invalid choice, please try again.")

    def clear_console(self):
        """Clear the console for better readability."""
        os.system('cls' if os.name == 'nt' else 'clear')

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
        
        print(f"\nCurrent Team Cost: ${team_cost} and Salary Cap: ${self.salary_cap}")
        print("\nEnter the number(s) of the player(s) you want to cut (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= len(self.user_team_players)}

        if not selected_indices:
            print("[Notice] No valid player IDs selected.")
            return team_cost
        for pid in selected_indices:
            pid = self.user_team_players[pid - 1]  # Convert to actual player
            self.user_team_players.remove(pid)
            team_cost = self.display_team_roster(display_attribute=False)
            return team_cost

    def player_name_exists(self, player_name): 
        """Check if a player_name exists in user_team_players."""
        return any(player.get('player_name') == player_name for player in self.user_team_players)

    def add_players(self):
        """Command-line prompt to add players from simulation."""        
        self.cut_players()

        team_cost = self.display_team_roster() or 0  # Step 1: Show team before selection

        # Only show players not already on the team and greater than 0 salary
        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players and int(p.get('salary', 0)) > 0]

        if len(eligible_players) < self.players_per_free_agency:
            print("[Notice] Not enough eligible players to show 3 choices.")
            return

        options = random.sample(eligible_players, k=self.players_per_free_agency)

        self.clear_console()
        print("\n🎯 Choose a player to add to your team:")
        for idx, player in enumerate(options, start=1):
            print(f"\nPlayer {idx}:")
            for key, value in player.items():
                print(f"  {key}: {value}")

        print("\nEnter the number(s) of the player(s) you want to add (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= self.players_per_free_agency}

        for i in selected_indices:
            player_id = options[i - 1]['player_name']
            if not self.player_name_exists(player_id):
                if team_cost + int(options[i - 1].get('salary', 0)) > self.salary_cap:
                    print(f"[Skipped] Adding {player_id} would exceed salary cap.")
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
        self.sim_stats['cash'] += (self.salary_cap - team_cost)

    def add_strategies(self):
        self.display_strategies()

        eligible_strategies = [t for tid, t in self.simulation.strategies.items() if tid not in self.strategies]

        if len(eligible_strategies) < self.strategies_per_offseason:
            print("[Notice] Not enough eligible strategies.")
            return

        options = random.sample(eligible_strategies, k=self.strategies_per_offseason)

        self.clear_console()
        print("\n🎯 Choose a strategy to add to your team:")
        for idx, strategy in enumerate(options, start=1):
            print(f"\Strategy {idx}:")
            for key, value in strategy.items():
                print(f"  {key}: {value}")

        print("\nEnter the number(s) of the strategies you want to add (e.g. 1 or 1,3):")
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
        
        # Compute win percentage
        total_games = self.weeks_per_year
        win_pct = self.wins / total_games if total_games else 0

        # Determine draft eligibility based on win percentage
        if win_pct > self.draft_threshold:
            print("[Draft Eligibility] You are not eligible to draft players.")
            input("\nPress Enter to continue...")
            return
        
        print("[Draft Eligibility] You are eligible to draft players.")
        self.display_team_roster()
        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players and int(p.get('salary', 0)) == 0]
        if not eligible_players:
            print("[Notice] No eligible players available for drafting.")
            input("\nPress Enter to continue...")
            return
        
        options = random.sample(eligible_players, k=min(self.players_per_draft, len(eligible_players)))

        print("\n🎯 Choose a player to draft:")
        for idx, player in enumerate(options, start=1):
            print(f"\nPlayer {idx}:")
            for key, value in player.items():
                print(f"  {key}: {value}")

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
        if len(self.sponsors) >= self.max_sponsors:
            return

        self.clear_console()
        print(f"\n--- Sponsor Management for Year {self.year_number} ---")
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