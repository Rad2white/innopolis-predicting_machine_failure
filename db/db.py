import sqlite3

class DbManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        
    def get_all_history(self):
        for row in self.cur.execute("SELECT * FROM usage_history ORDER BY id"):
            print(row)
            
    def insert_history(self, date, time):
        self.cur.execute(f"INSERT INTO usage_history(date, time) VALUES (?, ?)", (date, time))
        print(self.cur.lastrowid)
        self.con.commit()

    def get_all_results(self):
        for row in self.cur.execute("SELECT * FROM result_history ORDER BY id"):
            print(row)

    def result_history(self, type_frais, air_temp, proc_temp, rotation_speed, torque, tool_wear, result_string):
        self.cur.execute(f"INSERT INTO result_history(type_frais, air_temp, proc_temp, rotation_speed, torque, tool_wear, result_string) VALUES (?, ?, ?, ?, ?, ?, ?)", (type_frais, air_temp, proc_temp, rotation_speed, torque, tool_wear, result_string))
        print(self.cur.lastrowid)
        self.con.commit()