#https://www.pythoncentral.io/introduction-to-sqlite-in-python/
import argparse
import sqlite3
import csv
import json
import sys
from os import path
from datetime import datetime

#parameters
DEFAULT_VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
USER_HOME = path.expanduser('~')

def watch():
    try:
        assert sys.platform.startswith('win'), "watch.py is for windows only."
        args = parse() #-h stops here
        #get settings and db
        cwd = path.dirname(path.realpath(__file__))
        settings_dict = get_settings(args.settings_flag, cwd)
        db, cursor = get_db(cwd)
        #get whole db
        if args.view_flag or args.export_flag: #we need whole DB for both
            cursor.execute("SELECT * FROM series")
            db_items = cursor.fetchall()
        #view
        if args.view_flag:
            view(db_items)
        #settings
        if args.settings_flag:
            settings_dict = settings(settings_dict, args.cli_flag, cwd)
        #add
        if args.add_flag:
            #TODO: add show to DB
            add(db, cursor, args.cli_flag)
        #edit
        #delete
        #export
        if args.export_flag:
            if export_id in settings:
                settings['export_id'] = 1
            else:
                settings['export_id'] += 1
            #TODO: get export file location from settings, decide file name (settings), create csv
            export(export_file_path, db_items)
        #watch series
        if args.series_name:
            if args.season:
                if args.episode: #watch <series_name> S<season>E<episode>
                    pass
                else: #season but no episode
                    raise Exception("A season must be followed by an episode.")
            else: #get last episode from sql etc.
                pass 
        #finish
        db.close()
    except Exception as e:
        print "Error:", e
        sys.exit(1)


def parse():
    parser = argparse.ArgumentParser(prog='watch',
        description="" +
        "watch an episode of a series in your selected video player. Use watch -s to \n" +
        "change settings (already done if installed correctly), then add a series with \n" +
        "watch -a, and watch it with watch <series_name>. Some examples:\n" +
        "1. watch GoT 1 4 : Watch first season, fourth episode of the series you added as 'got'.\n"
        "2. watch Vikings : Watch the next episode of the series you added as 'vikings'.\n" +
        "3. watch -ve : Print and export your watch stats.",
        epilog='it is recommended to set up the settings, add a series, and then use watch \r\nwithout parameters until the last episode of the series',
        usage='watch [series_name [season episode]] [-h] [-a | -e | -r | -s | -x] [-v] [-c] [-d]',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-a','--add', help="add a new series to watch", action='store_true', dest='add_flag')
    group1.add_argument('-e','--edit', help="edit a series you've already added, keeping the last and total episodes watched", action='store_true', dest='edit_flag')
    group1.add_argument('-r','--remove', help="remove a series you've added completely.", action='store_true', dest='remove_flag')
    group1.add_argument('-s','--settings', help="edit the settings", action='store_true', dest='settings_flag')
    group1.add_argument('-x','--export', help="export series stats to excel file", action='store_true', dest='export_flag')
    
    parser.add_argument('-v','--view', help="print series stats on terminal", action='store_true', dest='view_flag')
    parser.add_argument('series_name', help="the name of the series to be watched, as specified when added", nargs='?')
    parser.add_argument('season', help="the season to be watched", nargs='?', type=int)
    parser.add_argument('episode', help="the episode to be watched", nargs='?', type=int)
    parser.add_argument('-c','--cli', help="use with add, settings, or export, to open them in a command line interface", action='store_true', dest='cli_flag')
    parser.add_argument('-d','--debug', help="print file name instead of watching it, without saving to database", action='store_true', dest='debug_flag')
    return parser.parse_args()


def add(db, cursor, cli):
    #TODO
    new_series = {
        'name' : "",
        'full_name' : "",
        'path' : ""
    }
    if cli:
        print "Type in the following values:"
        for k,v in new_series.iteritems():
            prompt_text = str(k) + ':'
            new_series[k] = raw_input(prompt_text)
    else: #GUI
        pass
    new_series['last_season_watched'] = 1
    new_series['last_episode_watched'] = 1
    new_series['total_episodes_watched'] = 0
    new_series['date_added'] = datetime.now() #TODO: format this
    cursor.execute('''INSERT INTO series(name, "full name", path, "last season watched", "last episode watched", "total episodes watched", "date added")
        VALUES(:name, :full_name, :path, :last_season_watched, :last_episode_watched, :total_episodes_watched, :date_added)
    ''', new_series)
    db.commit()


def edit():
    #TODO
    pass


def remove():
    #TODO
    pass


def settings(settings_dict, cli, cwd):
    #TODO: GUI
    settings_path = path.join(cwd, "settings")
    if settings_dict:
        old_settings_dict = settings_dict
        settings_dict = {}
    else:
        #default settings
        old_settings_dict = {
            'player path' : DEFAULT_VLC_PATH,
            'export path' : USER_HOME,
            }
    if cli:
        #TODO: go over settings one by one
        print "Type in each setting to change it, leave blank for no changes (old value in parentheses)"
        for k,v in old_settings_dict.iteritems():
            prompt_text = str(k) + '(' + str(v) + '):'
            new_setting = raw_input(prompt_text)
            settings_dict[k] = new_setting if new_setting else v
    else: #GUI
        pass
    write_settings(settings_path, settings_dict)
    return settings_dict


def export(export_file_path, db_items):
    #TODO: write db to csv in export_file_path
    pass


def view(db_items):
    #TODO: print the db , formatted
    for row in db_items:
        print row
    raw_input("press enter to proceed")


def read_settings(file):
    with open(file, 'r') as f:
        ret = json.load(f)
    return ret


def write_settings(file, settings_dict):
    with open(file, 'w+') as f:
        json.dump(settings_dict, f)
    return


def get_settings(flag, cwd):
    settings_path = path.join(cwd, "settings")
    if path.isfile(settings_path):
        settings_dict = read_settings(settings_path)
    elif not flag:
        raise Exception("The settings file is missing or corrupt. Please use 'watch -s'")
    else:
        settings_dict = {}
    return settings_dict


def get_db(cwd):
    db_path = path.join(cwd, "db")
    db_exists = path.isfile(db_path)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    if not db_exists: #new db
        cursor.execute('''
        CREATE TABLE series(
            id INTEGER PRIMARY KEY UNIQUE,
            name TEXT UNIQUE,
            "full name" TEXT,
            path TEXT,
            "last season watched" INTEGER,
            "last episode watched" INTEGER,
            "total episodes watched" INTEGER,
            "date added" TEXT)
        ''')
    db.commit
    return db, cursor


if __name__ == '__main__':
    watch()
