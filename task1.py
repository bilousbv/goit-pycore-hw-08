import pickle
import re
from collections import UserDict
from datetime import datetime, timedelta

WEEKDAYS_LENGTH = 5
WEEK_LENGTH = 7
DATE_FORMAT = '%d.%m.%Y'


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter a valid command."
        except ValueError:
            return "Enter the argument for the command."
        except Exception as e:
            return e
        except IndexError:
            return "Give me both name and phone number."

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
            self.birthday = birthday
            super().__init__(birthday)
        except ValueError:
            raise Exception("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.birthday.strftime(DATE_FORMAT)


class Phone(Field):
    def __init__(self, value):
        if not re.match(r"^\d{10}$", value):
            raise Exception("Phone number must be exactly 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.__phones = []
        self.__birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == phone_number:
                phone_to_remove = phone
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            print("Phone number not found.")

    def edit_phone(self, old_phone_number, new_phone_number):
        self.remove_phone(old_phone_number)
        self.add_phone(new_phone_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value
        return "Phone number not found."

    @property
    def birthday(self):
        return self.__birthday

    @property
    def phones(self):
        return self.__phones

    def add_birthday(self, birthday):
        self.__birthday = Birthday(birthday)

    def __str__(self):
        return (f"Contact name: {self.name.value},"
                f" Phones: {'; '.join(phone.value for phone in self.phones)},"
                f" Birthday: {self.birthday}")


class AddressBook(UserDict):
    def add_record(self, new_record):
        self.data[new_record.name.value] = new_record

    def find(self, record_name):
        return self.data.get(record_name)

    def delete(self, record_name):
        if record_name in self.data:
            del self.data[record_name]
        else:
            print("Contact not found.")

    def get_upcoming_birthdays(self):
        current_date = datetime.today().date()
        current_year = current_date.year
        users_for_congratulation = list()

        try:
            for user_name in self.data:
                user = self.data.get(user_name)
                if user.birthday is None:
                    continue

                user_birthday_date = datetime.strptime(str(user.birthday), DATE_FORMAT).date()
                user_birthday_date_this_year = user_birthday_date.replace(year=current_year)
                delta = user_birthday_date_this_year - current_date

                if delta.days not in range(0, 7):
                    continue

                weekday = user_birthday_date_this_year.weekday()

                if weekday < WEEKDAYS_LENGTH:
                    congratulation_date = user_birthday_date_this_year.strftime(DATE_FORMAT)
                else:
                    congratulation_date = user_birthday_date_this_year + timedelta(days=WEEK_LENGTH - weekday)

                users_for_congratulation.append(f"{user}, Congratulation date: {congratulation_date}")

            if len(users_for_congratulation) == 0:
                return None
            else:
                return "\n".join(f"{user_record}" for user_record in users_for_congratulation)
        except Exception as e:
            print(e)


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = f"Contact {name} has been updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Contact {name} has been added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone_number, new_phone_number = args
    record = book.find(name)

    if record is None:
        return f"Contact {name} not found."
    else:
        record.edit_phone(old_phone_number, new_phone_number)
        return f"Contact {name} has been updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return '; '.join(phone.value for phone in record.phones)


@input_error
def show_all(book):
    if not book.data.items():
        return "No contacts available."
    return "\n".join(f"{record}" for name, record in book.data.items())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    else:
        record.add_birthday(birthday)
        return f"Birthday has been added to {name}."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    else:
        return record.birthday


@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()

    if upcoming_birthdays is None:
        return "Upcoming birthdays not found."
    else:
        return upcoming_birthdays


@input_error
def delete_contact(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        book.delete(name)
        return f"Contact {name} has been deleted."


def parse_input(user_input):
    cmd, *args = user_input.split(' ')
    cmd = cmd.strip().lower()

    return cmd, *args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def get_commands():
    return ("Available commands:\n"
            "- help - to show available commands\n"
            "- hello\n"
            "- add [name] [phone_number] - to add new record to the address book\n"
            "- change [name] [old_phone_number] [new_phone_number] - to change phone number\n"
            "- phone [name] - to show records phone numbers\n"
            "- add-birthday [name] [birthday] - to add birthday to the address book record\n"
            "- show-birthday [name] - to show birthday of the address book record\n"
            "- birthdays - to show upcoming birthdays\n"
            "- delete [name] - to delete record from the address book\n"
            "- all - to show all contacts\n"
            "- exit or close - to exit\n")


def main():
    print("Welcome to Assistant Bot!")
    print(get_commands())
    book = load_data()

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book);
            print("Good bye!")
            break
        elif command == "help":
            print(get_commands())
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "all":
            print(show_all(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
