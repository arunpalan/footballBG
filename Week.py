import random
import os 

class Week:
    def __init__(self, week_number, simulation, user_team_players, opponents, tactics):
        self.week_number = week_number
        self.simulation = simulation
        self.user_team_players = user_team_players
        self.opponents = opponents
        self.tactics = tactics

        self.off_strategy = None
        self.def_strategy = None
        self.off_tactics = []
        self.def_tactics = []

    def run_events(self):
        print(f"Running events for Week {self.week_number}...")
        self.gameplan()
        win = self.play()
        return win

    def display_team_roster(self):
        """Show current players on your team with their attributes."""
        if not self.user_team_players:
            print("\n📭 Your team has no players yet.")
            return

        print("\n📋 Your Current Team:")
        for pid in self.user_team_players:
            player = self.simulation.players.get(pid)
            if player:
                print(f"\nPlayer Name: {pid}")
                for key, value in player.items():
                    print(f"  {key}: {value}")
            else:
                print(f"⚠️ Player Name {pid} not found in simulation database.")

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

        for pid in self.user_team_players:
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
            for pid in self.user_team_players:
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
            for pid in self.user_team_players:
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