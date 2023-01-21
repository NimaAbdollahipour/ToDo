import typer
from datetime import date
import sqlite3
from colorama import init as colorama_init
from colorama import Fore,Back
from colorama import Style

COLORS = [Fore.BLACK+Back.RED, Back.YELLOW+Fore.BLACK, Back.GREEN+Fore.BLACK, Back.WHITE+Fore.BLUE]
IMPORTANCE = {'high':1,'medium':2,'low':3}
colorama_init()
con = sqlite3.connect("database.db")
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, title TEXT, created DATE, date DATE, importance INTEGER, done INTEGER)')
app = typer.Typer()


@app.command()
def add(title: str,for_date:str,importance:str):
    importance = importance_to_num(importance)
    converted_date = convert_to_date(for_date)
    if importance and converted_date:
        try:
            cur.execute("INSERT INTO todos (title, created, date, importance, done) VALUES (?, ?, ?, ?, 0)", (title,date.today(),converted_date, importance))
            con.commit()
            disp_success('todo added successfully')
        except:
            disp_error('could not save to database')
    

@app.command()
def list(day: str):
    results = []
    if(day=='today'):
        cur.execute("SELECT * FROM todos WHERE date=? ORDER BY importance",(date.today(),))
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
        value = convert_to_date(value)
        if value:
            cur.execute("UPDATE todos SET date=? WHERE id=?",(value,id))
    elif(field=='importance'):
        value = importance_to_num(value)
        if value:
            cur.execute("UPDATE todos SET importance=? WHERE id=?",(value,id))
    else:
        disp_error('wrong field')
        return
    con.commit()
    disp_success('updated successfully')
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    display(result)

@app.command()
def delete(id: int):
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    if(not result):
        disp_error('not found')
        return
    display(result)
    try:
        cur.execute("DELETE FROM todos WHERE id=?",(id,))
        con.commit()
        disp_success('deleted successfully')
    except:
        disp_error('failed to delete')

@app.command()
def done(id: int):
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    if(not result):
        disp_error('not found')
        return
    display(result)
    try:
        cur.execute("UPDATE todos SET done=1 WHERE id=?",(id,))
        con.commit()
        disp_success('marked as done')
    except:
        disp_error('failed to mark as done')

@app.command()
def undone(id: int):
    cur.execute("SELECT * FROM todos WHERE id=?",(id,))
    result = cur.fetchone()
    if(not result):
        disp_error('not found')
        return
    display(result)
    try:
        cur.execute("UPDATE todos SET done=0 WHERE id=?",(id,))
        con.commit()
        disp_success('marked as undone')
    except:
        disp_error('failed to mark as undone')

@app.command()
def deletedone():
    try:
        cur.execute("DELETE FROM todos WHERE done=1")
        con.commit()
        disp_success('deleted done todos')
    except:
        disp_error('failed to delete')


def display(result):
    if result[5]==1:
        color = COLORS[3] + ' \u2713 '
    else:
        color = COLORS[result[4]-1] + ' \u2717 '
    id = str(result[0])
    id = (4-len(id))*'0'+id
    print(f'{color} {id}: {result[3]} : {result[1]} {Style.RESET_ALL}')


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
