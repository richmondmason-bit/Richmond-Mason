# main.py
from helper import Character, RandomGenerator, DataVisualization, StatisticalAnalyzer, CSVManager

def main():
    characters = CSVManager.load_from_csv()
    generator = RandomGenerator()
    visualizer = DataVisualization()

    while True:
        print("\nCharacter Management")
        print("1. Create Random Character")
        print("2. Show All Characters")
        print("3. Visualize Character Stats")
        print("4. Show Statistical Summary")
        print("5. Save & Exit")
        choice = input("Select an option: ")

        if choice == "1":
            char = generator.generate_character()
            characters.append(char)
            print(f"Created character: {char.name}")
        elif choice == "2":
            if not characters:
                print("No characters yet.")
                continue
            for i, c in enumerate(characters, start=1):
                print(f"{i}. {c.name} | Level {c.level} | Stats: {c.stats}")
        elif choice == "3":
            if not characters:
                print("No characters to visualize.")
                continue
            for i, c in enumerate(characters, start=1):
                print(f"{i}. {c.name}")
            try:
                idx = int(input("Select a character number: ")) - 1
                if 0 <= idx < len(characters):
                    visualizer.plot_bar_stats(characters[idx])
                    visualizer.plot_radar_chart(characters[idx])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a number.")
        elif choice == "4":
            if not characters:
                print("No characters to analyze.")
                continue
            analyzer = StatisticalAnalyzer(characters)
            print(analyzer.summary_stats())
        elif choice == "5":
            CSVManager.save_to_csv(characters)
            print("Characters saved to Character.csv. Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()