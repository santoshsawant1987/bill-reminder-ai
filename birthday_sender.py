import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv, find_dotenv

# ── Load Environment Variables ────────────────────────────────────────────────
load_dotenv(find_dotenv()) # 👈 this loads your .env file
# ── Data ────────────────────────────────────────────────────────────────────
data = [
    ["Sneha",   "1990-03-25"],
    ["Malan",   "1985-07-15"],
    ["Amrut",   "1992-04-19"],
    ["Santosh", "1987-11-30"],
    ["Rahul",   "1995-04-20"],
    ["Priya",   "1993-08-05"],
    ["Vikram",  "1988-04-19"],
    ["Neha",    "1991-12-01"],
]

columns = ["Name", "Birthday"]

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.DataFrame(data, columns=columns)
df["Birthday"] = pd.to_datetime(df["Birthday"])

# ── Filter Today and Upcoming 7 Days Birthdays ───────────────────────────────
today = datetime.today()

def days_until_birthday(bday):
    this_year_bday = bday.replace(year=today.year)
    if this_year_bday.date() < today.date():
        this_year_bday = bday.replace(year=today.year + 1)
    delta = (this_year_bday.date() - today.date()).days
    return delta

df["Days_Until"] = df["Birthday"].apply(days_until_birthday)
df["DOB"]        = df["Birthday"].dt.strftime("%d-%b")

# Today's birthdays
today_df    = df[df["Days_Until"] == 0].copy()

# Upcoming 7 days birthdays
upcoming_df = df[(df["Days_Until"] > 0) & (df["Days_Until"] <= 7)].copy()
upcoming_df = upcoming_df.sort_values("Days_Until")

# ── Build HTML ───────────────────────────────────────────────────────────────
def build_html(today_df, upcoming_df, today):

    # Today's birthdays section
    today_section = ""
    if not today_df.empty:
        rows = ""
        for _, row in today_df.iterrows():
            rows += f"""
            <tr style="background-color:#fff9c4;">
                <td>🎂 <b>{row['Name']}</b></td>
                <td>{row['DOB']}</td>
                <td><b style="color:green;">TODAY! 🎉</b></td>
            </tr>"""
        today_section = f"""
        <h2 style="color:#e53935;">🎉 Today's Birthdays</h2>
        <table border="1" cellpadding="8" cellspacing="0"
               style="border-collapse:collapse; font-family:Arial; font-size:13px; width:60%;">
            <thead style="background-color:#e53935; color:white;">
                <tr>
                    <th>Name</th>
                    <th>Date of Birth</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table><br>"""
    else:
        today_section = "<p>No birthdays today.</p>"

    # Upcoming birthdays section
    upcoming_section = ""
    if not upcoming_df.empty:
        rows = ""
        for _, row in upcoming_df.iterrows():
            days = int(row['Days_Until'])
            days_label = f"In {days} day{'s' if days > 1 else ''}"
            rows += f"""
            <tr>
                <td>👤 {row['Name']}</td>
                <td>{row['DOB']}</td>
                <td><b style="color:#1565c0;">{days_label}</b></td>
            </tr>"""
        upcoming_section = f"""
        <h2 style="color:#1565c0;">📅 Upcoming Birthdays (Next 7 Days)</h2>
        <table border="1" cellpadding="8" cellspacing="0"
               style="border-collapse:collapse; font-family:Arial; font-size:13px; width:60%;">
            <thead style="background-color:#1565c0; color:white;">
                <tr>
                    <th>Name</th>
                    <th>Date of Birth</th>
                    <th>Days Remaining</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table><br>"""
    else:
        upcoming_section = "<p>No upcoming birthdays in next 7 days.</p>"

    return f"""
    <html><body style="font-family:Arial; font-size:14px;">
    <h1 style="color:#333;">🎂 Birthday Reminder – {today.strftime('%d %B %Y')}</h1>
    <p>Dear Team,</p>
    <p>Here is the birthday reminder for today and the next 7 days:</p>
    {today_section}
    {upcoming_section}
    <br>
    <p>Please wish them on their special day! 🎊</p>
    <p>Regards,<br><b>Automated Birthday Reminder</b></p>
    </body></html>
    """

# ── Send Email ───────────────────────────────────────────────────────────────
def send_email(html_body, today_count, upcoming_count):
    sender   = os.environ["EMAIL_SENDER"]
    receiver = os.environ["EMAIL_RECEIVER"]
    password = os.environ["PASSWORD_API_KEY"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎂 Birthday Reminder – {today_count} Today | {upcoming_count} Upcoming"
    msg["From"]    = sender
    msg["To"]      = receiver

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(sender, password)
        s.sendmail(sender, receiver, msg.as_string())

    print(f"✅ Birthday reminder sent! Today: {today_count}, Upcoming: {upcoming_count}")

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    html = build_html(today_df, upcoming_df, today)
    send_email(html, len(today_df), len(upcoming_df))
    print(f"Today's birthdays: {len(today_df)}")
    print(f"Upcoming birthdays (7 days): {len(upcoming_df)}")