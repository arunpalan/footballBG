import random
import os 

class Week:
    def __init__(self, week_number, simulation, user_team_players, opponents, strategies, tactics_per_week, debug_mode=False):
        self.week_number = week_number
        self.simulation = simulation
        self.user_team_players = user_team_players
        self.opponents = opponents
        self.strategies = strategies
        self.tactics_per_week = tactics_per_week
        self.debug_mode = debug_mode

        self.selected_strategy = None
        self.tactics = []

    def run_events(self):
        print(f"Running events for Week {self.week_number}...")
        self.gameplan()
        win = self.play()
        return win

    def display_team_roster(self, display_attribute=True):

        if not self.user_team_players:
            return None
        
        self.clear_console()

        print("\n📋 Your Team Roster:")
        for team_player in self.user_team_players:
            pid = team_player.get('player_name')
            player = self.simulation.players.get(pid)
            if player:
                attrs = ', '.join(f"{key}: {value}" for key, value in player.items())
                print(f"Player: {attrs}")
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
            attrs = ', '.join(f"{attr}: {value}" for attr, value in offense_sums.items())
            print(f"Offense Attribute Sums: {attrs}")
            attrs = ', '.join(f"{attr}: {value}" for attr, value in defense_sums.items())
            print(f"Defense Attribute Sums: {attrs}")

        input("\nPress Enter to continue...")

        return total_salary

    def display_next_opponent(self):
        if not self.opponents:
            return
        
        print("\nNext opponent:")
        opponent = self.opponents[self.week_number]['team']
        print(', '.join(f"{key}: {value}" for key, value in opponent.items()))

    def display_strategies(self):
        if not self.strategies:
            return

        print("\n📋 Your Current Strategies:")
        for tid in self.strategies:
            strategy = self.simulation.strategy.get(tid)
            if strategy:
                print(f"\Strategy ID: {tid}")
                for key, value in strategy.items():
                    print(f"  {key}: {value}")
            else:
                print(f"⚠️ Strategy ID {tid} not found in simulation database.")

    def select_strategy(self):

        if len(self.strategies) < 2:
            self.selected_strategy = self.strategies[0]
            return
        
        print("\nSelect an offensive strategy: ")

        for idx, tid in enumerate(self.strategies, start=1):
            print(f"\Strategy {idx}:")
            strategy = self.simulation.strategies.get(tid)
            for key, value in strategy.items():
                print(f"  {key}: {value}")

        print("\nEnter the number next to the strategy you would like to select: ")
        choice = input(">> ").strip()
        
        self.selected_strategy = self.strategies[int(choice)-1]

    def select_tactics(self):
        if self.tactics_per_week < 1:
            return
        
        eligible_tactics = [t for t in self.simulation.tactics]
        options = random.sample(eligible_tactics, k=min(self.tactics_per_week, len(eligible_tactics)))

        for i, tactic_id in enumerate(options, start=1):
            tactic = self.simulation.tactics.get(tactic_id)
            attr = ', '.join(f"{key}: {value}" for key, value in tactic.items())
            print(f"{i}: {attr}")

        choice = input("Enter the number of the tactic to use: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            self.tactics.append(options[int(choice) - 1])

    def gameplan(self):
        self.display_next_opponent()

        if self.debug_mode:
            self.selected_strategy = 'strat1'
            return
        
        self.select_tactics()
        self.select_strategy()

    def play(self):
        if self.debug_mode:
            print("Debug mode: Simulating a loss for testing purposes.")
            self.opponents[self.week_number]['result'] = "L 30-20"
            return 0
        
        strategy = self.simulation.strategies.get(self.selected_strategy)
        off_arch = strategy['arch']
        opponent = self.opponents[self.week_number]['team']
        def_arch = opponent['arch']

        off_rat = int(strategy['bonus'])
        def_rat = 0

        for tactic_id in self.tactics:
            tactic = self.simulation.tactics.get(tactic_id)
            if tactic['type'] == 'defense':
                if tactic['arch'] == def_arch or tactic['arch'] == 'any':
                    def_rat += int(tactic['bonus'])
            if tactic['type'] == 'offense':
                if tactic['arch'] == off_arch or tactic['arch'] == 'any':
                    off_rat += int(tactic['bonus'])

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
            clutch = 0
            clutch += int(strategy['clutch'])

            for tactic_id in self.tactics:
                tactic = self.simulation.tactics.get(tactic_id)
                clutch += int(tactic['clutch'])

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
            clutch += int(strategy['clutch'])
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