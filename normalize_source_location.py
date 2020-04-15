import sqlite3
from sys import argv

def make_relative_absolute(part, page):
    offset_factor = {
        'first': 0, # already absolute!
        'second': 1,
        'third': 2,
        'fourth': 3,
        'fifth': 4,
        'sixth': 4,
        'seventh': 4,
    }
    return page+(50000*offset_factor)

with sqlite3.connect(argv[1]) as conn:
    cur = conn.cursor()
    cur.execute('select id, source_location from ' + sys.argv[2])

    while row = cur.fetchone():
        source_location = row[1] # file.pdf:page:line
        better_source_location = source_location[0, source_location.index(':')]  # file.pdf
        relative_page = source_location[source_location.index(':') + 1, source_location.rindex(':')] # page
        line = source_location[source_location.rindex(':') + 1]

        absolute_page = make_relative_absolute(source_location, int(relative_page))
        better_source_location = "{}:{}:{}".format(better_source_location, absolute_page, line)
        conn.execute('update ' + sys.argv[2] + ' set better_source_location = ?', [better_source_location])
        conn.commit()
        



# total 5678339
# distinct property_id 5392259