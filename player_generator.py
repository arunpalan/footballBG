import random

class playerGenerator:
    def __init__(self):
        self.off_totals = [1, 3, 6, 9, 12]
        self.off_zero_weights = [5, 4, 3, 2, 1]
        self.def_totals = [3, 6, 9, 12, 15]
        self.def_zero_weights = [9, 7, 5, 3, 1]
        self.dev_zero_weights = [1, 3, 5, 7, 9]
        self.qualities = [5]*40 + [4]*80 + [3]*100 + [2]*100 + [1]*80
        # Expanded first names (160)
        self.first_names = [
            "Aaron", "Tom", "Patrick", "Josh", "Justin", "Lamar", "Dak", "Russell", "Matthew", "Derrick",
            "Saquon", "Nick", "Christian", "Alvin", "Dalvin", "Tyreek", "Davante", "Stefon", "DeAndre", "Cooper",
            "Travis", "George", "Mark", "Darren", "Kyle", "Micah", "T.J.", "Jalen", "Myles", "Joey",
            "Jaire", "Xavien", "Jamal", "Derwin", "Budda", "Harrison", "Fred", "Bobby", "Darius", "Roquan",
            "Deshaun", "Baker", "Kirk", "Ryan", "Jared", "Carson", "Jimmy", "Tua", "Mac", "Zach",
            "Daniel", "Taylor", "Teddy", "Andy", "Joe", "Sam", "Cam", "Marcus", "Gardner", "Drew",
            "Ezekiel", "Leonard", "James", "Melvin", "Phillip", "Latavius", "Sony", "Kareem", "Chris", "Aaron",
            "A.J.", "Allen", "Antonio", "Brandin", "Calvin", "Courtland", "D.J.", "Deebo", "Emmanuel", "Jarvis",
            "Jerry", "JuJu", "Keenan", "Marquise", "Michael", "Odell", "Robby", "Sammy", "Sterling", "Terry",
            "Tyler", "Will", "Zay", "Adam", "Allen", "Amari", "Brandon", "Chase", "Corey", "Curtis",
            "DeVante", "Diontae", "DK", "Elijah", "Gabriel", "Hunter", "Jakobi", "Jamison", "Jarvis", "Jaylen",
            "John", "Josh", "Kenny", "Laviska", "Marvin", "Michael", "Nelson", "Parris", "Preston", "Randall",
            "Rashard", "Russell", "Scotty", "Tim", "Trent", "Tyrell", "Van", "Zach", "Alex", "Ben",
            "Blake", "Brett", "Bryce", "Chad", "Charlie", "Chase", "Chris", "Cody", "Colt", "Cooper",
            "Craig", "Dan", "Danny", "David", "Doug", "Dwayne", "Eric", "Frank", "Gary", "Gene",
            "Gus", "Jack", "Jake", "Jeff", "Jerry", "Jim", "Joe", "John", "Jon", "Jordan"
        ]
        # Expanded last names (160)
        self.last_names = [
            "Rodgers", "Brady", "Mahomes", "Allen", "Herbert", "Jackson", "Prescott", "Wilson", "Stafford", "Henry",
            "Barkley", "Chubb", "McCaffrey", "Kamara", "Cook", "Hill", "Adams", "Diggs", "Hopkins", "Kupp",
            "Kelce", "Kittle", "Andrews", "Waller", "Pitts", "Parsons", "Watt", "Ramsey", "Garrett", "Bosa",
            "Alexander", "Howard", "Adams", "James", "Baker", "Smith", "Warner", "Wagner", "Leonard", "Smith",
            "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Moore", "Taylor", "Thomas", "White",
            "Harris", "Martin", "Thompson", "Young", "Clark", "Lewis", "Walker", "Hall", "Allen", "King",
            "Wright", "Scott", "Green", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner",
            "Phillips", "Campbell", "Parker", "EvANS", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers",
            "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox",
            "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly",
            "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", "Perry",
            "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzalez",
            "Bryant", "Alexander", "Russell", "Griffin", "Diaz", "Hayes", "Myers", "Ford", "Hamilton", "Graham",
            "Sullivan", "Wallace", "Woods", "Cole", "West", "Jordan", "Owens", "Reynolds", "Fisher", "Ellis",
            "Harrison", "Gibson", "McDonald", "Cruz", "Marshall", "Ortiz", "Gomez", "Murray", "Freeman", "Wells",
            "Webb", "Simpson", "Stevens", "Tucker", "Porter", "Hunter", "Hicks", "Crawford", "Henry", "Boyd"
        ]
        self.used_names = set()
        
    def generate_ratings(self, quality, side='offense'):
        if side == 'offense':
            total = self.off_totals[quality - 1]
            # Step 1: Assign negatives
            negs = [0, 0, 0, 0]
            neg_type = random.randint(0, 13)
            if neg_type >= 13:
                idx = random.randint(0, 3)
                negs[idx] = -2
            elif neg_type >= 12:
                idxs = random.sample(range(4), 2)
                for idx in idxs:
                    negs[idx] = -1
            elif neg_type >= 8:
                idx = random.randint(0, 3)
                negs[idx] = -1
            # Step 2: Assign largest archetype rating (must be >= 0)
            largest = random.randint(0, total)
            # Step 3: Assign other archetype ratings (must be >= 0 after negative)
            others = [0, 0, 0]
            remain = total - largest
            # Distribute remaining as half-points, so double for integer math
            remain_half = remain * 2
            for i in range(3):
                if i < 2:
                    val = random.randint(0, remain_half)
                    others[i] = val // 2
                    remain_half -= val
                else:
                    others[i] = remain_half // 2
            # Step 4: Assign clutch and dev (must be >= 0)
            clutch_choices = list(range(0, max(0, total // 2) + 1))
            clutch_weights = [self.off_zero_weights[quality - 1] if c == 0 else 1 for c in clutch_choices]
            clutch = random.choices(clutch_choices, weights=clutch_weights, k=1)[0]
            
            dev_choices = list(range(0, max(0, total // 2) + 1))
            dev_weights = [self.dev_zero_weights[quality - 1] if d == 0 else 1 for d in dev_choices]
            dev = random.choices(dev_choices, weights=dev_weights, k=1)[0]
            
            # Step 5: Apply negatives and sort
            archs = [largest] + others
            for i in range(4):
                archs[i] += negs[i]
            archs.sort(reverse=True)
            # Step 6: Adjust clutch/dev to fit sum constraint
            # Equation: (largest) + 0.5*(sum others) + clutch + 0.5*dev = total
            # Try to fit by adjusting dev
            eq_sum = archs[0] + 0.5 * sum(archs[1:]) + clutch + 0.5 * dev
            diff = total - eq_sum
            
            if diff < 0:
                archs[0] -= round(diff)
                archs[0] = max(-1, archs[0])
                archs.sort(reverse=True)
                if dev > 0:
                    dev = 0
                    
                eq_sum = archs[0] + 0.5 * sum(archs[1:]) + clutch + 0.5 * dev
                diff = total - eq_sum
            if diff > 2:
                archs[0] += round(diff)
                
                eq_sum = archs[0] + 0.5 * sum(archs[1:]) + clutch + 0.5 * dev
                diff = total - eq_sum
            
            dev += int(round(diff * 2))
            dev = max(0, dev)
            # Final output
            return archs + [clutch, dev]
        else:
            total = self.def_totals[quality - 1]
            # Step 1: Assign negatives
            negs = [0, 0, 0, 0]
            neg_type = random.randint(0, 17)
            if neg_type >= 17:
                idx = random.randint(0, 3)
                negs[idx] = -2
            elif neg_type >= 16:
                idxs = random.sample(range(4), 2)
                for idx in idxs:
                    negs[idx] = -1
            elif neg_type >= 12:
                idx = random.randint(0, 3)
                negs[idx] = -1
            # Step 2: Assign archetype ratings (must be >= 0 after negative)
            archs = [random.randint(0, total) for _ in range(4)]
            # Step 3: Assign clutch and dev (must be >= 0)
            clutch_choices = list(range(0, max(0, total // 3) + 1))
            clutch_weights = [self.def_zero_weights[quality - 1] if c == 0 else 1 for c in clutch_choices]
            clutch = random.choices(clutch_choices, weights=clutch_weights, k=1)[0]

            dev_choices = list(range(0, max(0, total // 3) + 1))
            dev_weights = [self.dev_zero_weights[quality - 1] if d == 0 else 1 for d in dev_choices]
            dev = random.choices(dev_choices, weights=dev_weights, k=1)[0]
            # Step 4: Apply negatives
            for i in range(4):
                archs[i] += negs[i]
            archs = [max(-2, a) for a in archs]
            archs.sort(reverse=True)
            # Step 5: Adjust to fit sum constraint
            # Equation: sum(archs) + 2*clutch + dev = total
            eq_sum = sum(archs) + 2 * clutch + dev
            diff = total - eq_sum
            
            if diff < 0:
                archs[0] += diff
                archs[0] = max(0, archs[0])
                archs.sort(reverse=True)
                if dev > 0:
                    dev = 0
                    
                eq_sum = sum(archs) + 2 * clutch + dev
                diff = total - eq_sum
                
                archs[0] += diff
                archs[0] = max(0, archs[0])
                archs.sort(reverse=True)
                
                eq_sum = sum(archs) + 2 * clutch + dev
                diff = total - eq_sum
            if diff > 2:
                archs[0] += diff
                
                eq_sum = sum(archs) + 2 * clutch + dev
                diff = total - eq_sum
            
            dev += diff
            dev = max(0, dev)
            # Final output
            return archs + [clutch, dev]
        
    def weighted_random_sort(self, numbers, weights):
        """
        Sorts four numbers into a random order, with weights influencing the chance
        of each number being placed in each position.
        - numbers: list of 4 numbers
        - weights: 4x4 matrix, weights[i][j] is the weight for numbers[i] being in position j
        Returns: list of numbers in the new order
        """
        nums = list(numbers)
        order = []
        available = list(range(4))
        for pos in range(4):
            # Get weights for available numbers for this position
            w = [weights[i][pos] for i in available]
            total = sum(w)
            if total == 0:
                # fallback to uniform
                w = [1] * len(available)
                total = sum(w)
            probs = [x / total for x in w]
            idx = random.choices(range(len(available)), weights=probs, k=1)[0]
            chosen = available.pop(idx)
            order.append(nums[chosen])
        return order
    
    def random_nfl_name(self):
        while True:
            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
    def generate_players(self):
        players = []
        positions = ['QB', 'RB', 'WR', 'OL', 'DL', 'LB', 'CB', 'S']

        for idx, q in enumerate(self.qualities):
            pos = random.choice(positions)
            if pos == 'QB' or pos == 'S':
                weights = [
                    [1, 1, 3, 3],
                    [1, 1, 3, 3], 
                    [3, 3, 1, 1],  
                    [3, 3, 1, 1],  
                ]
            elif pos == 'WR' or pos == 'CB':
                weights = [
                    [1, 1, 3, 3],
                    [3, 3, 1, 1], 
                    [3, 3, 1, 1],  
                    [1, 1, 3, 3],  
                ]
            elif pos == 'RB' or pos == 'LB':
                weights = [
                    [3, 3, 1, 1],
                    [3, 3, 1, 1], 
                    [1, 1, 3, 3],  
                    [1, 1, 3, 3],  
                ]
            elif pos == 'OL' or pos == 'DL':
                weights = [
                    [3, 3, 1, 1],
                    [1, 1, 3, 3], 
                    [1, 1, 3, 3],  
                    [3, 3, 1, 1],  
                ]

            if pos in ['QB', 'RB', 'WR', 'OL']:
                side = 'offense'
                rat = self.generate_ratings(q, side)
            else:
                side = 'defense'
                rat = self.generate_ratings(q, side)
                
            archs = self.weighted_random_sort(rat[0:4], weights)
            
            player = {
                #"player_id": idx + 1,
                "player_name": self.random_nfl_name(),
                "side": side,
                "position": pos,
                "salary": q,
                "power run": archs[0],
                "spread": archs[1],
                "west cost": archs[2],
                "vertical": archs[3],
                "clutch": rat[4],
                "dev points": rat[5],
                "fast development": 'false'
            }
            players.append(player)
            
        return players
    
    def generate_player_csv(self, filename='players_test.csv'):
        players = self.generate_players()
        import csv
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ["player_name", "side", "position", "salary",
                            "power run", "spread", "west coast", "vertical",
                            "clutch", "dev points", "fast development"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for player in players:
                writer.writerow(player)
                
if __name__ == "__main__":
    pg = playerGenerator()
    pg.generate_player_csv()