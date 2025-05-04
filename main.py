from appoinment_feature import create_appt, cancel_appt, update_appt, view_all_appts

#See analytics 


def main():
    choice = '0'
    while choice != '5':
        print('Hello what would you like to do today?\n 1. Schedule an appointment\n 2. Cancel an appointment\n 3. Update an appointment\n 4. View exisiting appointments\n 5. Quit')
        choice = input('Choose an option:')
        if choice == '1':
            name = input('Enter the name of the patient:')
            doctor = input('Enter the name of the doctor:')
            date= input('Enter the preferred date (YYYY-MM-DD):')
            time = input('Enter the preferred time (HH:MM 24 hr format):')
            print(create_appt(name, doctor, date, time))
        elif choice == '2':
            name = input('Enter the name of the patient:')
            doctor = input('Enter the name of the doctor:')
            date= input('Enter the date of the appointment (YYYY-MM-DD):')
            time = input('Enter the time of the appointment (HH:MM 24 hr format):')
            print(cancel_appt(name, doctor, date, time))
        elif choice == '3':
            name = input('Enter the name of the patient:')
            doctor = input('Enter the name of the doctor:')
            old_date= input('Enter the old date (YYYY-MM-DD):')
            old_time = input('Enter the old time (HH:MM 24 hr format):')
            new_date= input('Enter the new date (YYYY-MM-DD):')
            new_time = input('Enter the new time (HH:MM 24 hr format):')
            print(update_appt(name, doctor, old_date, old_time, new_date, new_time))
        elif choice == '4':
            appointments = view_all_appts()
            if not appointments:
                print('No appointments have been scheduled.')
            else:
                for appt in appointments:
                    print(appt)
        else:
            print('Thank for using our system')

if __name__ == "__main__":
    main()