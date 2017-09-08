import requests
import re
import getpass

LOGIN_URL = "https://cas.id.ubc.ca/ubc-cas/login?TARGET=https%3A%2F%2Fssc.adm.ubc.ca%2Fsscportal%2Fservlets%2FSRVSSCFramework"
URL = 'https://ssc.adm.ubc.ca/sscportal/servlets/SRVSSCFramework?TARGET=https%3A%2F%2Fssc.adm.ubc.ca%2Fsscportal%2Fservlets%2FSRVSSCFramework'
LOGIN_URL2 = "https://courses.students.ubc.ca/cs/secure/login"
LOGOUT_URL = 'https://courses.students.ubc.ca/cs/main?submit=Logout'


session_requests = requests.session()

def loginAndRegister(dept, course, section, username, password):
    page = session_requests.get(LOGIN_URL)
    lt = re.findall(r'name="lt" value="(.*?)" />', str(page.content))
    payload = {
        'username' : username,
        'password' : password,
        'lt' : lt,
        'execution': 'e1s1',
        '_eventId': 'submit',
        'submit': 'Continue >'
    }
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    headers['refer'] = LOGIN_URL

    #Logging in
    result = session_requests.post(LOGIN_URL, data=payload, headers = headers)
    
    #Loading first page after logging into the ssc
    headers['refer'] = URL
    result = session_requests.get(URL, headers = headers)

    #Second login to the corse registration thingy
    headers['refer'] = LOGIN_URL2
    result = session_requests.get(LOGIN_URL2, headers = headers)

    #Register
    registrationURL = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&submit=Register%20Selected&wldel="+dept+"%7C"+course+"%7C"+section
    headers['refer'] = registrationURL
    result = session_requests.get(registrationURL, headers = headers)

    #Logout
    headers['refer'] = LOGOUT_URL
    result = session_requests.get(LOGOUT_URL, headers = headers)


def main():
    
    dept = input("Enter department(eg. CPSC): ")
    course = input("Enter course(eg. 304): ")
    section = input("Enter section(eg. 201): ")

    username = input("Enter your CWL username: ")
    password = getpass.getpass("Enter your CWL password: ")
    
    COURSE_URL = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=5&dept="+dept+"&course="+course+"&section="+section

    
    page = session_requests.get(COURSE_URL)
    totalSeats = re.compile("Total Seats Remaining:</td><td align=&#39;left&#39;><strong>(.*?)<")
    generalSeats = re.compile("General Seats Remaining:</td><td align=&#39;left&#39;><strong>(.*?)<")
    restrictedSeats = re.compile("Restricted Seats Remaining\*:</td><td align=&#39;left&#39;><strong>(.*?)<")
    

    seats = 0
    restrEligibility = input("Are you eligible for the restricted seats(Y/N): ")
    
    
    if restrEligibility[0].lower() == 'y':
        seats = totalSeats
    else:
        seats = generalSeats
    
    page = session_requests.get(COURSE_URL)
    eligibleSeats = int(re.findall(seats, str(page.content))[0])
    print(eligibleSeats)

    while True:
        page = session_requests.get(COURSE_URL)
        if eligibleSeats>0:
            loginAndRegister(dept, course, section, username, password)
            break
        
if __name__ == '__main__':
    main()
