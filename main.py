from __future__ import print_function
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from flask import Flask, render_template, request, make_response
import sqlalchemy
import json
import os
import requests as core_requests

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('student.html')


@app.route('/showall')
def showall():
    Category = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        Categorydata = conn.execute(
            "SELECT IncidentID, time_created, Issuetype, IssueDescription, status FROM Issuetb "
        ).fetchall()
    for row in Categorydata:
        Category.append({"IncidentID": "INC" + str(row[0]).zfill(7), "time_created": row[1], "Issue Type": row[2], "Issue Description": row[3], "status": row[4]})
    #print(Category)
    return render_template("showall.html", Category=Category)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        custname = request.form.get("Customer Name")
        aadharnumber = request.form.get("Aadhar Number")
        Category = request.form.get('Category')
        Description = request.form.get('Description')

        stmt = sqlalchemy.text(
            "INSERT INTO Issuetb (CustomerName, Issuetype, IssueDescription, status, aadharnumber)" "VALUES ("
            ":custname, :Category, :Description, :status, :aano)")

        with db.connect() as conn:
            conn.execute(stmt, custname=custname, Category=Category, Description=Description,
                         status='submitted', aano=aadharnumber )

        IncidentID = 0
        with db.connect() as conn:
            # Execute the query and fetch all results
            IncidentID = conn.execute(
                "SELECT MAX(IncidentID) FROM Issuetb "
            ).fetchall()
        #for row in Categorydata:
            #Category.append({"Issue Type": row[0], "Issue Description": row[1]})
        IncidentID=IncidentID[0][0]
        return render_template("result.html", result=result, IncidentID=str(IncidentID).zfill(5))


def init_tcp_connection_engine_local():
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,  # 30 seconds
        "pool_recycle": 1800,  # 30 minutes
    }
    db_user = "root"
    db_pass = "root"
    db_name = "mysqldb"
    db_host = "35.224.40.149:3306"

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_mysql_sqlalchemy_create_tcp]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp]

    return pool


def init_connection_engine():
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,  # 30 seconds
        "pool_recycle": 1800,  # 30 minutes
    }

    if os.environ.get("DB_HOST"):
        return init_tcp_connection_engine(db_config)
    else:
        return init_unix_connection_engine(db_config)


def init_tcp_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_mysql_sqlalchemy_create_tcp]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp]

    return pool


def init_unix_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_socket]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_socket": "{}/{}".format(
                    db_socket_dir,  # e.g. "/cloudsql"
                    cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            }
        ),
        # ... Specify additional properties here.

        # [END cloud_sql_mysql_sqlalchemy_create_socket]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_socket]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_socket]

    return pool


db = init_tcp_connection_engine_local()
#enable below in gcp app engine.
#db = init_connection_engine()


@app.route('/db')
def create_tables():
    # Create tables (if they don't already exist)
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS Issuetb "
            "( IncidentID int(7) unsigned zerofill not null auto_increment, time_created timestamp NOT NULL,"
            "CustomerName CHAR(20) NOT NULL DEFAULT 'VIRTUAL AGENT',"
            "Issuetype CHAR(50) NOT NULL, IssueDescription varchar(500),"
            "timeofresolved timestamp NULL, status CHAR(50), aadharnumber CHAR(50), PRIMARY KEY (IncidentID) );"
        )
    return "Success db"


@app.route("/searchresult")
def searchresult():
    Incident = []
    IncidentID = request.args.get("IncidentID")
    if (len(IncidentID) >3):
        IncidentID = IncidentID[3:]
    #IncidentID =1
    with db.connect() as conn:
        # Execute the query and fetch all results
        IncidentDetails = conn.execute(
            "SELECT IncidentID, time_created, Issuetype, IssueDescription, status FROM Issuetb WHERE IncidentID=" + str(IncidentID)
        ).fetchall()
    for row in IncidentDetails:
       Incident.append({"IncidentID": "INC" + str(row[0]).zfill(7), "time_created": row[1],
                        "Issue Type": row[2], "Issue Description": row[3], "status": row[4]})
    return render_template("searchresult.html", Incident=Incident)

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res =  {
        "fulfillmentText": "Sample from Webhook",
        "source": "Yahoo Weather"
    }

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def make_openweathermap_request(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    print('https://api.openweathermap.org/data/2.5/weather?q={}&appid=4caf7420789e9f763a81fbc58dc34e31'.format(city))

    try:
        r = core_requests.get(
            'https://api.openweathermap.org/data/2.5/weather?q={}&appid=4caf7420789e9f763a81fbc58dc34e31'.format(city))
        current_temp = r.json()['main']['temp']
        current_temp = float(current_temp) - 273.0
        current_temp = int(current_temp)

        speech_response = 'Current temperature in {} is {} Celsius '.format(city, current_temp)
    except Exception as e:
        speech_response = 'Unable to get temperature of {}'.format(city)

    return {
        "fulfillmentText": speech_response,
        "source": "Yahoo Weather"
    }


if __name__ == '__main__':
    app.run(debug=True)
