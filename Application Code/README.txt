# Airbnb-Management-System

Airbnb is a widely popular platform that connects hosts who want to rent their homes or apartments to travelers who need a place to stay. With its massive user base and global reach, Airbnb has revolutionized the travel and hospitality industry. However, managing a property on Airbnb can be a complex task, involving a wide range of activities such as property listings, reservations, payments, guest communication, and more. Therefore, there is a need for a robust and efficient Airbnb management system that can help hosts streamline their property management process and provide a seamless experience to their guests.

In this project, we propose to design and develop a smaller version of Airbnb Management System that will provide a comprehensive set of features to hosts and guests alike. The system will be built using a relational database management system (RDBMS) and will leverage various technologies such as SQL, Python, and Streamlit to provide a simple user interface. The system will be able to handle a few aspects of property management, from creating listings to managing bookings.

# Dataset

Inside Airbnb Dataset for Boston - http://insideairbnb.com/get-the-data/

All files used for the database is available in the project folder /inside_airbnb_data

# Technologies and Libraries Used

* Python for backend
* MySQL Server and Workbench
* Streamlit for frontend
* pymysql - for connectivity between Python and MySQL
* pandas, csv - for data population
* hashlib for user password hashing

# Steps for Installation

Download and extract the zip file, do the following. Open Terminal and do the following steps to setup environment

    cd RachelJacobJNeelakantanS_project/Application Code

Create a virtual environment and activate it using the following commands.

    python3 -m venv airbnb_env
    source airbnb_env/bin/activate

Install the required packages

    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt

Run the dump file Database_Schema/airbnb_dump.sql to create a database named ‘airbnb’.

# To pre-populate data

This is the code used by admin to pre-populate the tables. 
The data populated using this is provided in the database dump. So, this need not be repeated.

    python3 code/populate_data.py


# To run the application

In RachelJacobJNeelakantanS_project/Application Code/code/home.py change the connection parameters to 
reflect user DB username and password. Then run in terminal the following command.

    streamlit run code/home.py

These are the credentials already available in the databse dump. You can also register and login as host and guest roles.

Host Credentials 

Pre-populated host - Username - frank4804@airbnb.com, Password - frank@123
Newly added host - Username - joann@airbnb.com, Password - joann@123

Guest Credentials

Newly added guest - Username - sriram@airbnb.com, Password - sriram@123
