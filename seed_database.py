import sqlite3
conn = sqlite3.connect('klodev.db')
c = conn.cursor()
# Lower Dev's score so he doesn't steal the spotlight from American leads
c.execute("UPDATE contacts SET lead_score = 90 WHERE name = 'Dev Gupta'")
conn.commit()
conn.close()