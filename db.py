# Querying, inserting, updating, and deleting from the database
#
# By: Annika Wille
import sqlite3
from datetime import *
from datetime import date

class Database:
    def __init__(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            self.cur = self.conn.cursor()
        except Error as e:
            print(e)

    # query that finds all providers that have worked more appointments
    # than average within their department
    def fetch_providers(self):
        self.cur.execute("SELECT Provider.ProviderId, Provider.Name, Provider.Title, \
                        (AptCount.AppointmentCount - avgByDept.AverageNum) AS 'Hours Above Average' \
                            FROM (SELECT count(*) AS AppointmentCount, Provider.ProviderId, Provider.Title \
                                    FROM Appointment \
                                    JOIN Provider On Appointment.ProviderId = Provider.ProviderId \
                                    GROUP BY Provider.ProviderId) as aptCount \
                            LEFT JOIN (SELECT avg(aptCount.c) AS AverageNum, * FROM ( \
                                            SELECT count(*) AS c, Provider.ProviderId, Provider.Title \
                                            FROM Appointment \
                                            JOIN Provider On Appointment.ProviderId = Provider.ProviderId \
                                            GROUP BY Provider.ProviderId) AS aptCount \
                                        GROUP BY aptCount.Title ) AS avgByDept ON aptCount.Title = avgByDept.Title \
                            JOIN Provider ON Provider.ProviderId = aptCount.ProviderId \
                            WHERE aptCount.AppointmentCount > avgByDept.AverageNum \
                            ORDER BY Provider.Title, AptCount.AppointmentCount - avgByDept.AverageNum DESC")
        rows = self.cur.fetchall()
        return rows

    # return all patients that a provider has appointments with today
    def fetch_patients(self, id, date):
        self.cur.execute("SELECT Patient.SSN, Patient.Name, Appointment.Time, Appointment.Description \
                            FROM Appointment JOIN Patient ON Appointment.SSN = Patient.SSN \
                            JOIN Provider ON Appointment.ProviderId = Provider.ProviderId \
                            WHERE Provider.ProviderId = ? AND Appointment.Date = ? \
                            ORDER BY Appointment.Time ASC", (id, date,))
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            self.check_age(row[0])
            sub_data = []
            sub_data.append(row[1])
            sub_data.append(row[2])
            sub_data.append(self.find_possible_vaccines(row[0]))
            sub_data.append(self.find_missed_vaccines(row[0]))
            sub_data.append(row[3])
            sub_data.append(row[0])
            data.append(sub_data)
        return data
    
    # updating age attribute in the tuples of patients that a provider
    # sees  that current day, done before checking potential vaccinations
    # and missed vaccinations
    def check_age(self, ssn):
        self.cur.execute("SELECT Age, Birthdate FROM Patient \
                            WHERE Patient.SSN = ?", (ssn,))
        a = self.cur.fetchall()
        age = a[0][0]
        birth = a[0][1]
        birth = d = datetime.strptime(birth, '%Y-%m-%d')
        today = date.today()
        checked_age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        if (checked_age != age):
            self.cur.execute("UPDATE Patient SET AGE = ? WHERE SSN = ?", (checked_age, ssn,))
        self.conn.commit()

    # insert new patient into database
    def add_patient_db(self, ssn, name, birthdate, id):
        birth = datetime.strptime(birthdate, '%Y-%m-%d')
        today = datetime.today().date()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        self.cur.execute("INSERT INTO Patient (SSN, Name, Birthdate, Age, ProviderId) VALUES (?, ?, ?, ?, ?)", (ssn, name, birthdate, age, id))
        self.conn.commit()
    
    # delete patient from database
    def del_patient_db(self, ssn):
        self.cur.execute("DELETE FROM Patient WHERE Patient.SSN = ?", (ssn,))
        self.cur.execute("DELETE FROM Appointment WHERE Appointment.SSN = ?", (ssn,))
        self.cur.execute("DELETE FROM ImmunizationHistory WHERE ImmunizationHistory.SSN = ?", (ssn,))
        self.conn.commit()
    
    # delete appointment from database
    def del_appt_db(self, ssn, date, time, id):
        self.cur.execute("DELETE FROM Appointment WHERE SSN = ? AND Date = ? AND TIME = ? AND ProviderId = ?", (ssn, date, time, id,))
        self.conn.commit()
 
    # add immunization history record to the database
    def add_vax_db(self, ssn, immid, date):
        self.cur.execute("INSERT INTO ImmunizationHistory (SSN, ImmId, Date) VALUES (?, ?, ?)", (ssn, immid, date,))
        self.conn.commit()

    # add appointment to the database
    def add_appt_db(self, ssn, date, time, desc, id):
        self.cur.execute("INSERT INTO Appointment (Date, Time, Description, SSN, ProviderId) VALUES (?, ?, ?, ?, ?)", (date, time, desc, ssn, id))
        self.conn.commit()

    # query that returns all possible vaccinations for a patient
    # based on both their current age and their prior immunization history
    def find_possible_vaccines(self, ssn):
        self.cur.execute("SELECT subq2.Name FROM \
                                (SELECT * \
                                FROM ImmunizationList \
                                WHERE (SELECT Age FROM Patient WHERE SSN = ?) > ImmunizationList.minAge \
                                AND (SELECT Age FROM Patient \
                                        WHERE SSN = ?) < ImmunizationList.maxAge) AS subq1 \
                                JOIN (SELECT * FROM ImmunizationList \
                                        LEFT JOIN (SELECT * FROM ImmunizationHistory \
                                                    WHERE SSN = ?) AS PatientRecord \
                                        ON ImmunizationList.ImmId = PatientRecord.ImmId \
                                        WHERE PatientRecord.SSN IS NULL) AS subq2 \
                            ON subq1.ImmId = subq2.ImmId", (ssn, ssn, ssn))
        possible_rows = self.cur.fetchall()
        return possible_rows 

    # query to find any vaccines that a patient missed (they are too old for
    # now based on their age and past immunization history
    def find_missed_vaccines(self, ssn):
        self.cur.execute("SELECT ImmunizationList.Name FROM ImmunizationList \
                            NATURAL LEFT JOIN (SELECT * FROM ImmunizationHistory WHERE ImmunizationHistory.SSN = ?) AS q \
                            WHERE q.SSN IS NULL AND (SELECT Age FROM Patient WHERE Patient.SSN = ?) > ImmunizationList.maxAge", (ssn, ssn,))
        missed_rows = self.cur.fetchall()
        return missed_rows