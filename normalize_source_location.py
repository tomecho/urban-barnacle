import sqlite3
from sys import argv

def make_relative_absolute(relative_file, page):
    offset_factors = {
        'first': 0, # already absolute!
        'second': 1,
        'third': 2,
        'fourth': 3,
        'fifth': 4,
        'sixth': 5,
        'seventh': 6,
    }
    offset_factor = next(offset_factors[file_part] for file_part in offset_factors.keys() if (file_part in relative_file))
    return page+(50000*offset_factor)

with sqlite3.connect(argv[1]) as conn:
    total_records = int(conn.execute('select count(*) from ' + argv[2]).fetchone()[0])

    cur = conn.cursor()
    cur.execute('select id, source_location from ' + argv[2])

    for row in cur:
        source_location = row[1] # file.pdf:page:line
        better_source_location =   "file.pdf"
        relative_page = source_location[source_location.index(':') + 1 : source_location.rindex(':')] # page
        line = source_location[source_location.rindex(':') + 1 :]

        absolute_page = make_relative_absolute(source_location, int(relative_page))
        better_source_location = "{}:{}:{}".format(better_source_location, absolute_page, line)
        conn.execute('update ' + argv[2] + ' set better_source_location = ? where id = ?', [better_source_location, row[0]])
        conn.commit()
        if row[0] % 100 == 0: # printing to screen is i/o heavy, only do it every so often
            print(row[0] / total_records, end = '\r')

# 5678339