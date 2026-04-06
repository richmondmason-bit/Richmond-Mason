# helper.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from faker import Faker
import random
import os

fake = Faker()

# Character Class

class Character:
    def __init__(self, name, level=1, stats=None, backstory=None):
        self.name = name
        self.level = level
        self.stats = stats or {"strength": 5, "dexterity": 5, "intelligence": 5}
        self.backstory = backstory

    def to_dict(self):
        return {"name": self.name, "level": self.level, **self.stats, "backstory": self.backstory}



# Random Generator

class RandomGenerator:
    def generate_name(self):
        return fake.name()

    def generate_backstory(self):
        return fake.sentence(nb_words=15)

    def generate_stats(self):
        return {k: random.randint(1, 20) for k in ["strength", "dexterity", "intelligence"]}

    def generate_character(self):
        return Character(
            self.generate_name(),
            stats=self.generate_stats(),
            backstory=self.generate_backstory()
        )


# Data Visualization

class DataVisualization:
    def plot_bar_stats(self, character):
        stats = character.stats
        plt.bar(stats.keys(), stats.values(), color='skyblue')
        plt.title(f"{character.name}'s Stats")
        plt.ylabel('Value')
        plt.show()

    def plot_radar_chart(self, character):
        labels = list(character.stats.keys())
        values = list(character.stats.values())
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles), labels)
        plt.title(f"{character.name} Radar Chart")
        plt.show()



# Statistical Analyzer

class StatisticalAnalyzer:
    def __init__(self, characters):
        self.df = pd.DataFrame([c.to_dict() for c in characters])

    def summary_stats(self):
        numeric_cols = self.df.select_dtypes(include='number').columns
        return self.df[numeric_cols].describe()

    def filter_by_stat(self, stat, min_val):
        return self.df[self.df[stat] >= min_val]



# Data Manager

class CSVManager:
    CSV_FILE = "MR_CP2\Rpg\Character.csv"

    @staticmethod
    def save_to_csv(characters):
        df = pd.DataFrame([c.to_dict() for c in characters])
        df.to_csv(CSVManager.CSV_FILE, index=False)

    @staticmethod
    def load_from_csv():
        if not os.path.exists(CSVManager.CSV_FILE) or os.path.getsize(CSVManager.CSV_FILE) == 0:
            return []
        df = pd.read_csv(CSVManager.CSV_FILE)
        characters = []
        for _, row in df.iterrows():
            stats = {k: row[k] for k in ["strength", "dexterity", "intelligence"] if k in row}
            characters.append(Character(row['name'], row['level'], stats, row.get('backstory')))
        return characters