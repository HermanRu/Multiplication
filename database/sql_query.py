import sqlite3

import pandas as pd
import plotly.express as px

con = sqlite3.connect('database/multi_db_2.db')
cur = con.cursor()


def create_tables_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS multiplication (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            -- user_id  INTEGER,
            session_id INTEGER,
            a  INTEGER,
            b  INTEGER,
            c  INTEGER,
            duration  REAL,
            result INTEGER,
            FOREIGN KEY (session_id)  REFERENCES sessions (session_id)
                ON DELETE CASCADE ON UPDATE NO ACTION
            );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id  INTEGER,
            session_user_id INTEGER,
            date TEXT,
            session_duration REAL,
            solved_examples INTEGER,
            FOREIGN KEY (user_id)  REFERENCES users (user_id)
                ON DELETE CASCADE ON UPDATE NO ACTION);
            """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name  TEXT,
            other TEXT);
            """)
    con.commit()


def load_to_sql(session_id, a, b, c, duration, result):
    cur.execute('INSERT INTO multiplication (session_id, a, b, c, duration, "result") VALUES (?,?,?, ?,?,?)',
                [session_id, a, b, c, duration, result])
    con.commit()


def load_to_sessions(user_id, session_user_id, date, session_duration, solved_examples):
    cur.execute('INSERT INTO sessions (user_id, session_user_id, date, session_duration, solved_examples) VALUES (?,?,?, ?,?)',
                [user_id, session_user_id, date, session_duration, solved_examples])
    con.commit()


def print_results(user_id, session_id):
    results = cur.execute('''
                            SELECT 
                              time(SUM(a.duration), 'unixepoch') spent_time,
                              COUNT(a."result") - sum(a."result") errors,
                              COUNT(a."result") total,
                              round(100.0*sum(a/"result")/COUNT(a."result"), 1) success_score,
                              round(SUM(a.duration)/COUNT(a."result"),1) avg_time
                            FROM multiplication a 
                            LEFT JOIN sessions b 
                                ON a.session_id = b.session_id 
                            WHERE b.user_id = (?) AND a.session_id = (?) 
                          ''', [user_id, session_id]).fetchone()
    print(f'Time in game {results[0]}')
    print(f'Errors: {results[1]}/{results[2]}')
    print(f'Success score: {results[3]}%')
    print(f'Average Answer Time: {results[4]} sec')

    sql_query = f'SELECT * FROM multiplication WHERE session_id = {session_id}'
    df = pd.read_sql_query(sql=sql_query, con=con)

    fig1 = px.density_heatmap(df, x='a', y='b', z="duration", histfunc="avg",
                              nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
    fig2 = px.density_heatmap(df, x='a', y='b', z="result", histfunc="avg",
                              nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
    fig1.update_xaxes(dtick=1)
    fig1.update_yaxes(dtick=1)
    fig2.update_xaxes(dtick=1)
    fig2.update_yaxes(dtick=1)

    fig1.write_image("duration_heatmap_tmp.png")
    fig2.write_image("result_heatmap_tmp.png")

    zzz = input("Press any key to continue")


if __name__ == '__main__':
    con = sqlite3.connect('multi_db_2.db')
    cur = con.cursor()
    create_tables_db()
