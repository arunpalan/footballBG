import random
import os 

class Week:
    def __init__(self, week_number, simulation, user_team_players, opponents, tactics, debug_mode=False):
        self.week_number = week_number
        self.simulation = simulation
        self.user_team_players = user_team_players
        self.opponents = opponents
        self.tactics = tactics
        self.debug_mode = debug_mode

        self.off_strategy = None
        self.def_strategy = None
        self.off_tactics = []
        self.def_tactics = []

    def run_events(self):
        print(f"Running events for Week {self.week_number}...")
        self.gameplan()
        win = self.play()
        return win

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

    def display_next_opponent(self):
        if not self.opponents:
            return
        
        print("\n Next opponent:")
        opponent = self.opponents[self.week_number]['team']
        print(f"\nOpponent name: {opponent['team_name']}")
        for key, value in opponent.items():
            print(f"  {key}: {value}")

    def display_tactics(self):
        if not self.tactics:
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

    def gameplan(self):
        self.display_next_opponent()

        if self.debug_mode:
            self.off_strategy = 'strat1'
            self.def_strategy = 'defstrat1'
            self.off_tactics = []
            self.def_tactics = []
            return

        tactic_selected = False

        while not tactic_selected:
            self.off_strategy = None
            self.def_strategy = None
            self.off_tactics = []
            self.def_tactics = []

            self.clear_console()
            print("\nSelect an offensive strategy: ")

            for idx, tid in enumerate(self.tactics, start=1):
                print(f"\Tactic {idx}:")
                tactic = self.simulation.tactics.get(tid)
                for key, value in tactic.items():
                    print(f"  {key}: {value}")

            print("\nEnter the number next to the strategy you would like to select: ")
            choice = input(">> ").strip()

            chosen_tactic = self.simulation.tactics.get(self.tactics[int(choice)-1])
            if chosen_tactic['side'] != 'offense':
                print("\nDefensive strategy selected, try again")
                continue
            if chosen_tactic['type'] != 'strategy':
                print("\nTactic selected instead of strategy, try again")

            self.off_strategy = self.tactics[int(choice)-1]

            self.clear_console()
            print("\nSelect a defensive strategy: ")

            for idx, tid in enumerate(self.tactics, start=1):
                print(f"\Tactic {idx}:")
                tactic = self.simulation.tactics.get(tid)
                for key, value in tactic.items():
                    print(f"  {key}: {value}")

            print("\nEnter the number next to the strategy you would like to select: ")
            choice = input(">> ").strip()

            chosen_tactic = self.simulation.tactics.get(self.tactics[int(choice)-1])
            if chosen_tactic['side'] != 'defense':
                print("\Offensive strategy selected, try again")
                continue
            if chosen_tactic['type'] != 'strategy':
                print("\nTactic selected instead of strategy, try again")

            self.def_strategy = self.tactics[int(choice)-1]
            
            self.clear_console()
            print("\nSelect any offensive tactics: ")

            for idx, tid in enumerate(self.tactics, start=1):
                print(f"\Tactic {idx}:")
                tactic = self.simulation.tactics.get(tid)
                for key, value in tactic.items():
                    print(f"  {key}: {value}")

            print("\nEnter the number(s) next to the strategy you would like to select (e.g. 1 or 1,3): ")
            choice = input(">> ").strip()
            selected_indices = {int(i) for i in choice.split(",") if i.isdigit()}

            for i in selected_indices:
                chosen_tactic = self.simulation.tactics.get(self.tactics[i-1])
                if chosen_tactic['side'] == 'offense' and chosen_tactic['type'] == 'tactic':
                    self.off_tactics.append(self.tactics[i-1])

            self.clear_console()
            print("\nSelect any defensive tactics: ")

            for idx, tid in enumerate(self.tactics, start=1):
                print(f"\Tactic {idx}:")
                tactic = self.simulation.tactics.get(tid)
                for key, value in tactic.items():
                    print(f"  {key}: {value}")

            print("\nEnter the number(s) next to the strategy you would like to select (e.g. 1 or 1,3): ")
            choice = input(">> ").strip()
            selected_indices = {int(i) for i in choice.split(",") if i.isdigit()}

            for i in selected_indices:
                chosen_tactic = self.simulation.tactics.get(self.tactics[i-1])
                if chosen_tactic['side'] == 'defense' and chosen_tactic['type'] == 'tactic':
                    self.def_tactics.append(self.tactics[i-1])

            tactic_selected = True

    def play(self):
        if self.debug_mode:
            print("Debug mode: Simulating a loss for testing purposes.")
            self.opponents[self.week_number]['result'] = "L 30-20"
            return 0
        
        off_tactic = self.simulation.tactics.get(self.off_strategy)
        def_tactic = self.simulation.tactics.get(self.def_strategy)
        off_arch = off_tactic['arch']
        opponent = self.opponents[self.week_number]['team']
        def_arch = opponent['arch']

        off_rat = int(off_tactic['bonus'])
        def_rat = int(def_tactic['bonus'])

        for tid in self.off_tactics:
            tactic = self.simulation.tactics.get(tid)
            if tactic['side'] == 'offense' and tactic['arch'] == off_arch:
                off_rat += int(tactic['bonus'])
            elif tactic['side'] == 'defense' and tactic['arch'] == def_arch:
                def_rat += int(tactic['bonus'])

        for team_player in self.user_team_players:
            pid = team_player.get('player_name')
            player = self.simulation.players.get(pid)
            if player['side'] == 'offense':
                off_rat += int(player[off_arch])
            if player['side'] == 'defense':
                def_rat += int(player[def_arch])

        opp_off = int(opponent['off'])
        opp_def = int(opponent[off_arch])

        if off_rat == opp_def and def_rat == opp_off:
            clutch = 1
            clutch += int(off_tactic['clutch'])
            clutch += int(def_tactic['clutch'])
            for team_player in self.user_team_players:
                pid = team_player.get('player_name')
                player = self.simulation.players.get(pid)
                clutch += int(player['clutch'])

            user_roll = sum([random.randint(1,6) for _ in range(clutch)])
            opp_roll = sum([random.randint(1,6) for _ in range(int(opponent['clutch']))])

            if user_roll > opp_roll:
                user_score = random.randint(25, 50)
                opponent_score = random.randint(user_score - 7, user_score - 1)
                print(f"You won {user_score} to {opponent_score}!")
                self.opponents[self.week_number]['result'] = f"W {user_score}-{opponent_score}"
                return 1
            else:
                opponent_score = random.randint(25, 50)
                user_score = random.randint(opponent_score - 7, opponent_score - 1)
                print(f"You lost {opponent_score} to {user_score}!")
                self.opponents[self.week_number]['result'] = f"L {opponent_score}-{user_score}"
                return 0

        if off_rat >= opp_def and def_rat >= opp_off:
            user_score = random.randint(25, 50)
            opponent_score = random.randint(0, user_score - 7)
            print(f"You won {user_score} to {opponent_score}!")
            self.opponents[self.week_number]['result'] = f"W {user_score}-{opponent_score}"
            return 1
        elif opp_def >= off_rat and opp_off >= def_rat:
            opponent_score = random.randint(25, 50)
            user_score = random.randint(0, opponent_score - 7)   
            print(f"You lost {opponent_score} to {user_score}!")
            self.opponents[self.week_number]['result'] = f"L {opponent_score}-{user_score}"
            return 0
        else:
            clutch = 1
            clutch += int(off_tactic['clutch'])
            clutch += int(def_tactic['clutch'])
            for team_player in self.user_team_players:
                pid = team_player.get('player_name')
                player = self.simulation.players.get(pid)
                clutch += int(player['clutch'])

            user_roll = sum([random.randint(1,6) for _ in range(clutch)])
            opp_roll = sum([random.randint(1,6) for _ in range(int(opponent['clutch']))])

            if user_roll > opp_roll:
                user_score = random.randint(25, 50)
                opponent_score = random.randint(user_score - 7, user_score - 1)
                print(f"You won {user_score} to {opponent_score}!")
                self.opponents[self.week_number]['result'] = f"W {user_score}-{opponent_score}"
                return 1
            else:
                opponent_score = random.randint(25, 50)
                user_score = random.randint(opponent_score - 7, opponent_score - 1)
                print(f"You lost {opponent_score} to {user_score}!")
                self.opponents[self.week_number]['result'] = f"L {opponent_score}-{user_score}"
                return 0

    def clear_console(self):
        """Clear the console for a fresh display."""
        os.system('cls' if os.name == 'nt' else 'clear')