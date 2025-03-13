from tkinter import * # Importē visas tkinter pamata funkcijas

from tkinter.ttk import * # Importē ttk (stilizētus) logrīkus no tkinter

from tkinter import messagebox # Importē ziņojumu logu funkcijas

import sqlite3 # Importē SQLite datubāzes bibliotēku

import hashlib # Importē bibliotēku hešēšanai

def sanemt_atbidi(atbilde): # Funkcija, lai iegūtu uzdevumu un atbildi pēc izvēlētā grūtības līmeņa
    
    datu_baze = "matematikas_uzdevumi.db" # Saglaba datu bazes nosaukumu mainīgajā

    with sqlite3.connect(datu_baze) as savienojums: #Izveido savienojumu
        
        curs = savienojums.cursor() #Piesledza kursoru, lai būtu iespēja izvēlēties informāciju
        
        # Izveido pieprasījumu datu bazei
        curs.execute('''
            SELECT id, uzdevums, atbilde
            FROM uzdevumi
            WHERE sarezgitiba = ?
            ORDER BY RANDOM()
            LIMIT 1
        ''', (atbilde,))
        
        rezultats = curs.fetchone() # Atgriež vienu pieprasījuma elementu
        
    if rezultats is None:  # Ja nav atrasts neviens uzdevums
        
        # Atgriež paziņojumu, ka uzdevuma nav
        return (None, "Nav pieejamu uzdevumu!", "Nav pieejamas atbildes!")

    return rezultats # Atgriež rezultātu kā sarakstu [id, uzdevums, atbilde]
    
def parbaudit_lietotaju(username, password): # Funkcija, lai pārbaudītu lietotāja autentifikāciju
    
    datu_baze = "matematikas_uzdevumi.db" # Saglaba datu bazes nosaukumu mainīgajā
    
    with sqlite3.connect(datu_baze) as savienojums: #Izveido savienojumu
        
        curs = savienojums.cursor() #Piesledza kursoru, lai būtu iespēja izvēlēties informāciju
        
        # Izveido pieprasījumu datu bazei
        curs.execute("SELECT * FROM users WHERE logins = ? AND parole = ?", (username, password))
        
        return curs.fetchone() is not None # Atgriež True, ja lietotājs eksistē, citādi False

# Galvenā klase, kas pārvalda lietotni
class GalvenaisKlass(Tk):
    
    def __init__(self): # Inicializē klases īpašības un mainīgos
        
        super().__init__() # Mantos informāciu no Tk klases
        
        self.title("Matematikas Treineris") # Iestata loga virsrakstu
        
        self.geometry("800x400") # Definē loga izmēru
         
        self.selected_difficulty = StringVar() # Mainīgais izvēlētajam grūtības līmenim
        
        self.username = StringVar() # Mainīgais lietotājvārdam
        
        self.uzdevums_id = None # Saglabās uzdevuma ID
        
        self.container = Frame(self) # Galvenais konteineris lapām
        
        self.container.pack(fill="both", expand=True) # Iepako konteineri lapām
         
        self.frames = {}  # Saglabās visas lapas
        
        self.ielogotais_lietotajs = None  # Saglabā ielogoto lietotāju
                
        # Pievieno visas lapas
        for F in (IelogosanasLapa, Sakumlapa, GalvenaLapa, UzdevumaLapa, AtbildesLapa, RegistracijasLapa, AdminLapa):
            
            frame = F(self.container, self) # Izveido katru lapu
            
            self.frames[F] = frame # Saglabā to vārdnīcā
            
            self.grid_columnconfigure(0, weight=1)  # Padara kolonnu elastīgu
        
            self.grid_rowconfigure(0, weight=1)  # Vienmērīgi sadala rindu augstumus
            
            frame.grid(row=1, column=1, sticky="nsew") # Izvieto logā

        self.paradit_lapu(IelogosanasLapa) # Rāda pirmo lapu - ielogošanos
    
    def paradit_lapu(self, page): # Funkcija, lai parādītu konkrētu lapu
        
        # Ja tiek atvērta Galvenā lapa, atiestata mainīgos
        if page == GalvenaLapa:
            
            self.selected_difficulty.set("") # Izdzēš izvēlēto grūtības līmeni
            
            self.uzdevums_id = None # Definē uzdevuma ID
            
            self.uzdevums_text = None # Definē uzdevuma tekstu
            
            self.uzdevums_atbilde = None  # Definē uzdevuma atbildi
            
        if page == Sakumlapa: # Ja lietotājs atver sakuma lapu
            
            self.frames[Sakumlapa].atjaunot_lapu()  # Atjaunina lapu
            
            self.frames[page].tkraise() # Parada lapu
            
        # Ja tiek atvērta Uzdevuma lapa, sagatavo uzdevumu    
        if page == UzdevumaLapa:
            
            if self.uzdevums_id is None:  # Ja vēl nav izvēlēts uzdevums
                
                # Izsauc funkciju, kas atrod atbilstošu uzdevumu pēc izvēlētā grūtības līmeņa
                rezultats = sanemt_atbidi(self.selected_difficulty.get())
                
                # Saglabā iegūto uzdevuma ID, tekstu un atbildi
                self.uzdevums_id, self.uzdevums_text, self.uzdevums_atbilde = rezultats
            
            # Atjauno uzdevuma informāciju lapā    
            self.frames[UzdevumaLapa].atjaunot_uzdevumu(self)
        
        # Ja tiek atvērta Atbildes lapa, atjauno atbildes informāciju    
        if page == AtbildesLapa:
            
            # Atjauno lapu ar pareizo atbildi
            self.frames[AtbildesLapa].atjaunot_atbildi(self)
        
        # Parāda izvēlēto lapu (novieto to priekšplānā)    
        self.frames[page].tkraise()
        
