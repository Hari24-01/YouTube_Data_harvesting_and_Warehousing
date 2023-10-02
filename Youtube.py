
#importing the necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector as sql
import pymongo
from googleapiclient.discovery import build
from PIL import Image


# SETTING PAGE CONFIGURATIONS
icon = Image.open(r"Z:\Streamlit app\image\Youtube_logo.png")

st.set_page_config(page_title= "Youtube Data Harvesting and Warehousing | By J.Hari_Haran",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "auto",
                   menu_items={'About': """# This app is created by *J.Hari_Haran!*"""}
                   )

# APPLYING BACKGROUND
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://wallpapercave.com/wp/wp3516810.jpg");
background-size: cover;
background-position: left-conner;
background-repeat: no-repeat;
background-attachment: local;
}}

[data-testid="stSidebar"] > div:first-child {{
background-image: url("https://azouaoui-med.github.io/pro-sidebar-template/assets/images/sidebar-bg.jpg");
background-size: cover;
background-repeat: no-repeat;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# CREATING OPTION MENU
st.sidebar.header(":grey[PLAY WITH YOUTUBE]")
with st.sidebar:
    selected = option_menu("MENU", ["Home","Extract","Transform","View"], 
                           icons=["house-door-fill","download","upload","database"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "10px", 
                                                "--hover-color": "#010001"},
                                   "icon": {"font-size": "20px"},
                                   "container" : {"max-width": "8000px"},
                                   "nav-link-selected": {"background-color": "#FF0000"}})

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="",
                   database= "Youtube_data" #SELECT DATABASE FROM SQL SERVER
                  )
mycursor = mydb.cursor(buffered=True)

# Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
client = pymongo.MongoClient("mongodb+srv://hsquarehariharan:H24hariharan@cluster0.lmpu5lp.mongodb.net/?retryWrites=true&w=majority") #CONNECT TO YOUR MONGO DB SERVER
db = client['Youtube_Data'] #SELECT DATABASE MONGO DB SERVER

# BUILDING CONNECTION WITH YOUTUBE API
api_key = "AIzaSyB8iMqZ3irEirYUVtC71eVd3eZOstJsi4c" #ADD YOUR GOOGLE YOUTUBE API KEY
youtube = build('youtube','v3',developerKey=api_key)


# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part = 'snippet,contentDetails,statistics',
                                     id= channel_id).execute()

    for i in range(len(response['items'])):
        data = dict(Channel_id = channel_id[i],
                    Channel_name = response['items'][i]['snippet']['title'],
                    Playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers_count = response['items'][i]['statistics']['subscriberCount'],
                    channel_views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    channel_description = response['items'][i]['snippet']['description'],
                    )
        ch_data.append(data)
    return ch_data


# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids


# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []
    
    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=','.join(v_ids[i:i+50])).execute()
        for video in response['items']:
            video_details = dict(Channel_name = video['snippet']['channelTitle'],
                                Channel_id = video['snippet']['channelId'],
                                Video_id = video['id'],
                                video_name = video['snippet']['title'],
                                Tags = video['snippet'].get('tags'),
                                Thumbnail = video['snippet']['thumbnails']['default']['url'],
                                video_description = video['snippet']['description'],
                                Published_date = video['snippet']['publishedAt'],
                                Duration = video['contentDetails']['duration'],
                                view_count = video['statistics']['viewCount'],
                                Likes = video['statistics'].get('likeCount'),
                                comment_count = video['statistics'].get('commentCount'),
                                Favorite_count = video['statistics']['favoriteCount'],
                                Caption_status = video['contentDetails']['caption']
                               )
            video_stats.append(video_details)
    return video_stats


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                    videoId=v_id,
                                                    maxResults=100,
                                                    pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id = cmt['id'],
                            Video_id = cmt['snippet']['videoId'],
                            Comment_text = cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author = cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date = cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count = cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count = cmt['snippet']['totalReplyCount']
                           )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data


# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():   
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name


