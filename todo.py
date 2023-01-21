import typer
from datetime import date
import sqlite3
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style


IMPORTANCE = {'high':1,'medium':2,'low':3}
colorama_init()
con = sqlite3.connect("database.db")
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, title TEXT, created DATE, date DATE, type INTEGER)')
app = typer.Typer()


@app.command()
def add(title: str,for_date:str,importance:str):
    importance = importance_to_num(importance)
    converted_date = convert_to_date(for_date)
    if importance and converted_date:
        try:
            cur.execute("INSERT INTO todos (title, created, date, type) VALUES (?, ?, ?, ?)", (title,date.today(),converted_date, importance))
            con.commit()
        except:
            disp_error('could not save to database')
    disp_success('todo added successfully')


@app.command()
def list(day: str):
    results = []
    if(day=='today'):
        cur.execute("SELECT * FROM todos WHERE date=? ORDER BY type",(date.today(),))
        results = cur.fetchall()
    elif(day=='all'):
        cur.execute("SELECT * FROM todos ORDER BY date")
        results = cur.fetchall()
    for result in results:
        display(result)


@app.command()
def edit(id: int,field:str,value):
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    display(result)
    if(field=='title'):
        cur.execute("UPDATE todos SET title=? WHERE id=?",(value,id))
    elif(field=='date'):
        cur.execute("UPDATE todos SET date=? WHERE id=?",(value,id))
    elif(field=='type' or field=='importance'):
        cur.execute("UPDATE todos SET type=? WHERE id=?",(value,id))
    else:
        print(f'{Fore.RED}wrong field{Style.RESET_ALL}')
        return
    con.commit()
    print(f'{Fore.GREEN}successfully updated to:{Style.RESET_ALL}')
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    display(result)


@app.command()
def delete(id: int):
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    if(not result):
        print(f'{Fore.RED}not found{Style.RESET_ALL}')
        return
    display(result)
    try:
        cur.execute("DELETE FROM todos WHERE id=?",(id,))
        con.commit()
        print(f'{Fore.GREEN}successfully deleted:{Style.RESET_ALL}')
    except:
        print(f'{Fore.RED}could not delete:{Style.RESET_ALL}')


def display(result):
    if(result[4]==1):
        print(Fore.RED, end='')
    elif(result[4]==2):
        print(Fore.YELLOW, end='')
    elif(result[4]==3):
        print(Fore.GREEN,  end='')
    else:
        print(Fore.BLUE, end='')
    id = str(result[0])
    id = (4-len(id))*'0'+id
    print(id,':',result[3],':',result[1]+Style.RESET_ALL)


def disp_error(msg):
    print(Fore.RED+msg.upper()+Style.RESET_ALL)

def disp_success(msg):
    print(Fore.GREEN+ msg.upper() +Style.RESET_ALL)

def convert_to_date(input_date):
    try:
        converted_date = date.fromisoformat(input_date)
        return converted_date
    except ValueError:
        disp_error('wrong format for date')
    return None

def importance_to_num(importance):
    importance = IMPORTANCE.get(importance)
    if not importance:
        disp_error('wrong input type for importance')
        return None
    return importance

if __name__ == "__main__":
    app()
