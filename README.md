#          __YouTube_Data_harvesting_and_Warehousing__
## __YouTube Data Harvesting and Warehousing using PYTHON, SQL, MongoDB and Streamlit.__

### PROBLEM STATEMENT:
The aim of the project is to develop a Streamlit application that enables users to access and examine data from various YouTube channels.

### PLATFORMS USED:
PYTHON ; ATLAS MONGO DB ; XAMPP SQL ; STREAMLIT

### LIBRARY USED:
pandas, plotly.express, streamlit, mysql.connector, pymongo, googleapiclient.discovery

### PROCEDURE:
#### __STEP 1:__ Set up a Streamlit app:
Utilise the Python package "streamlit" to build a Streamlit application to manage YouTube channels, manage channel information, and migrate channels.
#### __STEP 2:__ Connect to the YouTube API:
Using the Google API client module, establish a Python connection to the YouTube API V3 to retrieve channel and video data.
#### __STEP 3:__ Store data in a MongoDB data lake:
By developing an API call method and saving the data in three collections, the information is kept in a MongoDB data lake that can handle unstructured and semi-structured data.
#### __NOTE:__ Make sure you have built the necessary databases (such as "YouTube") and collections or Tables in MONGO DB and SQL before executing the programme.
#### __STEP 4:__ Migrate data to a SQL data warehouse:
Using a SQL database like MySQL or XAMPPSQL, the data collected from multiple channels, including channel details, videos, and comments, is moved to a SQL data warehouse.
#### __STEP 5:__ Query the SQL data warehouse:
Use SQL queries to link tables in a data warehouse and obtain channel data depending on user input, while ensuring correct foreign and primary key assignment.
#### __STEP 6:__ Display data in the Streamlit app:
The obtained data is shown within the Streamlit application, where it is used to build charts and graphs for user analysis.