class IelogosanasLapa(Frame): # Ielogošanās lapa, kur lietotājs ievada savus datus
    
    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Inicializē Frame klasi
        
        self.grid_columnconfigure(0, weight=1)  # Padara kolonnu elastīgu
        
        self.grid_rowconfigure(0, weight=1)  # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Definē loga ramīti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        # Virsraksts "Ielogoties"
        Label(frame, text="Ielogoties", font=("Arial", 16)).pack()
        
        Label(frame, text="Lietotājvārds:").pack() # Lietotājvārda ievades etiķete
        
        # Ievades lauks lietotājvārda ievadei
        self.username_entry = Entry(frame, textvariable=controller.username)
        
        self.username_entry.pack() # Iepako ievades lauku
        
        Label(frame, text="Parole:").pack() # Paroles ievades etiķete
        
        self.password_entry = Entry(frame, show="*") # Ievades lauks parolei (slēpts)
        
        self.password_entry.pack() # Iepako ievades lauku
        
        
        # Poga, kas izsauc pieslēgšanās funkciju
        Button(frame, text="Ielogoties",
                command=lambda: self.pareizi_pieslegties(controller)).pack()
        
        # Poga, kas parada lapu lietotāja reģistēšanai
        Button(frame, text="Uz reģīstrācijas lapu",
                command=lambda: (controller.paradit_lapu(RegistracijasLapa),
                                 self.username_entry.delete(0, END), # Vizuāli notira logina ievades lauku 
                                 self.password_entry.delete(0, END))).pack() # Vizuāli notira paroles ievades lauku
        
    # Funkcija, kas pārbauda ievadītos datus un ielogo lietotāju
    def pareizi_pieslegties(self, controller):
        
        username = self.username_entry.get() # Sanem lietotāja loginu
        
        password = self.password_entry.get() # Saņem lietotāja paroli
        
        # Parbauda, ja nav ievadīts vai logins vai nu parole
        if not username or not password:
            
            # Parada kļudu
            messagebox.showerror("Kļūda", "Lūdzu, aizpildiet visus laukus!")
            
            return # Neko neatgriež 

        # Hešē lietotāja ievadito paroli
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        datu_baze = "matematikas_uzdevumi.db" # Saglaba datu bazes nosaukumu mainīgajā
        
        with sqlite3.connect(datu_baze) as savienojums: #Izveido savienojumu
            
            curs = savienojums.cursor()#Piesledza kursoru, lai būtu iespēja izvēlēties informāciju

            # Pārbauda, vai lietotājvārds un parole sakrīt
            curs.execute("SELECT * FROM users WHERE logins = ? AND parole = ?", (username, hashed_password))
            
            if curs.fetchone(): # Ja tiek atgriezts viens pieprasījuma elements
                
                # Parāda veiksmīgu paziņojumu
                messagebox.showinfo("Veiksmīgi", "Ielogošanās veiksmīga!")
                
                # Atgriež lietotāju uz  sakumlapu
                controller.paradit_lapu(Sakumlapa)
                
            else: # Citādi
                
                # Parada kļudu
                messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole!")
                
            self.username_entry.delete(0, END) # Vizuāli notira logina ievades lauku 
        
            self.password_entry.delete(0, END) # Vizuāli notira paroles ievades lauku 

