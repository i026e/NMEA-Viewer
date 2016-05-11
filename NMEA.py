#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed May 11 06:37:50 2016

@author: i026e
"""
import re
import sys
from sys import argv

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import font
    from tkinter import filedialog
else:
    import Tkinter as tk
    import tkFont as font
    import tkFileDialog as filedialog

import locale

TRANSLATIONS = {
"en_US" :{}, 
"ru_RU":{
"Unknown Record":"Неизвестная запись",
"Global Positioning System Fix Data" : "Данные о последнем определении местоположения",
"Geographic Position - Latitude/Longitude" : "Координаты, широта/долгота",
"GNSS DOP and Active Satellites" : "DOP (GPS) и активные спутники",
"GNSS Satellites in View" : "Наблюдаемые спутники",
"Recommended Minimum Specific GNSS Data" : "Рекомендуемый минимум навигационных данных",
"Course Over Ground and Ground Speed" : "Курс и скорость движения" ,
"Time and Date" : "Время и дата",
"Accuracy" : "Точность",

"Mode" : "Режим",
"UTC Time" : "Время UTC",
"UTC Date" : "Дата UTC",
"Latitude" : "Широта",
"Longitude" : "Долгота",
"Altitude" : "Высота" ,
"Azimuth" : "Азимут",
"Quality indicator" : "Индикатор качества",
"Satellites Used" : "Использовано спутников",
"Type":"Тип",
"Number of messages":"Число сообщений",
"Sequence number" : "Номер сообщения" ,
"Satellites in view" : "Видимых спутников"               
}
}

lang = locale.getdefaultlocale()[0]
LANGUAGE = lang if lang in TRANSLATIONS else "en_US"

def translate(str_):
    return TRANSLATIONS[LANGUAGE].get(str_, str_)


class Record(object):
    new_line = "\n"
    info = "Unknown Record"
    def __init__(self, list_record):
        self.fields = []
        self.list_record = list_record
        if len(list_record) > 0:
            last = self.ast_split(self.list_record.pop(-1))
            for elm in last:
                self.list_record.append(elm)
                
        try:    
            self._init_data_()  
        except:
            self.fields.append(("Unexpected Error", "Invalid Record"))
    def _init_data_(self):
        #hook
        pass
    
    def __str__(self):
        return translate(self.info) + self.new_line*2 + \
            self.new_line.join(translate(key) + " : " + translate(val) \
                                                for (key, val) in self.fields)
    def ast_split(self, entry):
        return entry.split('*')
        
class GGA(Record):
    info = "Global Positioning System Fix Data"
    def _init_data_(self):
        
        self.fields.append(("UTC Time", self.list_record[1]))
        self.fields.append(("Latitude", self.list_record[2] + self.list_record[3]))
        self.fields.append(("Longitude", self.list_record[4] + self.list_record[5]))
        
        
        indicators = {"0": "position fix unavailable",
                      "1": "valid position fix, SPS mode",
                      "2": "valid position fix, differential GPS mode"}
        self.fields.append(("Quality indicator", \
                                indicators.get(self.list_record[6], '')))
        
        self.fields.append(("Satellites Used", self.list_record[7]))
        self.fields.append(("HDOP", self.list_record[8]))
        self.fields.append(("Altitude", self.list_record[9] + self.list_record[10]))
        self.fields.append(("Geoidal Separation", self.list_record[11] + self.list_record[12]))
        
        self.fields.append(("Checksum", self.list_record[-1]))
        

class GLL(Record):
    info =  "Geographic Position - Latitude/Longitude"
    def _init_data_(self): 
        self.fields.append(("Latitude", self.list_record[1] + self.list_record[2]))
        self.fields.append(("Longitude", self.list_record[3] + self.list_record[4]))
        self.fields.append(("UTC Time", self.list_record[5]))
        
        statuses = {"V":"Data not valid",
                    "A":"Data Valid"}
        self.fields.append(("Status", statuses.get(self.list_record[6], ""))) 
        self.fields.append(("Checksum", self.list_record[-1]))

class GSA(Record):
    info = "GNSS DOP and Active Satellites"
    def _init_data_(self):        
        
        types = {"P":"GPS", "L":"GLONASS"}
    
        self.fields.append(("Type", types.get(self.list_record[0][2], "")))
        
        modes = {"A": "Automatic", "M" : "Manual"}
        self.fields.append(("Mode", modes.get(self.list_record[1], "")))
        
        fixes = {"1":"Fix not available", "2":"2D", "3":"3D"}
        self.fields.append(("Fix mode", fixes.get(self.list_record[2], "")))
        
        ids = ", ".join(id_ for id_ in self.list_record[3:15] if id_)
        self.fields.append(("Satellite IDs", ids))
        
        self.fields.append(("PDOP", self.list_record[15]))
        self.fields.append(("HDOP", self.list_record[16]))

        self.fields.append(("VDOP", self.list_record[17]))
        
        self.fields.append(("Checksum", self.list_record[-1]))

class GSV(Record):  
    info = "GNSS Satellites in View"
    def _init_data_(self):
        types = {"P":"GPS", "L":"GLONASS"}    
        self.fields.append(("Type", types.get(self.list_record[0][2], "")))
        
        self.fields.append(("Number of messages", self.list_record[1]))
        self.fields.append(("Sequence number", self.list_record[2]))
        self.fields.append(("Satellites in view", self.list_record[3]))
        
        self.fields.append(("Checksum", self.list_record[-1]))
        
        satellites = list(self.list_record[4:-1])
        if len(satellites) >= 4:
            #group by 4
            satellites = [satellites[i:i+4] for i in range(0, len(satellites), 4)] 
            for sat in satellites:
                if len(sat) == 4:
                    self.fields.append(("", ""))
                    self.fields.append(("Satellite ID", sat[0]))
                    self.fields.append(("Elevation", sat[1]))
                    self.fields.append(("Azimuth", sat[2]))
                    self.fields.append(("SNR", sat[3]))
    
class RMC(Record):  
    info = "Recommended Minimum Specific GNSS Data"
    def _init_data_(self):
        self.fields.append(("UTC Time", self.list_record[1]))
        
        statuses = {"V":"Navigation receiver warning",
                    "A":"Data Valid"}
        self.fields.append(("Status", statuses.get(self.list_record[2], ""))) 
        
        self.fields.append(("Latitude", self.list_record[3] + self.list_record[4]))
        self.fields.append(("Longitude", self.list_record[5] + self.list_record[6]))
        
        self.fields.append(("Speed, knots", self.list_record[7]))
        self.fields.append(("Course, deg", self.list_record[8]))
        
        self.fields.append(("UTC Date", self.list_record[9]))
        
        modes = {"N":"Data not valid", 
                 "A":"Autonomous",
                 "D":"Differential",
                 "E":"Estimated (dead reckoning)"}
        self.fields.append(("Mode", modes.get(self.list_record[-2], "")))  
        
        self.fields.append(("Checksum", self.list_record[-1]))
    
class VTG(Record):  
    info = "Course Over Ground and Ground Speed"
    def _init_data_(self):
        self.fields.append(("Course, deg True", self.list_record[1] + \
                                                self.list_record[2]))
        self.fields.append(("Course, deg Magnetic", self.list_record[3] + \
                                                    self.list_record[4]))
        self.fields.append(("Speed, knots", self.list_record[5] + \
                                            self.list_record[6]))
        self.fields.append(("Speed, km/hr", self.list_record[7] + \
                                            self.list_record[8]))
        
        modes = {"N":"Data not valid", 
                 "A":"Autonomous",
                 "D":"Differential",
                 "E":"Estimated (dead reckoning)"}
        self.fields.append(("Mode", modes.get(self.list_record[9], "")))
        self.fields.append(("Checksum", self.list_record[-1]))
    
class ZDA(Record):  
    info =  "Time and Date"
    def _init_data_(self):
        self.fields.append(("UTC Time", self.list_record[1]))
        self.fields.append(("UTC Day", self.list_record[2]))
        self.fields.append(("UTC Month", self.list_record[3]))
        self.fields.append(("UTC Year", self.list_record[4]))
        self.fields.append(("Local zone hours", self.list_record[5]))
        self.fields.append(("Local zone minutes", self.list_record[6]))
        self.fields.append(("Checksum", self.list_record[-1]))
 
class ACCURACY(Record):  
    info = "Accuracy"
    def _init_data_(self):
        self.fields.append(("Accuracy", self.list_record[1])) 
        self.fields.append(("Checksum", self.list_record[-1]))

class NMEA:    
    parsers = {"GGA": GGA, "GLL" : GLL, "GSA" : GSA,
               "GSV" : GSV, "RMC" : RMC, "VTG" : VTG, 
               "ZDA" : ZDA, "ACCURACY" : ACCURACY}
    new_line = "\n"           
    def __init__(self, filepath):       
        self.records = []
        
        try:
            with open(filepath, 'r') as input_:
                for line in input_:
                    self.records.append(line.strip())
        except:
            pass
        
    def get_info(self, record_ind):
        if record_ind >= 0 and record_ind < len(self.records):
            return NMEA.get_str_info(self.records[record_ind])
            
    @staticmethod
    def get_str_info(record_str):
        s =  record_str + NMEA.new_line*2 + NMEA._record_info(record_str)
                
        return s
        
    @staticmethod
    def _record_info(record_str):        
        record = record_str.split(",")
        
        parser = Record
        
        if len(record) > 0:
            if len(record[0]) >= 5:
                parser = NMEA.parsers.get(record[0][3:], Record)
                
        return(str(parser(record)))


class GUI:
    def __init__(self, filepath = None, filter_=""):
        self.root = tk.Tk()
        self.root.wm_title("NMEA Viewer")
        
        custom_font = font.Font(family="Helvetica", size=10)
        
        #Menu        
        menu = tk.Menu(self.root, font=custom_font, tearoff=0)
        self.root.config(menu=menu)
        
        file_menu = tk.Menu(menu, font=custom_font, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)        
        
        file_menu.add_command(label="Open", command = self.on_open_cmd, 
                              font=custom_font)
        
        
        #Frames
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
                
        
        records_frame = tk.Frame(main_frame)
        records_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        
        list_frame = tk.Frame(records_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        
        filter_frame = tk.Frame(records_frame)
        filter_frame.pack(side=tk.TOP, fill=tk.BOTH)
                
        
        #Left Textbox       
        self.txtbox = tk.Text(info_frame, 
                               font=custom_font, 
                               wrap=tk.WORD, width = 80)
        self.txtbox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        
        txt_scrollbar = tk.Scrollbar(info_frame)
        txt_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        self.txtbox.config(yscrollcommand=txt_scrollbar.set)
        txt_scrollbar.config(command=self.txtbox.yview)
        
        #Right List
        
        self.listbox = tk.Listbox(list_frame, font=custom_font, width=50)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.listbox.bind("<<ListboxSelect>>", self.on_record_select)
        
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        self.listbox.config(yscrollcommand=list_scrollbar.set)
        list_scrollbar.config(command=self.listbox.yview)
        
        #Filter
        self.filter_var = tk.StringVar(value=filter_)
        self.filter_var.trace("w", self.reload_nmea)
        
        filterbox = tk.Entry(filter_frame, font=custom_font, width=1,
                                  textvariable = self.filter_var)
        filterbox.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.X)
        
        
        #load file
        if filepath is not None:
            self.load_nmea(filepath)
        
    def load_nmea(self, filepath):
        self.nmea = NMEA(filepath)
        
        self.reload_nmea()

    def reload_nmea(self, *args):
        self.listbox.delete(0, tk.END)
        
                
        for record in self.filtered_nmea():
            #print(record)
            self.listbox.insert(tk.END, record)
    
    
    def filtered_nmea(self):
        expr = self.filter_var.get()
        print("filter", expr, len(expr))
        if len(expr) > 0:            
            regex = re.compile(expr, re.IGNORECASE)
            for line in self.nmea.records:                
                if regex.search(line):
                    yield line
        else:
            for line in self.nmea.records:
                yield line
            
    def on_record_select(self, evt):
        # Note here that Tkinter passes an event object
        w = evt.widget
        if len(w.curselection()) > 0 and self.nmea is not None:       
            index = int(w.curselection()[0])
            record = w.get(index)        
        
            text = NMEA.get_str_info(record)            
            self.txtbox.delete(1.0, tk.END)
            self.txtbox.insert(1.0, text)
        
    
    def on_open_cmd(self):
        filetypes = [('text files', '.txt'), ('all files', '.*')]
        
        filepath = filedialog.askopenfilename(filetypes = filetypes )
        
        print("open", filepath)
        if filepath:
            self.load_nmea(filepath) 
        
    
    def show(self):
        self.root.mainloop()


def main(*args):
    filepath = args[1] if len(args) >= 2 else None
    filter_ = args[2] if len(args) >= 3 else ""
    
    gui = GUI(filepath, filter_)
    gui.show()


if __name__ == "__main__":
    # execute only if run as a script
    main(argv)

