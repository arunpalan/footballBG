from Year import Year
from Simulation import Simulation
import os

class Engine:
    def __init__(self):
        self.simulation = Simulation()
        self.simulation.initialize_simulation()
        
        self.year_number = 1
        self.weeks_per_year = 10
        self.salary_cap = 20
        self.debug_mode = False
        self.user_team_players = []  # This could be player IDs or full player dicts
        self.stadium = 'stadium1'  # Default stadium, can be changed later
        self.coaches = ['Base Coach']
        self.staffers = []
        self.sponsors = []
        self.fans = []
        self.sim_stats = {
            'tokens': 0,
            'sb_wins': 0,
            'mvps': 0,
            'yearly_results': []
        }
        self.current_year = None

    def compute_score(self):
        """Compute the score based on simulation statistics."""
        score = (self.sim_stats['sb_wins'] * 5) + (self.sim_stats['mvps'])
        return score

    def print_simulation_stats(self):
        """Print the current simulation statistics."""
        self.clear_console()
        print("\nSimulation Statistics:")
        print(f"Current Year: {self.year_number}")
        print(f"Simulation Score: {self.compute_score()}")
        print(f"Stashed Tokens: ${self.sim_stats['tokens']}")
        print(f"Super Bowl Wins: {self.sim_stats['sb_wins']}")
        print(f"Most Valuable Players: {self.sim_stats['mvps']}")
        print("Yearly Results:")
        for result in self.sim_stats['yearly_results']:
            print(f"Year {result['year']}: {result['wins']}-{result['losses']}, Playoff Wins: {result['playoff_wins']}")
        input("\nPress Enter to continue...")

    def run(self, total_years=10):
        """Run the simulation for a specified number of years."""
        while self.year_number <= total_years:
            print(f"\n--- Year {self.year_number} ---")
            self.current_year = Year(self.year_number, self.simulation, self.user_team_players, self.weeks_per_year, self.sim_stats, self.salary_cap, self.stadium, self.fans, self.coaches, self.staffers, self.sponsors, self.debug_mode)
            self.current_year.run_events()

            self.year_number += 1
            self.print_simulation_stats()

    def clear_console(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

engine = Engine()
engine.run()