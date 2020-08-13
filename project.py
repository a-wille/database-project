# Program that helps providers determine whether a patient needs/is 
# eligible for a vaccination based on their age and immunization history. 
# This program also displays missed vaccinations for patients and the 
# providers who have worked more appointments than average within their 
# department. 
#
# This page is mostly for the formatting of Tkinter and how the program
# connects to the database and in what ways.
#
# By: Annika Wille

from tkinter import *
from tkinter import ttk
from PIL import Image
from datetime import datetime
from tkinter import messagebox
import db
from provider import provider
import re

admin_users = ['jryan']
provider_users = ['awille', 'mjohnson', 'ebart', 'jeaston', 'lwest', 'cwalker', 'bschaefer', \
            'tgreen', 'olongmore', 'estrange', 'lwallace', 'gdavis', 'ejames', 'bsmith', 'sgordon']

# create windows and base objects
class Display:
    def __init__(self):
        self.root = Tk()
        self.row_count = 0
        background_image = PhotoImage(file="login.gif")
        self.w, self.h = background_image.width(), background_image.height() - 200
        self.root.configure(background = 'SteelBlue3')
        self.root.geometry("%dx%d" % (self.w, self.h))
        self.login = Canvas(self.root, width = self.w, height = self.h)
        self.login.configure(background = "white")
        self.root.title("Hospital Application Login")
        self.login.create_image(self.w/2, self.h/2, image=background_image)
        self.root.resizable(True, True)
        
        # Username
        self.user_text = StringVar()
        self.login.create_text(self.w/2-85, self.h/2-30, text="Enter Username:", font=('MS Sans Serif', 14), fill="white")
        self.user_entry = Entry(self.login, textvariable=self.user_text)
        self.login.create_window(self.w/2+85, self.h/2-30, window=self.user_entry)

        # Password
        self.password_text = StringVar()
        self.login.create_text(self.w/2-85, self.h/2, text="Enter Password:", font=('MS Sans Serif', 14), fill="white")
        self.password_entry = Entry(self.login, show="*", textvariable=self.password_text)
        self.login.create_window(self.w/2+85, self.h/2, window=self.password_entry)

        self.enter_button = ttk.Button(self.login, text="Login", command=self.try_login)
        self.b_w = self.login.create_window(self.w/2, self.h/2+50, window=self.enter_button)
        self.login.pack()
        self.close_bool = True
        self.root.protocol("WM_DELETE_WINDOW", self.restart_window)
        self.root.mainloop()
        self.login.mainloop()
    
    def restart_window(self):
        self.root.destroy()
        if not self.close_bool:
            display = Display()

    def update_root_size(self):
        width, height = self.root.grid_size()
        height = height * 35
        self.root.geometry("%dx%d" % (self.w + 325, height))

    def try_login(self):
        data = []
        provider_user = False
        admin_user = False
        self.user = self.user_entry.get()
        for user in provider_users:
            if user == self.user:
                provider_user = True
        for user in admin_users:
            if user == self.user:
                admin_user = True
        
        if provider_user and self.password_entry.get() == "password":
            self.login.destroy()
            self.root.title("Appointments and Patient Information")
            self.date = datetime.date(datetime.now())
            self.conn = db.Database("./vaccinedb")
            p = provider()
            self.id = p.get_provider_id(self.user)
            data = self.conn.fetch_patients(self.id, self.date)
            self.display_data(data)
        
        if admin_user and self.password_entry.get() == "password":
            self.login.destroy()
            self.root.title("Admin Page")
            self.conn = db.Database("./vaccinedb")
            data = self.conn.fetch_providers()
            self.display_provider_data(data)

    def display_provider_data(self, data):
        self.close_bool = False
        admin = Label(text="Providers Who Worked More Appointments Than Average Within Their Department", bg='SteelBlue4', fg="white")
        admin.grid(row=self.row_count, column = 0, columnspan=4, padx=5, pady=5, sticky='nsew')
        self.row_count += 1
        id = Label(text="ID", bg='SteelBlue4', fg="white")
        id.grid(row=self.row_count, column = 0, padx=5, pady=5, sticky='nsew')
        provider = Label(text="Provider", bg='SteelBlue4', fg="white")
        provider.grid(row=self.row_count, column = 1, padx=5, pady=5, sticky='nsew')
        dept = Label(text="Department", bg='SteelBlue4', fg="white")
        dept.grid(row=self.row_count, column = 2, padx=5, pady=5, sticky='nsew')
        above = Label(text="Number of Appointments Above Average", bg='SteelBlue4', fg="white")
        above.grid(row=self.row_count, column = 3, padx=5, pady=5, sticky='nsew')
        self.row_count += 1
        for item in data:
            l = Label(text=item[0], bg='SteelBlue2', width=5)
            l.grid(row=self.row_count, column=0, padx=5, pady=5)
            descrip = Label(text=item[1], bg="SteelBlue2", width = 25)
            descrip.grid(row=self.row_count, column=1, padx=5, pady=5)
            ssi = Label(text=item[2], bg="SteelBlue2", width=12)
            ssi.grid(row=self.row_count, column=2, padx=5, pady=5)
            formatted = str(item[3])
            formatted = formatted[:3]
            name = Label(text=formatted, bg='SteelBlue2', width=40)
            name.grid(row=self.row_count, column=3, padx=5, pady=5)
            
            self.root.columnconfigure(0, uniform="group2")
            self.root.columnconfigure(1, uniform="group1")
            self.root.columnconfigure(2, uniform="group3")
            self.root.columnconfigure(3, uniform="group4")
            self.row_count += 1

        width, height = self.root.grid_size()
        height = height * 33
        width = width * 180
        self.root.geometry("%dx%d" % (width, height))
    
    def add_buttons(self):
        add = Button(self.root, text="Add Patient", command=self.add_patient, bg='SteelBlue4', fg="white")
        add.grid(row = self.row_count, column=3, padx=5, pady=5, sticky='ew')
        del_p = Button(self.root, text="Delete Patient", command=self.del_patient, bg='SteelBlue4', fg="white")
        del_p.grid(row = self.row_count+1, column=3, padx=5, pady=5, sticky='ew')
        apt = Button(self.root, text="Add Appointment", command = self.add_appt, bg='SteelBlue4', fg="white")
        apt.grid(row=self.row_count, column=4, padx=5, pady=5, sticky='ew')
        del_a = Button(self.root, text="Delete Appointment", command=self.del_appt, bg='SteelBlue4', fg="white")
        del_a.grid(row = self.row_count+1, column=4, padx=5, pady=5, sticky='ew')
        vax = Button(self.root, text="Add Vaccination", command = self.add_vacc, bg='SteelBlue4', fg="white")
        vax.grid(row=self.row_count, column=5, padx=5, pady=5, sticky='ew')

    def del_patient(self):
        self.new = Toplevel(self.root)
        self.new.title("Delete Patient")
        self.new.geometry("400x100")
        self.new.configure(bg="SteelBlue3")
        ssn = Label(self.new, text="SSN: ", width=15, bg="SteelBlue4", fg="white")
        ssn.grid(row=0, column=0, padx=10, pady=10)
        self.ssn_text = StringVar()
        self.ssn_text.set("XXX-XX-XXXX")
        self.ssne = Entry(self.new, textvariable=self.ssn_text, width=28)
        self.ssne.grid(row=0, column=1, padx=10, pady=10)

        del_button = Button(self.new, text="Delete Patient", command = self.update_del_patient, bg='SteelBlue4', fg="white")
        del_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
    
    def update_del_patient(self):
        self.conn.del_patient_db(self.ssn_text.get())
        for item in self.root.grid_slaves():
            item.grid_forget()
        self.row_count=0
        data = self.conn.fetch_patients(self.id, self.date)
        self.display_data(data)
        self.new.destroy()
        self.update_root_size()
    
    def del_appt(self):
        self.new = Toplevel(self.root)
        self.new.title("Delete Appointment")
        self.new.geometry("400x200")
        self.new.configure(bg="SteelBlue3")
        ssn = Label(self.new, text="SSN: ", width=15, bg="SteelBlue4", fg="white")
        date = Label(self.new, text="Date: ", width=15, bg="SteelBlue4", fg="white")
        time = Label(self.new, text="Time: ", width=15, bg="SteelBlue4", fg="white")
        ssn.grid(row=0, column=0, padx=10, pady=10)
        date.grid(row=1, column=0, padx=10, pady=10)
        time.grid(row=2, column=0, padx=10, pady=10)
        self.ssn_text = StringVar()
        self.date_text = StringVar()
        self.time_text = StringVar()
        self.ssn_text.set("XXX-XX-XXXX")
        self.date_text.set("YYYY-mm-dd")
        self.time_text.set("HH:mm")
        self.ssne = Entry(self.new, textvariable=self.ssn_text, width=28)
        self.ssne.grid(row=0, column=1, padx=10, pady=10)
        self.datee = Entry(self.new, textvariable=self.date_text, width=28)
        self.datee.grid(row=1, column=1, padx=10, pady=10)
        self.timee = Entry(self.new, textvariable=self.time_text, width=28)
        self.timee.grid(row=2, column=1, padx=10, pady=10)
        
        del_button = Button(self.new, text="Delete Appointment", command = self.update_del_appt, bg='SteelBlue4', fg="white")
        del_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    def update_del_appt(self):
        self.conn.del_appt_db(self.ssn_text.get(), self.date_text.get(), self.time_text.get(), self.id)
        for item in self.root.grid_slaves():
            item.grid_forget()
        self.row_count=0
        data = self.conn.fetch_patients(self.id, self.date)
        self.display_data(data)
        self.new.destroy()
        self.update_root_size()

    def add_patient(self):
        self.new = Toplevel(self.root)
        self.new.title("Add Patient")
        self.new.geometry("400x190")
        self.new.configure(bg="SteelBlue3")
        ssn = Label(self.new, text="SSN: ", width=15, bg="SteelBlue4", fg="white")
        name = Label(self.new, text="Name: ", width=15, bg="SteelBlue4", fg="white")
        bday = Label(self.new, text="Birthdate: ", width=15, bg="SteelBlue4", fg="white")
        ssn.grid(row=0, column=0, padx=10, pady=10)
        name.grid(row=1, column=0, padx=10, pady=10)
        bday.grid(row=2, column=0, padx=10, pady=10)
        self.ssn_text = StringVar()
        self.ssn_text.set("XXX-XX-XXXX")
        self.name_text = StringVar()
        self.bday_text = StringVar()
        self.bday_text.set('YYYY-mm-dd')
        self.ssne = Entry(self.new, textvariable=self.ssn_text, width=28)
        self.ssne.grid(row=0, column=1, padx=10, pady=10)
        self.namee = Entry(self.new, textvariable=self.name_text, width=28)
        self.namee.grid(row=1, column=1, padx=10, pady=10)
        self.bdaye = Entry(self.new, textvariable=self.bday_text, width=28)
        self.bdaye.grid(row=2, column=1, padx=10, pady=10)
        self.new.columnconfigure(0, uniform="group2")
        self.new.columnconfigure(1, uniform="group1")

        add_button = Button(self.new, text="Add Patient", command = self.update_patient, bg='SteelBlue4', fg="white")
        add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
    
    def update_patient(self):
        self.conn.add_patient_db(self.ssn_text.get(), self.name_text.get(), self.bday_text.get(), self.id)
        self.new.destroy()

    def add_appt(self):
        self.new = Toplevel(self.root)
        self.new.title("Add Appointment")
        self.new.geometry("400x220")
        self.new.configure(bg="SteelBlue3")
        ssn = Label(self.new, text="SSN: ", width=15, bg="SteelBlue4", fg="white")
        day = Label(self.new, text="Date: ", width=15, bg="SteelBlue4", fg="white")
        time = Label(self.new, text="Time: ", width=15, bg="SteelBlue4", fg="white")
        desc = Label(self.new, text="Description: ", width=15, bg="SteelBlue4", fg="white")
        ssn.grid(row=0, column=0, padx=10, pady=10)
        day.grid(row=1, column=0, padx=10, pady=10)
        time.grid(row=2, column=0, padx=10, pady=10)
        desc.grid(row=3, column=0, padx=10, pady=10)
        self.ssn_text = StringVar()
        self.ssn_text.set("XXX-XX-XXXX")
        self.date_text = StringVar()
        self.time_text = StringVar()
        self.time_text.set('HH:MM')
        self.desc_text = StringVar()
        self.date_text.set('YYYY-mm-dd')
        self.ssne = Entry(self.new, textvariable=self.ssn_text, width=28)
        self.ssne.grid(row=0, column=1, padx=10, pady=10)
        self.datee = Entry(self.new, textvariable=self.date_text, width=28)
        self.datee.grid(row=1, column=1, padx=10, pady=10)
        self.timee = Entry(self.new, textvariable=self.time_text, width=28)
        self.timee.grid(row=2, column=1, padx=10, pady=10)
        self.desce = Entry(self.new, textvariable=self.desc_text, width=28)
        self.desce.grid(row=3, column=1, padx=10, pady=10)
        self.new.columnconfigure(0, uniform="group2")
        self.new.columnconfigure(1, uniform="group1")

        add_button = Button(self.new, text="Add Appointment", command = self.update_appt, bg='SteelBlue4', fg="white")
        add_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
    
    def update_appt(self):
        self.conn.add_appt_db(self.ssn_text.get(), self.date_text.get(), self.time_text.get(), self.desc_text.get(), self.id)
        if self.date_text.get() == str(datetime.today().date()):
            for item in self.root.grid_slaves():
                item.grid_forget()
            self.row_count=0
            data = self.conn.fetch_patients(self.id, self.date)
            self.display_data(data)
        self.new.destroy()
        self.update_root_size()

    def add_vacc(self):
        self.new = Toplevel(self.root)
        self.new.title("Add Vaccination")
        self.new.geometry("450x520")
        self.new.configure(bg="SteelBlue3")
        header = Label(self.new, text="Vaccination and Number List", bg="SteelBlue4", fg="white")
        tdap = Label(self.new, text="1: Tdap", width=25, bg="SteelBlue4", fg="white")
        mmr = Label(self.new, text="2: MMR", width=25, bg="SteelBlue4", fg="white")
        var = Label(self.new, text="3: VAR", width=25, bg="SteelBlue4", fg="white")
        rzv = Label(self.new, text="4: RZV", width=25, bg="SteelBlue4", fg="white")
        hpv = Label(self.new, text="5: HPV", width=25, bg="SteelBlue4", fg="white")
        hepa = Label(self.new, text="6: HepA", width=25, bg="SteelBlue4", fg="white")
        hepb = Label(self.new, text="7: HepB", width=25, bg="SteelBlue4", fg="white")
        menb = Label(self.new, text="8: MenB", width=25, bg="SteelBlue4", fg="white")
        hib = Label(self.new, text="9: HIb", width=25, bg="SteelBlue4", fg="white")
        ipv = Label(self.new, text="10: IPV4", width=25, bg="SteelBlue4", fg="white")
        dtap = Label(self.new, text="11: DTaP5", width=25, bg="SteelBlue4", fg="white")
        header.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        tdap.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        mmr.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        var.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        rzv.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        hpv.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        hepa.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        hepb.grid(row=7, column=0, columnspan=2, padx=10, pady=5)
        menb.grid(row=8, column=0, columnspan=2, padx=10, pady=5)
        hib.grid(row=9, column=0, columnspan=2, padx=10, pady=5)
        ipv.grid(row=10, column=0, columnspan=2, padx=10, pady=5)
        dtap.grid(row=11, column=0, columnspan=2, padx=10, pady=5)

        ssn = Label(self.new, text="SSN: ", width=25, bg="SteelBlue4", fg="white")
        day = Label(self.new, text="Immunization Number: ", width=25, bg="SteelBlue4", fg="white")
        date = Label(self.new, text="Date: ", width=25, bg="SteelBlue4", fg="white")
        ssn.grid(row=12, column=0, padx=10, pady=5)
        day.grid(row=13, column=0, padx=10, pady=5)
        date.grid(row=14, column=0, padx=10, pady=5)
        self.ssn_text = StringVar()
        self.imm_text = StringVar()
        self.date_text = StringVar()
        self.date_text.set('YYYY-mm-dd')
        self.ssn_text.set('XXX-XX-XXXX')
        self.ssne = Entry(self.new, textvariable=self.ssn_text, width=25)
        self.ssne.grid(row=12, column=1, padx=10, pady=5)
        self.imme = Entry(self.new, textvariable=self.imm_text, width=25)
        self.imme.grid(row=13, column=1, padx=10, pady=5)
        self.datee = Entry(self.new, textvariable=self.date_text, width=25)
        self.datee.grid(row=14, column=1, padx=10, pady=5)
        
        add_button = Button(self.new, text="Add Vaccination", command = self.update_vax, bg='SteelBlue4', fg="white")
        add_button.grid(row=15, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
    
    def update_vax(self):
        self.conn.add_vax_db(self.ssn_text.get(), self.imm_text.get(), self.date_text.get())
        for item in self.root.grid_slaves():
            item.grid_forget()
        self.row_count=0
        data = self.conn.fetch_patients(self.id, self.date)
        self.display_data(data)
        self.new.destroy()

    def display_data(self, data):
        self.close_bool = False
        self.root.geometry("%dx%d" % (self.w +325, self.h - 100))
        apps = Label(text="Time", bg='SteelBlue4', fg="white")
        apps.grid(row=self.row_count, column = 0, padx=5, pady=5, sticky='nsew')
        descript = Label(text="Description", bg="SteelBlue4", fg="white")
        descript.grid(row=self.row_count, column = 1, padx=5, pady=5, sticky='nsew')
        ss = Label(text="SSN", bg="SteelBlue4", fg="white")
        ss.grid(row=self.row_count, column=2, padx=5, pady=5, sticky='nsew')
        patient = Label(text="Patient", bg='SteelBlue4', fg="white")
        patient.grid(row=self.row_count, column = 3, padx=5, pady=5, sticky='nsew')
        possible = Label(text="Potential Vaccinations", bg = 'SteelBlue4', fg="white")
        possible.grid(row=self.row_count, column=4, padx=5, pady=5, sticky='nsew')
        missed = Label(text="Missed Vaccinations", bg = 'SteelBlue4', fg=("white"))
        missed.grid(row=self.row_count, column=5, padx=5, pady=5, sticky = 'nsew')
        self.row_count += 1
        for item in data:
            l = Label(text=item[1], bg='SteelBlue2', width=10)
            l.grid(row=self.row_count, column=0, padx=5, pady=5)
            descrip = Label(text=item[4], bg="SteelBlue2", width = 25)
            descrip.grid(row=self.row_count, column=1, padx=5, pady=5)
            ssi = Label(text=item[5], bg="SteelBlue2", width=12)
            ssi.grid(row=self.row_count, column=2, padx=5, pady=5)
            name = Label(text=item[0], bg='SteelBlue2', width=20)
            name.grid(row=self.row_count, column=3, padx=5, pady=5)
            t = self.format_text(item[2])
            possible_v = Label(text=t, bg='SteelBlue2', width=45)
            possible_v.grid(row=self.row_count, column=4, padx=5, pady=5)
            t = self.format_text(item[3])
            missed_v = Label(text=t, bg='SteelBlue2', width=30)
            missed_v.grid(row=self.row_count, column=5, padx=5, pady=5)
            self.root.columnconfigure(0, uniform="group2")
            self.root.columnconfigure(1, uniform="group1")
            self.root.columnconfigure(2, uniform="group3")
            self.root.columnconfigure(3, uniform="group4")
            self.root.columnconfigure(4, uniform="group5")
            self.root.columnconfigure(5, uniform="group6")
            self.row_count += 1
        self.add_buttons()
        self.update_root_size()

    def format_text(self, l):
        t = ""
        if len(l) > 0:
            count = 0
            for vax in l:
                vax = str(vax)
                vax = re.sub(r'[^\w\s]', '', vax)
                if count == 0:
                    t = t + vax
                else:
                    t = t + ', ' + vax 
                count += 1
        else:
            t = "None"
        return t

def restart_display():
    del program
    program = Display()    

program = Display()
