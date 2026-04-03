# Helper.py
import pandas as pd
import matplotlib.pyplot as plt
from faker import Faker
import random

fake = Faker()

class Character:
    VALID_EYE_COLORS = ["Blue", "Brown", "Green", "Hazel", "Gray", "Amber"]

    def __init__(self, name, type_, STR, INT, SPD, HP, skin, eyes, height, hunter):
        self.name = name
        self.type = type_
        self.attributes = {"STR": STR, "INT": INT, "SPD": SPD, "HP": HP}
        self.skin = skin
        self.eyes = eyes if eyes in self.VALID_EYE_COLORS else "Brown"
        self.height = height
        self.hunter = hunter

    def to_dict(self):
        return {
            "Name": self.name,
            "Type": self.type,
            **self.attributes,
            "Skin": self.skin,
            "Eyes": self.eyes,
            "Height": self.height,
            "Hunter": self.hunter
        }

    def display_stats(self):
        print(f"{self.name} ({self.type})")
        for attr, val in self.attributes.items():
            print(f"{attr}: {val}")
        print(f"Skin: {self.skin} | Eyes: {self.eyes} | Height: {self.height} | Hunter: {self.hunter}")


class RandomGenerator:
    TYPES = ["Human", "Dog", "Goblin", "Bear"]
    SKINS = ["Fair", "Tan", "Dark", "Green", "Blue"]

    @staticmethod
    def GenerateCharacter():
        name = fake.name()
        type_ = random.choice(RandomGenerator.TYPES)
        STR = random.randint(5, 20)
        INT = random.randint(5, 20)
        SPD = random.randint(5, 20)
        HP = random.randint(10, 30)
        skin = random.choice(RandomGenerator.SKINS)
        eyes = random.choice(Character.VALID_EYE_COLORS)
        height = f"{random.randint(140, 210)}cm"
        hunter = random.choice(["Yes", "No"])
        return Character(name, type_, STR, INT, SPD, HP, skin, eyes, height, hunter)

    @staticmethod
    def GenerateBackstory(character: Character):
        traits = ["brilliant","reckless","charming","cold","empathetic","manipulative","loyal","ambitious"]
        hobbies = ["hiking","reading","coding","traveling","painting","gaming","cooking"]
        past_events = ["survived a near-fatal accident","won a prestigious award","lost someone important"]
        goals = ["seeking revenge","trying to find purpose","hiding a dangerous secret"]
        secrets = ["they are not who they claim to be","they are being watched","their past identity was erased"]
        return (
            f"{character.name}, a {character.type}, is {random.choice(traits)}. "
            f"Enjoys {random.choice(hobbies)}. "
            f"Previously, {random.choice(past_events)}. "
            f"Currently, {random.choice(goals)}. Secretly, {random.choice(secrets)}."
        )

class DataVisualization:
    @staticmethod
    def radar_chart(character: Character):
        stats = character.attributes
        labels = list(stats.keys())
        values = list(stats.values())
        values += values[:1]  # Close the loop
        angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
        angles += angles[:1]

        plt.figure(figsize=(6,6))
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.title(f"{character.name}'s Stats")
        plt.show()

    @staticmethod
    def bar_chart(character: Character):
        stats = character.attributes
        plt.figure(figsize=(6,4))
        plt.bar(stats.keys(), stats.values(), color='skyblue')
        plt.title(f"{character.name}'s Stats")
        plt.ylabel("Value")
        plt.show()

class StatisticalAnalyzer:
    def __init__(self, characters):
        self.characters = characters
        self.df = pd.DataFrame([c.to_dict() for c in characters])

    def summary_stats(self):
        print("=== Summary Statistics ===")
        print(self.df[["STR","INT","SPD","HP"]].describe())

    def top_attribute(self, attr, top_n=3):
        print(f"=== Top {top_n} Characters by {attr} ===")
        top = self.df.sort_values(by=attr, ascending=False).head(top_n)
        print(top[["Name","Type",attr]])

    def attribute_distribution(self, attr):
        plt.figure(figsize=(6,4))
        self.df[attr].hist(color='lightgreen')
        plt.title(f"Distribution of {attr}")
        plt.xlabel(attr)
        plt.ylabel("Frequency")
        plt.show()


class CSVManager:
    @staticmethod
    def SaveCharToCSV(characters, filename="MR_CP2\Rpg\Character.csv"):
        df = pd.DataFrame([c.to_dict() for c in characters])
        df.to_csv(filename, index=False)
        print(f"Saved {len(characters)} characters to {filename}")

    @staticmethod
    def LoadCharToCSV(filename="MR_CP2\Rpg\Character.csv"):
        characters = []
        try:
            df = pd.read_csv(filename)
            for _, row in df.iterrows():
                c = Character(
                    row["Name"], row["Type"], row["STR"], row["INT"], row["SPD"], row["HP"],
                    row["Skin"], row["Eyes"], row["Height"], row["Hunter"]
                )
                characters.append(c)
        except FileNotFoundError:
            print(f"No CSV file found: {filename}")
        return characters