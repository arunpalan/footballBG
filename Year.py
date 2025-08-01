import random
from Week import Week
import os

class Year:
    def __init__(self, year_number, simulation, user_team_players, weeks_per_year, sim_stats, salary_cap):
        self.year_number = year_number
        self.simulation = simulation
        self.user_team_players = user_team_players
        self.weeks_per_year = weeks_per_year
        self.sim_stats = sim_stats
        self.salary_cap = salary_cap
        self.players_per_free_agency = 3
        self.tactics_per_offseason = 5

        self.week_number = 1
        self.wins = 0
        self.playoff_wins = None
        self.current_week = None
        self.opponents = {}
        self.playoff_bracket = {}
        self.tactics = []

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
            print("2. View Tactics")
            print("3. View Schedule")
            print("4. Play Match")
            choice = input("Enter your choice (1-4): ").strip()
            if choice == '1':
                self.display_team_roster()  
            elif choice == '2':
                self.display_tactics()
            elif choice == '3':
                self.view_schedule()
            elif choice == '4':
                self.current_week = Week(self.week_number, self.simulation, self.user_team_players, self.opponents, self.tactics)
                win = self.current_week.run_events()
                self.wins += win
                self.week_number += 1

                input("\nPress Enter to continue to the next week...")

    def handle_offseason(self):
        """Handle offseason activities like adding players and tactics."""
        added_players = False
        added_tactics = False
        ready_to_proceed = False
        self.schedule_matches()

        while not ready_to_proceed:
            self.clear_console()
            print(f"\n--- Offseason Activities for Year {self.year_number} ---")
            print("\nChoose an offseason activity:")
            print("1. Add Players")
            print("2. Add Tactics")
            print("3. View Team Roster")
            print("4. View Tactics")
            print("5. View Schedule")
            print("6. Exit Offseason")

            choice = input("Enter your choice (1-6): ").strip()
            if choice == '1':
                if not added_players:
                    added_players = True
                    self.add_players()
                else:
                    print("You have already added players this offseason.")
                
            elif choice == '2':
                if not added_tactics:
                    added_tactics = True
                    self.add_tactics()
                else:
                    print("You have already added tactics this offseason.")

            elif choice == '3':
                self.display_team_roster()
            elif choice == '4':
                self.display_tactics()
            elif choice == '5':
                self.view_schedule()
            elif choice == '6':
                ready_to_proceed = True
            else:
                print("Invalid choice, please try again.")

    def handle_playoffs(self):
        """Handle NFL-like 12-team playoff bracket."""
        self.clear_console()
        print(f"\n--- Playoff Activities for Year {self.year_number} ---")

        total_games = self.weeks_per_year
        win_pct = self.wins / total_games if total_games else 0
        made_playoffs = win_pct >= 0.55  # Example threshold for playoffs

        if not made_playoffs:
            print("Your team did not qualify for the playoffs this year.")
            input("\nPress Enter to continue...")
            return
        
        has_bye = win_pct >= 0.75
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
            print("2. View Tactics")
            print("3. View Playoff Bracket")
            print("4. Play Playoff Game")
            choice = input("Enter your choice (1-4): ").strip()
            if choice == '1':
                self.display_team_roster()
            elif choice == '2':
                self.display_tactics()
            elif choice == '3':
                view_playoff_bracket()
            elif choice == '4':
                # Simulate a playoff game
                # You can customize opponent logic as needed
                print("\nPlaying playoff game...")

                self.current_week = Week(playoff_round, self.simulation, self.user_team_players, self.playoff_bracket, self.tactics)
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
        self.clear_console()
        """Show current players on your team with their attributes."""
        if not self.user_team_players:
            print("\n📭 Your team has no players yet.")
            input("\nPress Enter to continue...")
            return 0

        print("\n📋 Your Team Roster:")
        for team_player in self.user_team_players:
            pid = team_player.get('player_name')
            player = self.simulation.players.get(pid)
            if player:
                print(f"\nPlayer ID: {pid}")
                for key, value in player.items():
                    print(f"  {key}: {value}")
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

    def display_tactics(self):
        self.clear_console()
        if not self.tactics:
            print("\n📭 You have no tactics yet.")
            input("\nPress Enter to continue...")
            return

        print("\n📋 Your Current Tactics:")
        for tid in self.tactics:
            tactic = self.simulation.tactics.get(tid)
            if tactic:
                print(f"\Tactic ID: {tid}")
                for key, value in tactic.items():
                    print(f"  {key}: {value}")
            else:
                print(f"⚠️ Tactic ID {tid} not found in simulation database.")

        input("\nPress Enter to continue...")

    def cut_players(self):
        """Command-line prompt to cut players from your team."""
        team_cost = self.display_team_roster(display_attribute=False)

        if not self.user_team_players:
            print("[Notice] Your team has no players to cut.")
            return 
        
        print(f"\nCurrent Team Cost: ${team_cost} and Salary Cap: ${self.salary_cap}")
        print("\nEnter the number(s) of the player(s) you want to cut (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= len(self.user_team_players)}

        if not selected_indices:
            print("[Notice] No valid player IDs selected.")
            return
        for pid in selected_indices:
            pid = self.user_team_players[pid - 1]  # Convert to actual player
            self.user_team_players.remove(pid)

    def player_name_exists(self, player_name): 
        """Check if a player_name exists in user_team_players."""
        return any(player.get('player_name') == player_name for player in self.user_team_players)

    def add_players(self):
        """Command-line prompt to add players from simulation."""        
        self.cut_players()

        team_cost = self.display_team_roster()  # Step 1: Show team before selection
        eligible_players = [p for pid, p in self.simulation.players.items() if pid not in self.user_team_players]

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

        team_cost = self.display_team_roster()  # Step 2: Show team after updates
        self.sim_stats['cash'] += (self.salary_cap - team_cost)

    def add_tactics(self):
        self.display_tactics()

        eligible_tactics = [t for tid, t in self.simulation.tactics.items() if tid not in self.tactics]

        if len(eligible_tactics) < self.tactics_per_offseason:
            print("[Notice] Not enough eligible tactics to show 3 choices.")
            return

        options = random.sample(eligible_tactics, k=self.tactics_per_offseason)

        self.clear_console()
        print("\n🎯 Choose a tactic to add to your team:")
        for idx, tactic in enumerate(options, start=1):
            print(f"\Tactic {idx}:")
            for key, value in tactic.items():
                print(f"  {key}: {value}")

        print("\nEnter the number(s) of the tactic(s) you want to add (e.g. 1 or 1,3):")
        choice = input(">> ").strip()
        selected_indices = {int(i) for i in choice.split(",") if i.isdigit() and 1 <= int(i) <= self.tactics_per_offseason}

        for i in selected_indices:
            tactic_id = options[i - 1]['tactic_name']
            if tactic_id not in self.tactics:
                self.tactics.append(tactic_id)
                print(f"[Added] Tactic {tactic_id} to your team!")
            else:
                print(f"[Skipped] Tactic {tactic_id} is already on your team.")

        self.display_tactics()  # Step 2: Show team after updates