# HOME PAGE
if selected == "Home":
    
    
    st.header(":red[Youtube Data Harvesting and Warehousing]",divider='grey')
    # Title Image
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("### :red[Domain] : Social Media")
    col1.markdown("##### :red[Technologies used] : Youtube Data API, Python, MongoDB, MySql, Streamlit")
    col1.markdown("##### :red[Overview] : Obtaining data from YouTube channels using the Google API, storing it in a MongoDB data lake, moving and translating it into a SQL database, and then querying and showing thedata in the Streamlit app.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.image(icon)
    
    
# EXTRACT and TRANSFORM PAGE
if selected == "Extract":
    st.header(":orange[EXTRACT]")
    
    # EXTRACT DATA FROM YOUTUBE AND STOREING IN MONGO DATABASE
    st.markdown("#    ")
    st.write("### Enter YouTube Channel_ID below :")
    ch_id = st.text_input("Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

    if ch_id and st.button("Extract Data"):
        ch_details = get_channel_details(ch_id)
        st.write(f'#### Extracted data from :red["{ch_details[0]["Channel_name"]}"] channel')
        st.table(ch_details)

    if st.button("Upload to MongoDB"):
        with st.spinner('Please Wait for it...'):
            ch_details = get_channel_details(ch_id)
            v_ids = get_channel_videos(ch_id)
            vid_details = get_video_details(v_ids)
                
            def comments():
                com_d = []
                for i in v_ids:
                   com_d+= get_comments_details(i)
                return com_d
            comm_details = comments()

            collections1 = db.channel_details
            collections1.insert_many(ch_details)

            collections2 = db.video_details
            collections2.insert_many(vid_details)

            collections3 = db.comments_details
            collections3.insert_many(comm_details)
            st.success("Upload to MogoDB successful !!")
      
# TRANSFORMING DATA FROM MONGO DATABASE TO SQL SERVER
if selected == "Transform":
    st.header(":orange[TRANSFORM]")  
    st.markdown("#   ")
    st.markdown("### Select a channel to begin Transformation to SQL")
        
    ch_names = channel_names()
    user_inp = st.selectbox("Select channel",options= ch_names)
        
    def insert_into_channels():
        collections = db.channel_details
        query = """INSERT INTO channels VALUES(%s,%s,%s,%s,%s,%s,%s)"""
                
        for i in collections.find({"Channel_name" : user_inp},{'_id':0}):
            mycursor.execute(query,tuple(i.values()))
            mydb.commit()
                
    def insert_into_videos():
        collectionss = db.video_details
        query1 = """INSERT INTO videos VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        for i in collectionss.find({"Channel_name" : user_inp},{"_id":0}):
            t=tuple(i.values())
            mycursor.execute(query1,t)
            mydb.commit()

    def insert_into_comments():
        collections1 = db.video_details
        collections2 = db.comments_details
        query2 = """INSERT INTO comments VALUES(%s,%s,%s,%s,%s,%s,%s)"""

        for vid in collections1.find({"Channel_name" : user_inp},{'_id' : 0}):
            for i in collections2.find({'Video_id': vid['Video_id']},{'_id' : 0}):
                t=tuple(i.values())
                mycursor.execute(query2,t)
                mydb.commit()

    if st.button("Submit"):
        try:
                
            insert_into_channels()
            insert_into_videos()
            insert_into_comments()
            st.success("Transformation to MySQL Successful!!!")
        except:
            st.error("Channel details already transformed!!")
            
# VIEW PAGE
if selected == "View":
    
    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Question',
    ['Click the question that you would like to query',
    '1. What are the names of all the videos and their corresponding channels?',
    '2. Which channels have the most number of videos, and how many videos do they have?',
    '3. What are the top 10 most viewed videos and their respective channels?',
    '4. How many comments were made on each video, and what are their corresponding video names?',
    '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
    '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
    '7. What is the total number of views for each channel, and what are their corresponding channel names?',
    '8. What are the names of all the channels that have published videos in the year 2022?',
    '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
    '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT video_name AS video_name, channel_name AS Channel_Name FROM videos ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name 
        AS Channel_Name, total_videos AS Total_Videos
                            FROM channels
                            GROUP BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write("### :red[Number of videos in each channel :]")
        st.write(df)
        
        #st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[0],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, video_name AS video_name, view_count AS view_count 
                            FROM videos
                            ORDER BY view_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write("### :red[Top 10 most viewed videos :]")
        st.write(df)
        
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, a.video_name AS video_name, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comments GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,video_name AS video_name,likes AS Likes_Count 
                            FROM videos
                            ORDER BY likes DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write("### :red[Top 10 most liked videos :]")
        st.write(df)
        
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT video_name AS video_name, likes AS Likes_Count
                            FROM videos
                            ORDER BY likes DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
         
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, channel_views AS channel_views
                            FROM channels
                            ORDER BY channel_views DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write("### :red[Channels vs Views :]")
        st.write(df)
        
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name AS Channel_Name
                            FROM videos
                            WHERE published_date LIKE '2022%'
                            GROUP BY channel_name
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        
    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name, 
                        SUM(duration_sec) / COUNT(*) AS average_duration
                        FROM (
                            SELECT channel_name, 
                            CASE
                                WHEN duration REGEXP '^PT[0-9]+H[0-9]+M[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT(
                                SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'H', 1), 'T', -1), ':',
                            SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'H', -1), ':',
                            SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                            ))
                                WHEN duration REGEXP '^PT[0-9]+M[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT(
                                '0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'T', -1), ':',
                                SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                            ))
                                WHEN duration REGEXP '^PT[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT('0:0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'T', -1)))
                                END AS duration_sec
                        FROM videos
                        ) AS subquery
                        GROUP BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names
                          )
        st.write("### :red[Average video duration for channels :]")                  
        st.write(df)
        
        

        
    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,video_id AS Video_ID,comment_count AS comment_count
                            FROM videos
                            ORDER BY comment_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :red[Videos with most comments :]")
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[2],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
