# /index.py

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher
import json
import pytz
import dateutil.parser
from datetime import date, time, datetime
import pprint

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

flight_list = []
url = ""
destination = ""
@app.route('/get_flight_details', methods=['POST'])
def get_flight_details():
    global flight_list, url, destination
    data = request.get_json(silent=True)
    print(data['queryResult']['action'])
    if data['queryResult']['action'] == "bookflight":
        source = data['queryResult']['parameters']['source']
        destination = data['queryResult']['parameters']['destination']
        passengers = data['queryResult']['parameters']['passengers']
        date = data['queryResult']['parameters']['date']
        time_of_day = data['queryResult']['parameters']['time']
        url = "http://flights.makemytrip.com/makemytrip/search/O/O/E/" + str(int(passengers)) + "/0/0/S/V0/" + str(source) + "_" + str(destination) + "_" + dateutil.parser.parse(date).strftime("%d-%m-%Y")
        os.system("python2.7 scrape-makemytrip.py {0} {1} {2} {3}".format(source,destination,date,passengers))
        flight_list = []
        with open("out.json",'r') as file:
            flights_dict = json.load(file)

        for flight in flights_dict:
            #print(flight["le"][0]["d"],destination)
            if (flight["le"][0]["d"] != destination):
                continue
            if time_of_day == "earlymorning":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(5,00)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(8,59)):
                    flight_list.append(flight)
            elif time_of_day == "morning":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(9,00)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(11,59)):
                    flight_list.append(flight)
            elif time_of_day == "afternoon":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(12,00)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(16,59)):
                    flight_list.append(flight)
            elif time_of_day == "evening":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(17,00)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(19,29)):
                    flight_list.append(flight)
            elif time_of_day == "night":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(19,30)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(22,59)):
                    flight_list.append(flight)
            elif time_of_day == "latenight":
                if (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()>time(23,00)) and (datetime.strptime(flight["le"][0]["fdt"],"%H:%M").time()<time(4,59)):
                    flight_list.append(flight)
        #print(flight_list)
        reply = {
            "fulfillmentText": "Please wait while I search for the available flights. In the meantime, would you like to know more about your destination?",
        }
        return jsonify(reply)

    elif data['queryResult']['action'] == "BookFlight.destinfo":
        #destination = ""
        pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(data['queryResult'])
        print(data['queryResult']['outputContexts'],"\n")
        print(data['queryResult']['outputContexts'][0],"\n")
        print(data['queryResult']['outputContexts'][1],"\n")
        outputContexts_list = data['queryResult']['outputContexts']
        #nonlocal destination
        # for outputContext_dict in outputContexts_list:
        #     #nonlocal destination
        #     if outputContext_dict["name"] == "bookflight-followup":
        #         destination = outputContext_dict['parameters']['destination']
        print(destination,"\n")
        with open("destfact.json",'r') as file:
            destfact_list = json.loads(file.read())
        print(destfact_list)
        response = "Here is some information about your destination.<br><br>"
        for destfact in destfact_list:
            if destfact["code"] == destination:
                response += destfact["info"]
                response += "<br><br>Here are some fun facts about the city:<br><ul>"
                for destfunfact in destfact["facts"]:
                    response+=("<li>"+destfunfact+"</li>")
                response += "</ul>"
        response +="<br><br>I have procured the details of the flights, would you like to see them now?"
        reply = {
            "fulfillmentText": response,
        }
        return jsonify(reply)

    elif data['queryResult']['action'] == "BookFlight.destinfo.displaydetails":
        response = """
            These are the cheapest flights according to your preferences:
            <ol>
        """
        for flight in flight_list:
            response += """
                <li><a href = "{8}" >Rs. {0} - {1} flight {2}-{3} travelling from {4} to {5} on {6} at {7}. </li>
            """.format(flight["af"] , flight["le"][0]["an"] , flight["le"][0]["fn"] , flight["le"][0]["oc"] , flight["le"][0]["f"] , flight["le"][0]["t"] , dateutil.parser.parse(flight["le"][0]["dep"]).strftime('%d / %m / %Y') , flight["le"][0]["fdt"] , url)
        response += """
        </ol>
        """
        reply = {
            "fulfillmentText": response,
        }


        return jsonify(reply)


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }

    return jsonify(response_text)

    # run Flask app
if __name__ == "__main__":
    app.run()