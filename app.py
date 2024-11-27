import customtkinter as ctk
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from CTkMessagebox import CTkMessagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Teacher Scheduler")
        self.geometry("700x500")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tabview.add("Add Teacher")
        self.tabview.add("Assign Schedule")
        self.tabview.add("View Schedule")

        # Add Teacher Tab
        self.name_entry = ctk.CTkEntry(self.tabview.tab("Add Teacher"), placeholder_text="First Name")
        self.name_entry.pack(pady=10)
        self.surname_entry = ctk.CTkEntry(self.tabview.tab("Add Teacher"), placeholder_text="Last Name")
        self.surname_entry.pack(pady=10)
        self.add_teacher_button = ctk.CTkButton(self.tabview.tab("Add Teacher"), text="Add Teacher", command=self.add_teacher)
        self.add_teacher_button.pack(pady=10)

        # Assign Schedule Tab
        self.teacher_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"), values=self.get_teachers())
        self.teacher_select.pack(pady=10)
        self.teacher_select.set("Select Teacher")

        self.day_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"),
                                          values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.day_select.pack(pady=10)
        self.day_select.set("Select Day")

        self.start_hour_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"), values=[str(i) for i in range(8, 18)])
        self.start_hour_select.pack(pady=5)  # Reduced pady for better spacing
        self.start_hour_select.set("Start Hour")

        self.end_hour_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"), values=[str(i) for i in range(9, 18)])
        self.end_hour_select.pack(pady=5)  # Reduced pady
        self.end_hour_select.set("End Hour")

        self.class_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"),
                                            values=["Class A", "Class B", "Class C"])
        self.class_select.pack(pady=10)
        self.class_select.set("Select Class")

        self.module_select = ctk.CTkComboBox(self.tabview.tab("Assign Schedule"),
                                             values=["Math", "Science", "English", "History"])
        self.module_select.pack(pady=10)
        self.module_select.set("Select Module")

        self.assign_button = ctk.CTkButton(self.tabview.tab("Assign Schedule"), text="Assign", command=self.assign_schedule)
        self.assign_button.pack(pady=10)

        # View Schedule Tab
        self.view_teacher_select = ctk.CTkComboBox(self.tabview.tab("View Schedule"), values=self.get_teachers())
        self.view_teacher_select.pack(pady=10)
        self.view_teacher_select.set("Select Teacher")


        self.preview_button = ctk.CTkButton(self.tabview.tab("View Schedule"), text="Preview", command=self.preview_schedule)
        self.preview_button.pack(pady=5)

        self.schedule_text = ctk.CTkTextbox(self.tabview.tab("View Schedule"), width=500, height=200)
        self.schedule_text.pack(pady=10)
        self.schedule_text.configure(state="disabled")


        self.save_pdf_button = ctk.CTkButton(self.tabview.tab("View Schedule"), text="Save to PDF", command=self.save_schedule_pdf)
        self.save_pdf_button.pack(pady=10)

    def add_teacher(self):
        name = self.name_entry.get()
        surname = self.surname_entry.get()
        if name and surname:
            with open("teachers.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, surname])
            self.name_entry.delete(0, ctk.END)
            self.surname_entry.delete(0, ctk.END)
            #Update comboboxes
            self.update_teacher_comboboxes()

    def get_teachers(self):
        try:
            with open("teachers.csv", "r") as f:
                reader = csv.reader(f)
                teachers = [f"{row[0]} {row[1]}" for row in reader]
            return teachers
        except FileNotFoundError:  # Handle the case where the file doesn't exist yet.
            return []

    def assign_schedule(self):
            teacher = self.teacher_select.get()
            day = self.day_select.get()
            try:
                start_hour = int(self.start_hour_select.get())
                end_hour = int(self.end_hour_select.get())
            except ValueError:
                CTkMessagebox(title="Error", message="Invalid start or end hour. Please enter numbers.")
                return

            selected_class = self.class_select.get()
            module = self.module_select.get()

            if end_hour <= start_hour:
                CTkMessagebox(title="Error", message="End time must be after start time.")
                return

            if all([teacher, day, start_hour, end_hour, selected_class, module]):
                if self.check_schedule_conflict(teacher, day, start_hour, end_hour):
                    CTkMessagebox(title="Error", message="Teacher already has a class scheduled during this time.")
                    return  # Don't add the schedule

                schedule_filename = teacher.replace(" ", "_") + "_schedule.csv"
                with open(schedule_filename, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([day, start_hour, end_hour, selected_class, module])

                self.teacher_select.set("Select Teacher")
                self.day_select.set("Select Day")
                self.start_hour_select.set("Start Hour")
                self.end_hour_select.set("End Hour")
                self.class_select.set("Select Class")
                self.module_select.set("Select Module")

    def check_schedule_conflict(self, teacher, day, start_hour, end_hour):
        schedule_filename = teacher.replace(" ", "_") + "_schedule.csv"
        try:
            with open(schedule_filename, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    existing_day = row[0]
                    existing_start = int(row[1])
                    existing_end = int(row[2])
                    if existing_day == day and (
                        (start_hour >= existing_start and start_hour < existing_end) or
                        (end_hour > existing_start and end_hour <= existing_end) or
                        (start_hour <= existing_start and end_hour >= existing_end)
                    ):
                        return True  # Conflict found
        except FileNotFoundError:
            pass  # No existing schedule, so no conflict
        return False  # No conflict
    
    def preview_schedule(self):
        self.view_schedule()  # Just call view_schedule

    def view_schedule(self):  
        teacher = self.view_teacher_select.get()
        if teacher:
            schedule_filename = teacher.replace(" ", "_") + "_schedule.csv"
            try:
                with open(schedule_filename, "r") as f:
                    reader = csv.reader(f)
                    schedule = ""
                    for row in reader:
                        schedule += f"{row[0]} from {row[1]} to {row[2]}: {row[3]} ({row[4]})\n" # Updated output
                    self.schedule_text.configure(state="normal")
                    self.schedule_text.delete("1.0", ctk.END)
                    self.schedule_text.insert("1.0", schedule)
                    self.schedule_text.configure(state="disabled")
            except FileNotFoundError:
                self.schedule_text.configure(state="normal")
                self.schedule_text.delete("1.0", ctk.END)
                self.schedule_text.insert("1.0", "No schedule found for this teacher.")
                self.schedule_text.configure(state="disabled")

    def save_schedule_pdf(self):
        teacher = self.view_teacher_select.get()
        if teacher:
            schedule_filename = teacher.replace(" ", "_") + "_schedule.csv"
            try:
                c = canvas.Canvas(teacher.replace(" ", "_") + "_schedule.pdf", pagesize=letter)
                c.drawString(1 * inch, 10 * inch, f"Schedule for {teacher}")
                y_position = 9.5 * inch


                with open(schedule_filename, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                         c.drawString(1 * inch, y_position, f"{row[0]} at {row[1]}: {row[2]} ({row[3]})")
                         y_position -= 0.2* inch
                c.save()

            except FileNotFoundError:
                print("No schedule found for this teacher.")

    def update_teacher_comboboxes(self):
        teachers = self.get_teachers()
        self.teacher_select.configure(values=teachers)
        self.view_teacher_select.configure(values=teachers)

if __name__ == "__main__":
    app = App()
    app.mainloop()