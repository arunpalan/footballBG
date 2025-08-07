import numpy as np
import pandas as pd
import csv

class Simulation:
    def __init__(self):
        self.teams = {}
        self.players = {}
        self.coaches = {}
        self.fans = {}
        self.tactics = {}
        self.stadiums = {}
        self.strategies = {}
        self.sponsors = {}

    def load_csv_data(self, filepath, key_field):
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

    def initialize_simulation(self):
        """Load all glossary data from CSV files."""
        self.teams = self.load_csv_data('teams.csv', key_field='team_name')
        self.players = self.load_csv_data('players.csv', key_field='player_name')
        self.coaches = self.load_csv_data('coaches.csv', key_field='name')
        self.fans = self.load_csv_data('fans.csv', key_field='name')
        self.tactics = self.load_csv_data('tactics.csv', key_field='name')
        self.stadiums = self.load_csv_data('stadiums.csv', key_field='name')
        self.strategies = self.load_csv_data('strategies.csv', key_field='name')
        self.sponsors = self.load_csv_data('sponsors.csv', key_field='company')