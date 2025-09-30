import csv
import random

# Example name pools (expand as needed)
first_names = [
    "Aaron", "Tom", "Patrick", "Josh", "Justin", "Lamar", "Dak", "Russell", "Matthew", "Derrick",
    "Saquon", "Nick", "Christian", "Alvin", "Dalvin", "Tyreek", "Davante", "Stefon", "DeAndre", "Cooper",
    "Travis", "George", "Mark", "Darren", "Kyle", "Micah", "T.J.", "Jalen", "Myles", "Joey",
    "Jaire", "Xavien", "Jamal", "Derwin", "Budda", "Harrison", "Fred", "Bobby", "Darius", "Roquan",
    "Deshaun", "Baker", "Kirk", "Ryan", "Jared", "Carson", "Jimmy", "Tua", "Mac", "Zach",
    "Daniel", "Taylor", "Teddy", "Andy", "Joe", "Sam", "Cam", "Marcus", "Gardner", "Drew",
    "Ezekiel", "Leonard", "James", "Melvin", "Phillip", "Latavius", "Sony", "Kareem", "Chris", "A.J.",
    "Allen", "Antonio", "Brandin", "Calvin", "Courtland", "D.J.", "Deebo", "Emmanuel", "Jarvis", "Jerry",
    "JuJu", "Keenan", "Marquise", "Michael", "Odell", "Robby", "Sammy", "Sterling", "Terry", "Tyler",
    "Will", "Zay", "Adam", "Amari", "Brandon", "Chase", "Corey", "Curtis", "DeVante", "Diontae"
]
last_names = [
    "Rodgers", "Brady", "Mahomes", "Allen", "Herbert", "Jackson", "Prescott", "Wilson", "Stafford", "Henry",
    "Barkley", "Chubb", "McCaffrey", "Kamara", "Cook", "Hill", "Adams", "Diggs", "Hopkins", "Kupp",
    "Kelce", "Kittle", "Andrews", "Waller", "Pitts", "Parsons", "Watt", "Ramsey", "Garrett", "Bosa",
    "Alexander", "Howard", "Smith", "Warner", "Wagner", "Leonard", "Johnson", "Williams", "Brown", "Jones",
    "Miller", "Davis", "Moore", "Taylor", "Thomas", "White", "Harris", "Martin", "Thompson", "Young",
    "Clark", "Lewis", "Walker", "Hall", "King", "Wright", "Scott", "Green", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
    "Rivera", "Cooper", "Richardson", "Cox", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "Watson"
]

used_names = set()
def random_coach_name():
    while True:
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        if name not in used_names:
            used_names.add(name)
            return name

with open("coaches.csv", newline='', encoding='utf-8') as infile, \
     open("coaches_out.csv", "w", newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    staffers = list(reader)
    for row in staffers:
        writer.writerow(row)  # original staffer
    for row in staffers:
        coach_row = row.copy()
        coach_row['name'] = random_coach_name()
        coach_row['type'] = 'coach'
        coach_row['salary'] = str(int(row['salary']) + 1)
        writer.writerow(coach_row)

print("Done! Output written to coaches_out.csv")