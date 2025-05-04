from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import pyodbc
import os
from appoinment_feature import create_appt
from collections import defaultdict

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(base_dir, "PatientDatabase", "patientapointdb.accdb")
conn_str = (
     r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    rf'DBQ={db_file};'
)

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/patients')
def patients():
    return render_template('patients.html')


@app.route('/appointments')
def index():
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT AppointmentID, PatientName, AppointmentDate, AppointmentTime, DoctorName, ReasonForVisit, PhoneNumber FROM Appointment")
    rows = cursor1.fetchall()

    appointments = [  #gets appt info
        {
            "AppointmentID": row.AppointmentID,
            "patient": row.PatientName,
            "date": row.AppointmentDate,
            "time": row.AppointmentTime,
            "doctor": row.DoctorName,
            "reason": row.ReasonForVisit,
            "phone": row.PhoneNumber
        } for row in rows
    ]
        #get doctor info
    cursor1.execute("SELECT LastName FROM Doctor")
    doctor_rows = cursor1.fetchall()
    doctors = [row.LastName for row in doctor_rows]
    conn1.close()

    return render_template('appointments.html', appointments= appointments, doctors=doctors)



@app.route('/book', methods=['POST'])
def book_appointment():
    try:
        data = request.get_json()
        print(f"Received data: {data}")


        patient_name = data.get('patient')
        appointment_date = data.get('date')
        appointment_time = data.get('time')
        doctor_name = data.get('doctor')
        reason_for_visit = data.get('reason')
        phone_number = data.get('phone')

        if not all([patient_name, appointment_date, appointment_time, doctor_name, reason_for_visit]):
            return jsonify({"error": "Missing info"}), 400

        conn1 = pyodbc.connect(conn_str)
        cursor1 = conn1.cursor()


        cursor1.execute(''' 
            INSERT INTO Appointment(AppointmentDate, AppointmentTime, DoctorName, ReasonForVisit, PatientName, PhoneNumber)
            VALUES (?,?,?,?,?,?)
    ''', (appointment_date, appointment_time, doctor_name, reason_for_visit, patient_name, phone_number))
        
        conn1.commit()
        conn1.close()

        return jsonify({"message": "Appointment has been booked."}), 200

    except Exception as e:
        print("Error could not book appt:", e)
        return jsonify({"error":"Could not book appt"}), 500
    finally:
        conn1.close

@app.route('/api/appointments')
def view_all_appointments():
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()
    cursor1.execute("""
        SELECT
            Appointment.AppointmentID,
            Appointment.AppointmentDate,
            Appointment.AppointmentTime,
            Appointment.DoctorName,
            Appointment.ReasonForVisit,
            Appointment.PatientName,
            Appointment.PhoneNumber 
        FROM Appointment
        LEFT JOIN Patient
        ON
            Patient.FirstName & ' ' & Patient.LastName = Appointment.PatientName
    """)
    rows = cursor1.fetchall()
    conn1.close()

    appointments = []
    for row in rows:
        appointments.append({
            "AppointmentID":row.AppointmentID,
            "patient":row.PatientName,
            "phone": row.PhoneNumber,
            "date":str(row.AppointmentDate),
            "time":str(row.AppointmentTime),
            "doctor":row.DoctorName,
            "reason":row.ReasonForVisit

        })
    
    return jsonify(appointments)
        

@app.route('/delete/<int:appointment_id>', methods=['DELETE'])
def delete_appt(appointment_id):
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()
    try:
        cursor1.execute("DELETE FROM Appointment WHERE AppointmentID = ?", (appointment_id,))
        conn1.commit()
        return '', 204
    except Exception as e:
        print('Was not able to delete the appointment.', e)
        return 'Could not delete', 500
    finally:
        conn1.close()

@app.route('/update/<int:appointment_id>', methods=['PUT'])
def update_appt(appointment_id):
    data = request.get_json()
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()

    try:
        cursor1.execute(''' 
            UPDATE Appointment
            SET PatientName = ?, AppointmentDate = ?, AppointmentTime = ?, DoctorName = ?, ReasonForVisit = ?, PhoneNumber = ?
            WHERE AppointmentID = ?
        ''', (
            data.get('patient'),
            data.get('date'),
            data.get('time'),
            data.get('doctor'),
            data.get('reason'),
            data.get('phone'),  # make sure 'phone' key exists in request
            appointment_id
        ))

        conn1.commit()
        return '', 204

    except Exception as e:
        print("Could not update appointment: ", e)
        return "Could not update", 500
    finally:
        conn1.close()

@app.route('/doctors')
def doctor():
    schedules = get_doctor_schedules()
    return render_template('doctors.html', schedules=schedules)

def get_doctor_schedules():
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()

    cursor1.execute("""
        SELECT 
            Doctor.FirstName + ' ' + Doctor.LastName AS Doctor,
            Appointment.AppointmentDate,
            Appointment.AppointmentTime
        FROM Appointment
        INNER JOIN Doctor ON Appointment.DoctorID = Doctor.DoctorID;
    """)



    schedules_by_doctor = defaultdict(list)
    for row in cursor1.fetchall():
        date_str = row.AppointmentDate.strftime("%Y-%m-%d")
        time_str = row.AppointmentTime.strftime("%H:%M:%S")
        schedules_by_doctor[row.Doctor].append(f"{date_str} at {time_str}")

    conn1.close()
    return schedules_by_doctor 

@app.route('/patients')
def patients():
    conn1 = pyodbc.connect(conn_str)
    cursor1 = conn1.cursor()

    # Fetching data from Patient and Appointment tables
    cursor1.execute("""
        SELECT 
            p.FirstName,
            p.LastName,
            p.DateOfBirth,
            a.AppointmentDate,
            a.DoctorName,
            d.Specialization,
            a.ReasonForVisit,
            a.Status,
            p.PhoneNumber
        FROM Patient p
        LEFT JOIN Appointment a ON p.PatientID = a.PatientID
        LEFT JOIN Doctor d ON a.DoctorID = d.DoctorID
    """)

    rows = cursor1.fetchall()
    patients = []

    # Prepare a list of patients with the fetched data
    for row in rows:
        patients.append({
            "first_name": row.FirstName,
            "last_name": row.LastName,
            "date_of_birth": row.DateOfBirth,
            "appointment_date": row.AppointmentDate,
            "doctor_name": row.DoctorName,
            "specialization": row.Specialization,
            "reason_for_visit": row.ReasonForVisit,
            "status": row.Status,
            "phone": row.PhoneNumber
        })

    conn1.close()

    return render_template('patients.html', patients=patients)  

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')
