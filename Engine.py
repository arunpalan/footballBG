from Year import Year
from Simulation import Simulation

class Engine:
    def __init__(self):
        self.simulation = Simulation()
        self.simulation.initialize_simulation()
        
        self.year_number = 1
        self.weeks_per_year = 10
        self.user_team_players = []  # This could be player IDs or full player dicts
        self.current_year = None

    def run(self, total_years=10):
        """Run the simulation for a specified number of years."""
        while self.year_number <= total_years:
            print(f"\n--- Year {self.year_number} ---")
            self.current_year = Year(self.year_number, self.simulation, self.user_team_players, self.weeks_per_year)
            self.current_year.run_events()

            self.year_number += 1

engine = Engine()
engine.run()