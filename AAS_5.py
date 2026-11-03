from datetime import datetime

appointments = []
faculties = []
availability = []

purposes = [
    "Academic Advising",
    "Subject Consultation",
    "Enrollment Concern",
    "Academic Requirement",
    "Other Concern"
]


def banner():
    print("\n" + "=" * 68)
    print("                 ACADEMIC APPOINTMENT SCHEDULER")
    print("=" * 68)


def print_table(headers, rows):
    """Print a simple aligned text table."""
    if not rows:
        print("No records found.")
        return
    widths = [len(str(header)) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(separator)
    print("| " + " | ".join(str(headers[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    print(separator)
    for row in rows:
        print("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    print(separator)


def find_faculty(faculty_id):
    for faculty in faculties:
        if faculty["id"] == faculty_id:
            return faculty
    return None


def check_date(date_text):
    try:
        datetime.strptime(date_text, "%m/%d/%Y")
        return True
    except ValueError:
        return False


def check_time(time_text):
    try:
        datetime.strptime(time_text, "%I:%M %p")
        return True
    except ValueError:
        return False


def create_account():
    print("\n--- CREATE FACULTY ACCOUNT ---")
    name = input("Faculty name: ").strip()
    password = input("Create password: ").strip()
    if not name or not password:
        print("Name and password cannot be empty.")
        return

    faculty_id = str(max([int(f["id"]) for f in faculties], default=0) + 1).zfill(3)
    faculties.append({"id": faculty_id, "name": name, "password": password})
    print("\nAccount created successfully!")
    print("Faculty ID:", faculty_id)
    print("Please remember your Faculty ID and password.")


def slot_is_booked(faculty_id, date, slot, skip_appointment=None):
    return any(
        appointment is not skip_appointment
        and appointment["faculty_id"] == faculty_id
        and appointment["date"] == date
        and appointment["slot"] == slot
        and appointment["status"] == "Confirmed"
        for appointment in appointments
    )


def get_available_slots(faculty_id, date=None, skip_appointment=None):
    """Return each faculty availability period as one selectable slot.

    The faculty member sets the start and end time. The system does not split
    availability into fixed 30-minute intervals.
    """
    slots = []
    for item in availability:
        if item["faculty_id"] != faculty_id or (date and item["date"] != date):
            continue
        slot_text = f"{item['start']} - {item['end']}"
        if not slot_is_booked(faculty_id, item["date"], slot_text, skip_appointment):
            entry = {"faculty_id": faculty_id, "date": item["date"], "slot": slot_text}
            if entry not in slots:
                slots.append(entry)
    slots.sort(key=lambda entry: (
        datetime.strptime(entry["date"], "%m/%d/%Y"),
        datetime.strptime(entry["slot"].split(" - ")[0], "%I:%M %p")
    ))
    return slots


def show_slots(faculty_id, skip_appointment=None):
    slots = get_available_slots(faculty_id, skip_appointment=skip_appointment)
    rows = [[i + 1, slot["faculty_id"], slot["date"], slot["slot"]] for i, slot in enumerate(slots)]
    print_table(["Slot No.", "Faculty ID", "Available Date", "Time"], rows)
    return slots


def add_availability(faculty_id):
    print("\n--- ADD AVAILABLE TIME ---")
    date_text = input("Date (MM/DD/YYYY): ").strip()
    if not check_date(date_text):
        print("Invalid date. Please use MM/DD/YYYY.")
        return
    start_text = input("Start time (e.g., 8:00 AM): ").strip().upper()
    end_text = input("End time (e.g., 11:00 AM): ").strip().upper()
    if not check_time(start_text) or not check_time(end_text):
        print("Invalid time. Use a format like 8:00 AM or 1:00 PM.")
        return

    start = datetime.strptime(start_text, "%I:%M %p")
    end = datetime.strptime(end_text, "%I:%M %p")
    if end <= start:
        print("End time must be later than start time.")
        return
    for item in availability:
        if item["faculty_id"] == faculty_id and item["date"] == date_text:
            old_start = datetime.strptime(item["start"], "%I:%M %p")
            old_end = datetime.strptime(item["end"], "%I:%M %p")
            if start < old_end and end > old_start:
                print("This time overlaps with availability you already added.")
                return

    availability.append({
        "faculty_id": faculty_id,
        "date": date_text,
        "start": start.strftime("%I:%M %p"),
        "end": end.strftime("%I:%M %p")
    })
    print("Available time added successfully!")


def view_my_available_times(faculty_id):
    rows = []
    for item in availability:
        if item["faculty_id"] == faculty_id:
            rows.extend([[slot["date"], slot["slot"], "Available"]
                         for slot in get_available_slots(faculty_id, item["date"])])
    print("\n--- MY AVAILABLE SLOTS ---")
    print_table(["Date", "Time", "Status"], rows)


def faculty_appointments(faculty_id, confirmed_only=False):
    return [a for a in appointments if a["faculty_id"] == faculty_id and (not confirmed_only or a["status"] == "Confirmed")]


def view_faculty_appointments(faculty_id):
    print("\n--- MY APPOINTMENTS ---")
    rows = [[a["student"], a["purpose"], a["date"], a["slot"], a["status"], a["done"]]
            for a in faculty_appointments(faculty_id)]
    print_table(["Student Name", "Purpose", "Date", "Time", "Status", "Done?"], rows)


def update_appointment_done(faculty_id):
    print("\n--- UPDATE APPOINTMENT STATUS ---")
    found = faculty_appointments(faculty_id, confirmed_only=True)
    rows = [[i + 1, a["student"], a["purpose"], a["date"], a["slot"], a["done"]]
            for i, a in enumerate(found)]
    print_table(["No.", "Student Name", "Purpose", "Date", "Time", "Done?"], rows)
    if not found:
        return
    choice = input("Select appointment number to update (or press Enter to go back): ").strip()
    if not choice:
        return
    if not choice.isdigit() or not 1 <= int(choice) <= len(found):
        print("Invalid appointment number.")
        return
    done = input("Appointment done? (Yes/No): ").strip().lower()
    if done not in ("yes", "no"):
        print("Please enter Yes or No.")
        return
    found[int(choice) - 1]["done"] = "Yes" if done == "yes" else "No"
    print("Appointment status updated.")


def faculty_login():
    print("\n--- FACULTY LOGIN ---")
    faculty_id = input("Faculty ID: ").strip()
    password = input("Password: ").strip()
    faculty = find_faculty(faculty_id)
    if not faculty:
        print("Faculty ID not found. Please create an account first.")
        return
    if faculty["password"] != password:
        print("Incorrect password.")
        return
    print("\nWelcome,", faculty["name"] + "!")
    faculty_menu(faculty_id)


def faculty_menu(faculty_id):
    while True:
        print("\n--- FACULTY MENU ---")
        print("1. Login")
        print("2. Add Available Time")
        print("3. View Available Slots")
        print("4. View Appointments / Update Done Status")
        print("5. Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            print("You are already logged in.")
        elif choice == "2":
            add_availability(faculty_id)
        elif choice == "3":
            view_my_available_times(faculty_id)
        elif choice == "4":
            view_faculty_appointments(faculty_id)
            update_appointment_done(faculty_id)
        elif choice == "5":
            print("Faculty logged out.")
            break
        else:
            print("Invalid choice. Please try again.")


def book_appointment():
    print("\n--- BOOK APPOINTMENT ---")
    if not faculties:
        print("No faculty accounts are available. Please ask a faculty member to create an account first.")
        return
    student_name = input("Enter name: ").strip()
    if not student_name:
        print("Name cannot be empty.")
        return
    faculty_id = input("Enter Faculty ID: ").strip()
    faculty = find_faculty(faculty_id)
    if not faculty:
        print("Invalid Faculty ID.")
        return

    slots = show_slots(faculty_id)
    if not slots:
        return
    choice = input("Select time slot number: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(slots):
        print("Invalid time slot number.")
        return
    selected = slots[int(choice) - 1]

    print("\n--- SELECT PURPOSE ---")
    for i, purpose in enumerate(purposes, 1):
        print(f"{i}. {purpose}")
    purpose_choice = input("Choose purpose number: ").strip()
    if not purpose_choice.isdigit() or not 1 <= int(purpose_choice) <= len(purposes):
        print("Invalid purpose.")
        return
    if slot_is_booked(faculty_id, selected["date"], selected["slot"]):
        print("Sorry, that time slot has just been booked. Please select another slot.")
        return

    appointments.append({
        "student": student_name,
        "faculty_id": faculty_id,
        "faculty_name": faculty["name"],
        "date": selected["date"],
        "purpose": purposes[int(purpose_choice) - 1],
        "slot": selected["slot"],
        "status": "Confirmed",
        "done": "No"
    })
    print("\nAppointment booked successfully!")
    print_table(["Faculty", "Date", "Time", "Purpose", "Status"], [[faculty["name"], selected["date"], selected["slot"], purposes[int(purpose_choice) - 1], "Confirmed"]])


def find_student_appointments(student_name, confirmed_only=False):
    return [a for a in appointments if a["student"].casefold() == student_name.casefold() and (not confirmed_only or a["status"] == "Confirmed")]


def select_student_appointment(action):
    student_name = input("Enter your name: ").strip()
    found = find_student_appointments(student_name, confirmed_only=True)
    rows = [[i + 1, a["faculty_name"], a["purpose"], a["date"], a["slot"], a["status"]]
            for i, a in enumerate(found)]
    print_table(["No.", "Faculty", "Purpose", "Date", "Time", "Status"], rows)
    if not found:
        return None
    choice = input(f"Select appointment number to {action} (or press Enter to go back): ").strip()
    if not choice:
        return None
    if not choice.isdigit() or not 1 <= int(choice) <= len(found):
        print("Invalid appointment number.")
        return None
    return found[int(choice) - 1]


def cancel_appointment():
    print("\n--- CANCEL APPOINTMENT ---")
    appointment = select_student_appointment("cancel")
    if appointment is None:
        return
    confirm = input("Cancel this appointment? (Yes/No): ").strip().lower()
    if confirm == "yes":
        appointment["status"] = "Cancelled"
        print("Appointment cancelled successfully.")
    else:
        print("Cancellation stopped.")


def reschedule_appointment():
    print("\n--- RESCHEDULE APPOINTMENT ---")
    appointment = select_student_appointment("reschedule")
    if appointment is None:
        return
    faculty_id = input("Enter Faculty ID for the new appointment: ").strip()
    faculty = find_faculty(faculty_id)
    if not faculty:
        print("Invalid Faculty ID.")
        return
    slots = show_slots(faculty_id, skip_appointment=appointment)
    if not slots:
        return
    choice = input("Select new time slot number: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(slots):
        print("Invalid time slot number.")
        return
    selected = slots[int(choice) - 1]
    if slot_is_booked(faculty_id, selected["date"], selected["slot"], appointment):
        print("Sorry, that time slot has just been booked. Please select another slot.")
        return
    appointment["faculty_id"] = faculty_id
    appointment["faculty_name"] = faculty["name"]
    appointment["date"] = selected["date"]
    appointment["slot"] = selected["slot"]
    appointment["done"] = "No"
    print("Appointment rescheduled successfully!")


def view_history():
    print("\n--- APPOINTMENT HISTORY ---")
    student_name = input("Enter your name: ").strip()
    found = find_student_appointments(student_name)
    rows = [[a["faculty_name"], a["purpose"], a["date"], a["slot"], a["status"], a["done"]]
            for a in found]
    print_table(["Faculty", "Purpose", "Date", "Time", "Status", "Done?"], rows)


def student_menu():
    while True:
        print("\n--- STUDENT MENU ---")
        print("1. Book Appointment")
        print("2. Cancel Appointment")
        print("3. Reschedule Appointment")
        print("4. View Appointment History")
        print("5. Back to Main Menu")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            book_appointment()
        elif choice == "2":
            cancel_appointment()
        elif choice == "3":
            reschedule_appointment()
        elif choice == "4":
            view_history()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def faculty_menu_entry():
    while True:
        print("\n--- FACULTY MENU ---")
        print("1. Login")
        print("2. Back to Main Menu")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            faculty_login()
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    while True:
        banner()
        print("1. Create Account")
        print("2. Faculty Menu")
        print("3. Student Menu")
        print("4. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            create_account()
        elif choice == "2":
            faculty_menu_entry()
        elif choice == "3":
            student_menu()
        elif choice == "4":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
