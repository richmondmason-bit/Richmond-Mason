class Student:
    def __init__(self, name: str, student_id: str):
        self.name = name.strip()
        self.student_id = student_id.strip()
        self.grades: list[float] = []

    def add_grade(self, grade: float) -> bool:
        if not isinstance(grade, (int, float)) or not (0 <= grade <= 100):
            return False
        self.grades.append(float(grade))
        return True

    def calculate_average(self) -> float | None:
        if not self.grades:
            return None
        return sum(self.grades) / len(self.grades)

    def get_letter_grade(self) -> str:
        avg = self.calculate_average()
        if avg is None:
            return "N/A"
        if avg >= 90:
            return "A"
        elif avg >= 80:
            return "B"
        elif avg >= 70:
            return "C"
        elif avg >= 60:
            return "D"
        else:
            return "F"

    def display_info(self) -> None:
        avg = self.calculate_average()
        letter = self.get_letter_grade()
        print(f"Student: {self.name} (ID: {self.student_id})")
        print(f"Grades: {self.grades if self.grades else 'None entered yet'}")
        if avg is None:
            print("Average: N/A")
        else:
            print(f"Average: {avg:.2f}")
        print(f"Letter Grade: {letter}")
        print("-" * 40)
class GradeBook:
   
    def __init__(self):
        self.students: list[Student] = []

    def add_student(self, student: Student) -> bool:
        if any(s.student_id == student.student_id for s in self.students):
            return False
        self.students.append(student)
        return True

    def find_student_by_id(self, student_id: str) -> Student | None:
        for student in self.students:
            if student.student_id == student_id.strip():
                return student
        return None

    def find_student_by_name(self, name: str) -> list[Student]:
        search_name = name.strip().lower()
        return [s for s in self.students if s.name.lower() == search_name]

    def get_class_average(self) -> float | None:
        valid_avgs = [s.calculate_average() for s in self.students if s.calculate_average() is not None]
        if not valid_avgs:
            return None
        return sum(valid_avgs) / len(valid_avgs)

    def display_all_students(self) -> None:
        if not self.students:
            print("No students in the grade book yet.")
            return
        for student in self.students:
            student.display_info()


def main():
    gradebook = GradeBook()
    print("Grade Book")
    print("Tip: Always enter student id for anything the program does not use names only the id")
    while True:
        print("Main Menu")
        print("1. Add a new student")
        print("2. Add a grade to a student")
        print("3. View individual student record")
        print("4. View student record")
        print("5. View class summary ")
        print("6. Exit the program")
        

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1": 
            name = input("Enter student's full name: ").strip()
            if not name:
                print("Error: Name cannot be empty.")
                continue
            student_id = input("Enter unique student ID: ").strip()
            if not student_id:
                print("Error: Student ID cannot be empty.")
                continue
            new_student = Student(name, student_id)
            if gradebook.add_student(new_student):
                print(f" Student '{name}' (ID: {student_id}) added successfully!")
            else:
                print(" Student already exists.")

        elif choice == "2":  
            student_id = input("enter student to add grade: ").strip()
            student = gradebook.find_student_by_id(student_id)
            if not student:
                print("Student not found.")
                continue
            try:
                grade_input = input(f"enter grade for {student.name} (0-100): ").strip()
                grade = float(grade_input)
                if student.add_grade(grade):
                    print(f" Grade {grade} added to {student.name}.")
                else:
                    print("grade must be between 0 and 100 inclusive.")
            except ValueError:
                print(" enter a valid number")

        elif choice == "3": 
            student_id = input("Enter student ID: ").strip()
            student = gradebook.find_student_by_id(student_id)
            if student:
                print("\nStudent Record:")
                student.display_info()
            else:
                print(" Student not found.")

        elif choice == "4":  
            name = input("Enter student name: ").strip()
            students = gradebook.find_student_by_name(name)
            if students:
                print(f"\nFound {len(students)} student(s) with name '{name}':")
                for student in students:
                    student.display_info()
            else:
                print("No students found with that name.")

        elif choice == "5":  
            print("\nClass summary")
            gradebook.display_all_students()
            class_avg = gradebook.get_class_average()
            if class_avg is not None:
                print(f"\nOverall Class Average: {class_avg:.2f}")
            else:
                print("\nNo grades have been entered yet for any student.")

        elif choice == "6":
            print("\nThank you for using the Grade Book System. Goodbye!")
            break

        else:
            print("Invalid menu choice. Please enter a number between 1 and 6.")
        input("\nPress Enter to return to the main menu...")
main()