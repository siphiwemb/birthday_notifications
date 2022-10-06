import requests, json, datetime


class Notifications():
    employees = list()

    def __init__(self, event:str):
        self.api_hostname = "https://interview-assessment-1.realmdigital.co.za"
        self.employees_url = self.api_hostname + "/employees"
        self.do_not_send_url = self.api_hostname + "/do-not-send-birthday-wishes"
        self.do_not_send_ids = list()
        self.today = datetime.datetime.today()
        self.event = event

    
    def __get_employees_data(self):
        """Gets and returns list of employees."""
        try:
            employees_req = requests.get(self.employees_url)
            employees = json.loads(employees_req.content)
            self.employees = employees

            employee_ids_req = requests.get(self.do_not_send_url)
            employee_ids = json.loads(employee_ids_req.content)
            self.do_not_send_ids = employee_ids
            
        except Exception as err:
            print(str(err))


    def get_today_birthdays(self):
        """Filters self.employees to employees with birthdays today."""
        self.employees = list(filter(self.__has_birthday, self.employees))


    def __has_birthday(self, employee_obj: dict):
        """Gets and returns employees with today's birthdays"""

        if "dateOfBirth" in employee_obj:
            if employee_obj["dateOfBirth"] is None:
                return False
            else:
                birthdate = datetime.datetime.strptime(employee_obj["dateOfBirth"], "%Y-%m-%dT%H:%M:%S")
                if birthdate.date().month == self.today.month and birthdate.date().day == self.today.day:
                    return True
                else:
                    if self.today.month == 2:
                        if not self.__is_leap_year() and birthdate.day > 28 and self.today.day == 28:
                            return True
                        else:
                            return False
                    else:
                        return False
        else:
            return False


    def __is_leap_year(self):
        """Checks and returns if self.today.year is a leap year or not"""
        year = self.today.year
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
    
    
    def remove_excluded_employees(self):
        """Removes employees that must not receive a notification."""

        for item in self.do_not_send_ids:
            self.employees = list(filter(lambda x: x["id"] != item, self.employees))
        
        self.employees = list(filter(self.__employee_has_started, self.employees))
        self.employees = list(filter(self.__employment_not_ended, self.employees))
        self.employees = list(filter(self.__birthday_not_notified, self.employees))


    def __employee_has_started(self, employee_obj: dict):
        """Returns true or false if an employee has started working."""

        if "employmentStartDate" in employee_obj:
            if employee_obj["employmentStartDate"] is None:
                return False
            else:
                employment_start_date = datetime.datetime.strptime(employee_obj["employmentStartDate"], "%Y-%m-%dT%H:%M:%S")
                if employment_start_date.date() <= self.today.date():
                    return True
                else:
                    return False
        else:
            return False
    

    def __employment_not_ended(self, employee_obj: dict):
        """Returns true or false if an employee has not stopped working."""

        if "employmentEndDate" in employee_obj:
            if employee_obj["employmentEndDate"] is None:
                return True
            else:
                employment_end_date = datetime.datetime.strptime(employee_obj["employmentEndDate"], "%Y-%m-%dT%H:%M:%S")
                if employment_end_date.date() <= self.today.date():
                    return True
                else:
                    return False
        else:
            return True


    def __birthday_not_notified(self, employee_obj: dict):
        """Returns true or false if an employee has not been notified on their birthday for the day."""

        if "lastBirthdayNotified" in employee_obj:
            if employee_obj["lastBirthdayNotified"] is None:
                return True
            else:
                last_birthday_notified = datetime.datetime.strptime(employee_obj["lastBirthdayNotified"], "%Y-%m-%d")
                if last_birthday_notified.date() == self.today.date():
                    return False
                else:
                    return True
        else:
            return True

    def __initiliza_emp_data(self):
        """Initializes the employee data to leave self.employee with employees ready to receive a notification."""
        self.__get_employees_data()
        self.get_today_birthdays()
        self.remove_excluded_employees()


    def __message(self, employee_obj: dict):
        """Text message to be sent to employees."""
        return f"""Happy {self.event} {employee_obj["name"]} {employee_obj["lastname"]}."""


    def send_messages(self):
        """Sends the notification to the prepared list of employees in self.employees"""
        self.__initiliza_emp_data()

        for emp in self.employees:
            print(self.__message(emp))
            emp["lastBirthdayNotified"] = str(self.today.date())

            # update_notified = requests.put(
            #     url=self.employees_url,
            #     data=emp
            # )


if __name__ == '__main__':
    try:
        notifications = Notifications("Birthday")
        notifications.send_messages()
    except Exception as err:
        print(str(err))