class Sakumlapa(Frame): # Sākuma lapa
    
    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases
        
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.grid_rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Definē loga ramīti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        # Parada virsraksts
        Label(frame, text="Matemātikas Treineris",
                    font=("Arial", 18)).pack(pady=10)
        
        # Poga, lai sāktu darbu
        Button(frame, text="Sakt darbu", 
                  command=lambda: controller.paradit_lapu(GalvenaLapa)).pack()
        
        # Izveido pogu atgriešanai ielogošanas lapā
        Button(frame, text="Atpakaļ", command=lambda:
                    controller.paradit_lapu(IelogosanasLapa)).pack()
        
        # Poga "Rediģēt"
        self.rediget_poga = Button(frame, text="Rediģēt",
                                        command=lambda: controller.paradit_lapu(AdminLapa))
                
        self.rediget_poga.pack() # Sākumā tiek pievienota, bet to paslēpsim atkarībā no lietotāja
        
        self.atjaunot_lapu() # Pārbaudām, vai jāslepj poga
        
    def atjaunot_lapu(self): # Pārbauda, vai lietotājs ir admin, un attiecīgi rādām pogu
        
        if self.controller.username.get() == "admin": # ja ir lietotājs ir admins
            
            self.rediget_poga.pack()  # Rāda pogu "Rediģēt"
            
        else: # Ja lietotājs nav admins
            
            self.rediget_poga.pack_forget()  # Slēpj pogu
                
    def pabeigt_programmu(self): # Pabeidz programmu un parāda paziņojumu
        
        # Atvadu ziņojums ar lietotāja vardu
        messagebox.showinfo("Visu labu", f"Visu labu, {self.master.username.get()}!")
        
        self.master.quit() # Programmas iziešana
        
