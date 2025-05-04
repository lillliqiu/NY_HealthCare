import pyodbc
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

db_file= os.path.join(base_dir, "PatientDatabase","patientapointdb.accdb")
# print("Full DB Path:", db_file)
# print("Exists:", os.path.exists(db_file))


conn_str= (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    rf'DBQ={db_file};'
)

conn1 = pyodbc.connect(conn_str) #Connects to the PatientDatabase
cursor1 = conn1.cursor()


cursor1.execute("SELECT Doctor.FirstName + ' ' + Doctor.LastName AS Doctor, Appointment.AppointmentDate+ + Appointment.AppointmentTime As Schedule FROM Appointment INNER JOIN Doctor ON Appointment.DoctorID=Doctor.DoctorID;")
for i in cursor1.fetchall():
    print(i)
    