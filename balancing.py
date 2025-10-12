    # def initialize_simulation(self):
    #     """Load all glossary data from CSV files."""
    #     self.teams = self.load_csv_data('teams.csv', key_field='team_id')
    #     self.players = self.load_csv_data('players.csv', key_field='player_name')
    #     self.coaches = self.load_csv_data('coaches.csv', key_field='name')
    #     self.fans = self.load_csv_data('fans.csv', key_field='name')
    #     self.tactics = self.load_csv_data('tactics.csv', key_field='name')
    #     self.stadiums = self.load_csv_data('stadiums.csv', key_field='name')
    #     self.strategies = self.load_csv_data('strategies.csv', key_field='name')
    #     self.sponsors = self.load_csv_data('sponsors.csv', key_field='company')
        
import numpy as np
import csv
from math import comb

def load_csv_data(filepath, key_field):
    """General method to load CSV data into a dictionary keyed by 'key_field'."""
    data = {}
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = row[key_field]
                data[key] = row
    except FileNotFoundError:
        print(f"[Error] File not found: {filepath}")
    return data
        
def win_pct_d6(x, y):
    if x == y:
        return 0.5
    if y < 1:
        return 1.0
    if x < 1:
        return 0.0
    
    d6 = np.ones(6) / 6.0

    # Convolve to get distribution for x and y dice
    px = d6
    for _ in range(x - 1):
        px = np.convolve(px, d6)
    py = d6
    for _ in range(y - 1):
        py = np.convolve(py, d6)

    # The possible sums
    min_sum_x, max_sum_x = x, 6 * x
    min_sum_y, max_sum_y = y, 6 * y

    # Pad distributions so their indices match their possible sums
    px_full = np.zeros(max_sum_x + 1)
    py_full = np.zeros(max_sum_y + 1)
    px_full[min_sum_x:max_sum_x + 1] = px
    py_full[min_sum_y:max_sum_y + 1] = py

    # Compute probability that sum_x > sum_y
    prob = 0.0
    for sx in range(min_sum_x, max_sum_x + 1):
        for sy in range(min_sum_y, min(sx,max_sum_y+1)):
            prob += px_full[sx] * py_full[sy]
        if sx <= max_sum_y:
            prob += 0.5 * px_full[sx] * py_full[sx]
    return prob
        
def balance():
    teams = load_csv_data('teams.csv', key_field='team_id')
    
    team_strength = []
    
    choices = input("Enter Mock team strength as Offense rating, Def Power Run, Def Spread, Def West Coast, Def Verticals, then Clutch: \n").strip()
    if choices:
        indices = choices.split(',')
        for index in indices:
            team_strength.append(int(index.strip()))
            
    off_arch = input("Enter strategy (power run, west coast, spread, vertical): \n").strip()
            
    winPct = []
    winPct1 = []
    winPct2 = []
    winPct3 = []
    winPct4 = []
    winPct5 = []
            
    for team in teams.values():
        def_arch = team['arch']
        if def_arch == 'power run':
            def_rat = team_strength[1]
        elif def_arch == 'spread':
            def_rat = team_strength[2]
        elif def_arch == 'west coast':
            def_rat = team_strength[3]
        elif def_arch == 'vertical':    
            def_rat = team_strength[4]

        quality = int(team['quality'])
        clutch = team_strength[5]
        opp_clutch = int(team['clutch'])

        off_rat = team_strength[0]
        
        opp_off_rat = int(team['off'])
        opp_def_rat = int(team[off_arch])

        if off_rat == opp_def_rat and def_rat == opp_off_rat:
            win = win_pct_d6(clutch, opp_clutch)
        elif off_rat >= opp_def_rat and def_rat >= opp_off_rat:
            win = 1.0
        elif off_rat <= opp_def_rat and def_rat <= opp_off_rat:
            win = 0.0
        else:
            win = win_pct_d6(clutch, opp_clutch)
            
        winPct.append(win)
        if quality == 1:
            winPct1.append(win)
        elif quality == 2:
            winPct2.append(win)
        elif quality == 3:
            winPct3.append(win)
        elif quality == 4:
            winPct4.append(win)
        elif quality == 5:
            winPct5.append(win)
            
    print(f"Overall Win Pct: {100*np.mean(winPct):.3f}%")
    print(f"Quality 1 Win Pct: {100*np.mean(winPct1):.3f}%")
    print(f"Quality 2 Win Pct: {100*np.mean(winPct2):.3f}%")
    print(f"Quality 3 Win Pct: {100*np.mean(winPct3):.3f}%")
    print(f"Quality 4 Win Pct: {100*np.mean(winPct4):.3f}%")
    print(f"Quality 5 Win Pct: {100*np.mean(winPct5):.3f}%")
    
    # Calculate how likely to make playoffs
    required_wins = 4
    total_games = 10
    prob_make_playoffs = 0.0
    for wins in range(required_wins, total_games + 1):
        prob_make_playoffs += comb(total_games, wins) * (np.mean(winPct) ** wins) * ((1 - np.mean(winPct)) ** (total_games - wins))
        
    print(f"Probability of making playoffs (at least {required_wins} wins): {100*prob_make_playoffs:.3f}%")
    
balance()