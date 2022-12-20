import requests
from bs4 import BeautifulSoup
import json
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import pyrebase


# Created by Anton Andersson
## Klipper / Moonsail plugin to get an email when print is done!


# You will need to install
# Pyrebase (firebase)
# Sendgrid (for email)
# BeautifulSoup4

############## CHANGE TO YOUR SETTINGS ########################

# API-KEY for moonsail
api_key_moonsail = ""
# API-KEY for sendgrid
api_key_sendgrid = ""

# IP FOR YOUR PRINTER OR HOSTNAME!
printer_ip = ""

# Settings for sendgrid
sendgrid_from_email = ""
sendgrid_to_email = ""

# Settings for firebase
fb_apiKey = ""
fb_authDomain = ""
fb_databaseURL = ""
fb_storageBucket =  ""

# Change if you want to use a diffrent name or with multiplie printers
DATABASE_CHILD = "printer"

############## CHANGE TO YOUR SETTINGS ########################

# Firebase config
config = {
  "apiKey": fb_apiKey,
  "authDomain": fb_authDomain,
  "databaseURL": fb_databaseURL,
  "storageBucket": fb_storageBucket


}

# Init firebase
firebase = pyrebase.initialize_app(config)


def save_database(key_enter, data_enter):
	db = firebase.database()
	data = {key_enter: data_enter}
	db.child(DATABASE_CHILD).update(data)


def send_email(subject_enter, information_enter, send_to):
	my_sg = sendgrid.SendGridAPIClient(api_key = api_key_sendgrid)

	# Change to your verified sender
	from_email = Email(sendgrid_from_email, "Enter Your name Here)  

	# Change to your recipient
	to_email = To(send_to)  

	subject = subject_enter
	content = Content("text/html", information_enter + "<img src='ENTER_URL_TO_IMAGE'>")


	mail = Mail(from_email, to_email, subject, content)

	# Get a JSON-ready representation of the Mail object
	mail_json = mail.get()

	# Send an HTTP POST request to /mail/send
	response = my_sg.client.mail.send.post(request_body=mail_json)

	save_database("email_sent", True)

headers = {
	'X-Api-Key' : api_key_moonsail
}

response = requests.get('http://' + printer_ip + '/printer/objects/query?heater_bed=temperature&extruder=temperature&fan=speed&print_stats=state&display_status=progress', headers=headers)

y = json.loads(response.content)

db = firebase.database()

status = y["result"]["status"]["print_stats"]["state"]


# --- For debugging
#print(status)

if (status == "printing"):

	# --- For debugging
	#print("Printer is printing")

	save_database("email_sent", False)

	save_database("status", "The printer is working!")

if (status == "complete"):
	# --- For debugging
	#print("Printer is done")

	save_database("status", "Printing is Done!")

	user = db.child(DATABASE_CHILD).get().val()

	get_if_email_sent = user["email_sent"]

	if get_if_email_sent == False:
		send_email("Your 3D-print is done!", "Your printer is done printing!", "enter_your_email")
		imgURL = "http://" + printer_ip + "/webcam?action=snapshot"
		urllib.request.urlretrieve(imgURL, "/var/www/html/printer.jpg")



	

