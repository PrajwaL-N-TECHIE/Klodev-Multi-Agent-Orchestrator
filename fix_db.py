import sqlite3

print("🔧 Fixing database schema...")
conn = sqlite3.connect('klodev.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE email_tracking ADD COLUMN subject TEXT")
    print("✅ Added 'subject' column.")
except Exception as e:
    print(f"Subject column already exists or error: {e}")

try:
    c.execute("ALTER TABLE email_tracking ADD COLUMN campaign_name TEXT")
    print("✅ Added 'campaign_name' column.")
except Exception as e:
    print(f"Campaign_name column already exists or error: {e}")

conn.commit()
conn.close()
print("🎯 Database fixed! You are good to go.")