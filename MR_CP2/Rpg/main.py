# main.py
from Helper import RandomGenerator, DataVisualization, StatisticalAnalyzer, CSVManager

characters = CSVManager.LoadCharToCSV()

def main_menu():
    while True:
        print("\n=== TERMINAL RPG MANAGER ===")
        print("1. Create new character")
        print("2. View character stats")
        print("3. Visualize character stats")
        print("4. Statistical analysis")
        print("5. Save all characters")
        print("6. Load characters")
        print("7. Quit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            c = RandomGenerator.GenerateCharacter()
            print("\nGenerated Character:")
            c.display_stats()
            print("\nBackstory:")
            print(RandomGenerator.GenerateBackstory(c))
            characters.append(c)

        elif choice == "2":
            if not characters:
                print("No characters available.")
                continue
            for i, c in enumerate(characters):
                print(f"{i+1}. {c.name} ({c.type})")
            idx = input("Select character: ")
            if idx.isdigit() and 1 <= int(idx) <= len(characters):
                characters[int(idx)-1].display_stats()
            else:
                print("Invalid selection.")

        elif choice == "3":
            if not characters:
                print("No characters available.")
                continue
            for i, c in enumerate(characters):
                print(f"{i+1}. {c.name} ({c.type})")
            idx = input("Select character: ")
            if idx.isdigit() and 1 <= int(idx) <= len(characters):
                chart_type = input("Chart type (radar/bar): ").lower()
                if chart_type == "radar":
                    DataVisualization.radar_chart(characters[int(idx)-1])
                else:
                    DataVisualization.bar_chart(characters[int(idx)-1])
            else:
                print("Invalid selection.")

        elif choice == "4":
            if not characters:
                print("No characters available.")
                continue
            analyzer = StatisticalAnalyzer(characters)
            print("1. Summary stats")
            print("2. Top attribute")
            print("3. Attribute distribution")
            sub_choice = input("Select analysis: ")
            if sub_choice == "1":
                analyzer.summary_stats()
            elif sub_choice == "2":
                attr = input("Attribute (STR/INT/SPD/HP): ").upper()
                analyzer.top_attribute(attr)
            elif sub_choice == "3":
                attr = input("Attribute (STR/INT/SPD/HP): ").upper()
                analyzer.attribute_distribution(attr)
            else:
                print("Invalid option.")

        elif choice == "5":
            CSVManager.SaveCharToCSV(characters)

        elif choice == "6":
            characters[:] = CSVManager.LoadCharToCSV()
            print(f"Loaded {len(characters)} characters.")

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main_menu()