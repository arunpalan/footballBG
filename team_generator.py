import csv
import random

team_names = [
    "Bears", "Packers", "Steelers", "Cowboys", "49ers", "Patriots", "Giants", "Jets",
    "Eagles", "Rams", "Raiders", "Broncos", "Chiefs", "Dolphins", "Vikings", "Saints",
    "Colts", "Chargers", "Seahawks", "Buccaneers", "Ravens", "Falcons", "Panthers",
    "Texans", "Jaguars", "Titans", "Browns", "Cardinals", "Lions", "Bills", "Commanders"
]

archetypes = ["power run", "vertical", "west coast", "spread"]
qualities = [5]*20 + [4]*40 + [3]*50 + [2]*50 + [1]*40
random.shuffle(qualities)

def get_clutch(q):
    if q == 5:
        return random.randint(6, 8)
    elif q == 4:
        return random.randint(4, 7)
    elif q == 3:
        return random.randint(2, 6)
    elif q == 2:
        return random.randint(1, 4)
    else:
        return random.randint(0, 2)

def get_off(q):
    if q == 5:
        return random.randint(6, 17)
    elif q == 4:
        return random.randint(4, 15)
    elif q == 3:
        return random.randint(2, 13)
    elif q == 2:
        return random.randint(0, 11)
    else:
        return random.randint(0, 9)

def get_def(q):
    if q == 5:
        return random.randint(6, 17)
    elif q == 4:
        return random.randint(2, 15)
    elif q == 3:
        return random.randint(0, 13)
    elif q == 2:
        return random.randint(0, 11)
    else:
        return random.randint(0, 9)

teams = []
def_totals = [0, 0, 0, 0]  # power run, spread, west coast, vertical

for i in range(200):
    q = qualities[i]
    arch = archetypes[i % 4]
    clutch = get_clutch(q)
    off = get_off(q)
    # Defensive ratings
    defs = [get_def(q) for _ in range(4)]
    # Make sure no negative, and variance for lower quality
    for j in range(4):
        if q == 1 and random.random() < 0.2:
            defs[j] = 0
    # Now adjust so sum matches required total
    total = 3*off + sum(defs) + 4*clutch
    target = [16, 36, 56, 76, 96][q-1]
    diff = target - total
    # Adjust defense ratings to match total
    while diff != 0:
        idx = random.randint(0, 3)
        if diff > 0 and defs[idx] < (17 if q==5 else 15):
            defs[idx] += 1
            diff -= 1
        elif diff < 0 and defs[idx] > 0:
            defs[idx] -= 1
            diff += 1
        else:
            # Try next index
            continue
    def_totals = [def_totals[j] + defs[j] for j in range(4)]
    team = {
        "team_id": i+1,
        "team_name": random.choice(team_names),
        "quality": q,
        "arch": arch,
        "off": off,
        "power run": defs[0],
        "spread": defs[1],
        "west coast": defs[2],
        "vertical": defs[3],
        "clutch": clutch
    }
    teams.append(team)

# Balance defense totals
avg_def = sum(def_totals) // 4
for j in range(4):
    while def_totals[j] > avg_def:
        # Find a team with this defense > 0 and reduce it
        for t in teams:
            if t[archetypes[j]] > 0:
                t[archetypes[j]] -= 1
                def_totals[j] -= 1
                break
    while def_totals[j] < avg_def:
        # Find a team with this defense < max and increase it
        for t in teams:
            if t[archetypes[j]] < (17 if t["quality"]==5 else 15):
                t[archetypes[j]] += 1
                def_totals[j] += 1
                break

with open("teams_test.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["team_id","team_name","quality","arch","off","power run","spread","west coast","vertical","clutch"])
    writer.writeheader()
    for team in teams:
        writer.writerow(team)