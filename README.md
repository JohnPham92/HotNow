# HotNow

Krispy Kreme is offering free donuts when customers find the Hot Now sign on. So to track, I wrote a script that will
send a text letting people know donuts are ready.

There's a requirement to create a secrets.py file that contains your sendgrid api key. And then a
list `PHONE_NUMBERS = ['1234567890']` that contains the formatting for your phone number. T-Mobile has a particular
email domain that allows you to email to sms, but check what it is for your particular carrier.