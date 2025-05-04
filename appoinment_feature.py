
import pyodbc
import os
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))

db_file= os.path.join(base_dir, "PatientDatabase","patientapointdb.accdb")

conn_str= (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    rf'DBQ={db_file};'
)

conn1 = pyodbc.connect(conn_str)
cursor1 = conn1.cursor()




def create_appt(patient_name, doctor_name, date, time, reason):
    try:
        time = datetime.strptime(time, '%H:%M').time()
    except ValueError:
        return 'Use 24 hour format.'
    
    if time < datetime.strptime('8:00', '%H:%M').time() or time > datetime.strptime('20:00', '%H:%M').time():
        return 'NY Health Clinic is only open 8AM - 8PM.'
    
    cursor1.execute('SELECT * FROM Appointment WHERE DoctorName=? AND AppointmentDate=? AND AppointmentTime=?',
                   (doctor_name, date, time.strftime('%H:%M')))
    
    if cursor1.fetchone():
        return 'Sorry that time is unavailable please select a different time.'
    
    cursor1.execute('INSERT INTO Appointment (PatientName, DoctorName, AppointmentDate, AppointmentTime) VALUES (?,?,?,?)',
                   (patient_name, doctor_name, date, time.strftime('%H:%M')))
    conn1.commit()

    return f"Appointment booked for {patient_name} with {doctor_name} at {time.strftime('%H:%M')} on {date}."


def cancel_appt(patient_name, doctor_name, date, time):
    try:
        time = datetime.strptime(time, '%H:%M').time()
    except ValueError:
        return 'Use a 24 hour time format please.'
    
    time_str = time.strftime('%H:%M')
    
    cursor1.execute('''
        SELECT * FROM Appointment
        WHERE PatientName=? AND DoctorName=? AND AppointmentDate=? AND AppointmentTime=?
    ''', (patient_name, doctor_name, date, time_str))

    if not cursor1.fetchone():
        return 'Could not find an appointment to cancel'
    
    cursor1.execute('''
        DELETE FROM Appointment
        WHERE PatientName=? AND DoctorName=? AND AppointmentDate=? AND AppointmentTime=?
    ''', (patient_name, doctor_name, date, time_str))
    conn1.commit()
    return f"Your appointment for {patient_name} at {time_str} on {date} has been cancelled."

def update_appt(patient_name, doctor_name, old_date, old_time, new_date, new_time):
    try:
        old_time = datetime.strptime(old_time, '%H:%M').time()
        new_time = datetime.strptime(new_time, '%H:%M').time()
    except ValueError:
        return 'Use a 24 hour time format please.'
    
    cursor1.execute('''
        SELECT * FROM Appointment
        WHERE PatientName=? AND DoctorName=? AND AppointmentDate=? AND AppointmentTime=?
    ''', (patient_name, doctor_name, old_date, old_time.strftime('%H:%M')))
    if not cursor1.fetchone():
        return 'Could not find an appointment.'
    
    cursor1.execute('''
        SELECT * FROM Appointment
        WHERE DoctorName=? AND AppointmentDate=? AND AppointmentTime=?
    ''', (doctor_name, new_date, new_time.strftime('%H:%M')))
    if not cursor1.fetchone():
        return 'That time is not available.'
    
    cursor1.execute('''
        UPDATE Appointment
        SET AppointmentDate=?, AppointmentTime=?
        WHERE PatientName=? AND DoctorName=? AND AppointmentDate=? AND AppointmentTime=?
    ''', (new_date, new_time.strftime('%H:%M'), patient_name, doctor_name, old_date, old_time.strftime('%H:%M')))
    conn1.commit()
    return f"Appointment had been updated from {old_time.strftime('%H:%M')} on {old_date} to {new_time.strftime('%H:%M')} on {new_date}."

  
def view_all_appts(): #Data Analytics feature
    print('Here are all the Appointment.')
    cursor1.execute("SELECT * FROM Appointment")
    return cursor1.fetchall()
    

cursor1.execute("SELECT * FROM Appointment WHERE 1=0;")
column_names = [desc[0] for desc in cursor1.description]

print("Columns in Appointment table:", column_names)