class GalvenaLapa(Frame): # Galvenā lapa, kur lietotājs izvēlas grūtības līmeni
    
    def __init__(self,parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases
        
        self.columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Definē loga ramīti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        # Parada virsrakstu
        Label(frame, text="Izvēlēties grūtības līmeņi",
                    font=("Arial", 14)).pack(pady=10)
        
        varianti = ["viegls", "videjais", "gruts"] # Grūtības līmeņu saraksts
        
        # Kombinētais lauks grūtības līmeņa izvēlei
        self.komboboks = Combobox(frame, values=varianti,
                                  textvariable=controller.selected_difficulty)
        
        self.komboboks.pack() # Iepako komboboks lauku
        
         # Poga "Turpināt"                
        Button(frame, text="Paradīt Uzdevumu",
                    command=lambda: self.parbaudit_un_paradit(controller)).pack(padx=10)
        
        # Izveido pogu atgriešanai sakuma lapā
        Button(frame, text="Atpakaļ", command=lambda:
                    controller.paradit_lapu(Sakumlapa)).pack()
        
        # Poga "Pabeigt darbu"
        Button(frame, text="Pabeigt Darbu", command=controller.quit).pack(pady=10) 
        
        
    def parbaudit_un_paradit(self, controller): # Funkcija, kas pārbauda izvēlēto līmeni
        
        if not self.komboboks.get(): # Parbauda, vai komboboks laukā ir kaut kas izvēlēts 
            
            # Ja nekas nav izvēlēts, izmet kļūdu
            messagebox.showerror("Kļūda", "Lūdzu, izvēlieties grūtības līmeni!")
            
        else:# Saglabā izvēlēto līmeni
            
            controller.selected_difficulty.set(self.komboboks.get()) #Saņem komoboboks vertību
            
            controller.paradit_lapu(UzdevumaLapa) # Pāriet uz uzdevuma lapu
            
            self.komboboks.delete(0, END) # Notira kombobox vertību
    
        
class UzdevumaLapa(Frame): # Lapa, kurā tiek attēlots uzdevums

    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases
        
        self.columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Definē loga ramīti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        # Teksta etiķete uzdevuma parādīšanai
        self.label = Label(frame, text=f"Uzdevums: ", font=("Arial", 14))
        
        self.label.pack(pady=10) # Iepako uzdevuma tekstu
        
        # Poga "Parādīt atbildi"
        Button(frame, text="Parādīt Atbildi",
               command=lambda: controller.paradit_lapu(AtbildesLapa)).pack()
                
    def atjaunot_uzdevumu(self, controller): # Funkcija, kas ielādē uzdevumu
        
        # Parada uzdevuma tekstu uz ekrāna
        self.label.config(text=f"Uzdevums: {controller.uzdevums_text}")

class AtbildesLapa(Frame): # Lapa, kurā tiek attēlota atbilde
    
    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases
        
        self.columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Definē loga ramīti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        # Teksta etiķete atbildes parādīšanai
        self.label = Label(frame, text=f"Atbilde: ",
                           font=("Arial", 14))
        
        self.label.pack(pady=10) # Iepako atbildes tekstu
        
        # Poga "Atgriezties"
        Button(frame, text="Atgriezties Uz Galveno Lapu",
               command=lambda: self.parbaudit_atbildi(controller)).pack()
        
    def atjaunot_atbildi(self, controller): # Funkcija, kas ielādē atbildi
        
        # Parada atbildes tekstu uz ekrana 
        self.label.config(text=f'''Atbilde: {controller.uzdevums_atbilde}''')
        
     # Funkcija, kas parbauda vai lietotājs pareizi atrisināja uzdevumu    
    def parbaudit_atbildi(self, controller):
        
        #Ziņojums ar jautājumu
        zinojums = messagebox.askyesno("Jautājums",
                                        "Vai Jūsu atbilde ir tāda pati kā ekrānā?")
        
        if zinojums: # Ja atbilde ir "Jā"
            
            #Izvada ziņojumu
            messagebox.showinfo("Ziņojums", "Jūs esat malacis!")
            
        else: # Ja atilde ir "Nē"
            
            #Izvada ziņojumu
            messagebox.showinfo("Ziņojums", "Jums jātrenējas vairāk!")
            
        controller.paradit_lapu(GalvenaLapa) #Paradā galvenu lapu

class RegistracijasLapa(Frame): # Izveido klasi RegistracijasLapa, logu reģistrācijas forma
    
    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases

        self.columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Izveido rāmiti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()

        Label(frame, text="Reģistrācija", font=("Arial", 16)).pack()  # Izveido virsraksta uzrakstu

        Label(frame, text="Lietotājvārds:").pack() # Izveido uzrakstu lietotājvārdam
        
        self.username_entry = Entry(frame) # Izveido ievades lauku lietotājvārdam
        
        self.username_entry.pack() # Iepako ievades lauku lietotājvārdam

        Label(frame, text="Parole:").pack() # Izveido uzrakstu paroles ievadei
        
        self.password_entry = Entry(frame, show="*")  # Izveido paroles ievades lauku ar maskētiem simboliem
        
        self.password_entry.pack() # Attēlo paroles ievades lauku
        
    
        # Izveido pogu "Reģistrēties" un piesaista funkciju, kas saglabā lietotāju datubāzē
        Button(frame, text="Reģistrēties",
               command=lambda: self.registret_lietotaju(controller)).pack()
        
        # Izveido pogu "Atpakaļ", kas atgriežas uz iepriekšējo (IelogosanasLapa) logu
        Button(frame, text="Atpakaļ",
               command=lambda: (controller.paradit_lapu(IelogosanasLapa), 
                                self.username_entry.delete(0, END), # Vizuāli notira logina ievades lauku
                                self.password_entry.delete(0, END))).pack() # Vizuāli notira paroles ievades lauku
    
    # Funkcija lietotāja reģistrācijai
    def registret_lietotaju(self, controller):
        
        username = self.username_entry.get() # Iegūst ievadīto lietotājvārdu
        
        password = self.password_entry.get() # Iegūst ievadīto paroli
        
        if not username or not password: # Pārbauda, vai abi lauki ir aizpildīti
            
            # Parāda kļūdas paziņojumu
            messagebox.showerror("Kļūda", "Lūdzu, aizpildiet visus laukus!")
            
            return # Pārtrauc funkcijas izpildi, ja lauki nav aizpildīti
        
        if username.lower() != "admin": # Ja admina vēl nav, tad to var pievienot
            
            # Hešē lietotāja paroli
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
            datu_baze = "matematikas_uzdevumi.db" # Saglaba datu bazes nosaukumu mainīgajā
            
            with sqlite3.connect(datu_baze) as savienojums: # Izveido savienijumu ar datu bāzi
                
                curs = savienojums.cursor() # Izveido datubāzes kursoru

                # Pārbauda, vai lietotājvārds jau eksistē
                curs.execute("SELECT * FROM users WHERE logins = ?", (username,))
                
                if curs.fetchone(): # Ja tiek atrasts jau eksistējošs lietotājs
                    
                    # Parāda kļūdas paziņojumu
                    messagebox.showerror("Kļūda", "Šis lietotājvārds jau eksistē!")
                    
                    return # Pārtrauc funkcijas izpildi, ja lietotājvārds jau pastāv

                # Pievieno jauno lietotāju
                curs.execute("INSERT INTO users (logins, parole) VALUES (?, ?)", (username, hashed_password))
                
                savienojums.commit() # Saglabā izmaiņas datubāzē
                
                # Parāda veiksmīgas reģistrācijas paziņojumu
                messagebox.showinfo("Veiksmīgi", "Lietotājs veiksmīgi reģistrēts!")
                
            controller.paradit_lapu(Sakumlapa) # Pēc reģistrācijas pāriet uz sākumlapu
            
        else: # Ja nē
            
            # Parādā klūdu
            messagebox.showerror("Kļūda", "Admins jau eksistē!")
            
            self.username_entry.delete(0, END) # Notira logina lauku
            
            self.password_entry.delete(0, END) # Notira paroles lauku
            
class AdminLapa(Frame): # Izveido klasi adminam
    
    def __init__(self, parent, controller): # Inicializē klases īpašības un mainīgos
        
        super().__init__(parent) # Mantos informāciu no Frame klases
        
        self.columnconfigure(0, weight=1) # Padara kolonnu elastīgu
        
        self.rowconfigure(0, weight=1) # Vienmērīgi sadala rindu augstumus
        
        frame = Frame(self) # Izveido rāmiti
        
        frame.grid(row=0, column=0, sticky="nsew") # Iepako ramīti ar grid()
        
        self.controller = controller # Saglabā atsauci uz galveno kontrolleri, lai varētu pārslēgt lapas
        
        Label(frame, text="Pievienot jaunu uzdevumu").pack() # Izveido virsrakstu jaunam uzdevumam
        
        Label(frame, text="Uzdevums:").pack() # Izveido tekstu, kas apzīmē uzdevuma ievades lauku
        
        self.uzdevums_entry = Entry(frame) # Izveido ievades lauku, kur lietotājs var ierakstīt uzdevumu
        
        self.uzdevums_entry.pack() # Iepako ievades lauku logā
        
        Label(frame, text="Atbilde:").pack() # Izveido tekstu, kas apzīmē atbildes ievades lauku
        
        self.atbilde_entry = Entry(frame) # Izveido ievades lauku atbildei
        
        self.atbilde_entry.pack() # Iepako ievades lauku logā
        
        Label(frame, text="Sarežģītība:").pack() # Izveido tekstu, kas apzīmē sarežģītības ievades lauku
        
        self.sarezgitiba_entry = Entry(frame) # Izveido ievades lauku sarežģītības līmeņa ievadīšanai
        
        self.sarezgitiba_entry.pack() # Iepako ievades lauku logā
        
        # Izveido pogu uzdevuma saglabāšanai un piesaista funkciju
        Button(frame, text="Saglabāt", command=self.pievienot_uzdevumu).pack() 
        
        # Izveido pogu atgriešanai galvenajā lapā
        Button(frame, text="Atpakaļ", command=lambda:
                    controller.paradit_lapu(Sakumlapa)).pack()

    def pievienot_uzdevumu(self): # Saglabā jaunu uzdevumu datubāzē
        
        uzdevums = self.uzdevums_entry.get() # Iegūst ievadīto uzdevumu
        
        atbilde = self.atbilde_entry.get() # Iegūst ievadīto atbildi
        
        sarezgitiba = self.sarezgitiba_entry.get() # Iegūst ievadīto sarežģītības līmeni
        
        if uzdevums and atbilde and sarezgitiba: # Pārbauda, vai visi lauki ir aizpildīti
            
            conn = sqlite3.connect("matematikas_uzdevumi.db") # Izveido savienojumu ar datubāzi
            
            cursor = conn.cursor() # Izveido kursoru, lai izpildītu SQL komandas
            
            cursor.execute("INSERT INTO uzdevumi (uzdevums, atbilde, sarezgitiba) VALUES (?, ?, ?)",
                                (uzdevums, atbilde, sarezgitiba)) # Ievieto jaunus datus datubāzē
            
            conn.commit() # Saglabā izmaiņas datubāzē
            
            conn.close() # Aizver savienojumu ar datubāzi
            
            # Parāda paziņojumu par veiksmīgu saglabāšanu
            messagebox.showinfo("Veiksmīgi", "Uzdevums pievienots!")
            
            self.uzdevums_entry.delete(0, END) # Notira uzdevuma lauku
            
            self.atbilde_entry.delete(0, END) # Notira atbilžu lauku
            
            self.sarezgitiba_entry.delete(0, END) # Notira sarežģitības lauku
            
        else: # Ja kāds no laukiem nav aizpildīts
            
            messagebox.showerror("Kļūda", "Aizpildiet visus laukus!") # Parāda kļūdas ziņojumu
            
if __name__ == "__main__": # Programmas palaišanas punkts
    
    app = GalvenaisKlass() # Izveido galveno logu
    
    app.mainloop() # Palaid Tkinter programmu