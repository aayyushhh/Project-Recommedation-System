import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import plotly.express as px
import base64
import openai
import pymongo
import streamlit.components.v1 as components
import json
from streamlit_lottie import st_lottie
import requests

openai.api_key = "API-key"
# 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
myclient=pymongo.MongoClient('mongodb://localhost:27017')

mydb=myclient['pss']
mycol=mydb['projects']
mycol2=mydb['users']

model_engine = "text-davinci-003"
st.set_page_config(page_title="Project Predictor", layout="wide")

def show_project(recommended_project,i,level):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Objective:** {recommended_project['Project_domain']}")
        st.write(f"**Output:** {recommended_project['Project_title']}")
        st.write(f"**Type:** {recommended_project['Project_type']}")
    

    c=recommended_project['Project_domain']
    y= c.replace(" ", "+")
    d=recommended_project['Project_title']
    x = d.replace(" ", "+")
    e=recommended_project['Project_type']
    f=recommended_project["Required_Skills"]
    data={ "Project_title":d,'Project_type':e,'Required_Skills':f , 'Project_domain':c }

        
    j=str(i+100)
    k=str(i+200)
    l=str(i+300)
    
    
    with col2:
        st.write(f"**Desc:** {recommended_project['Description']}")
        
        # b1=st.button("steps to do?", key=j )
        # b2=st.button("startup strategy", key=k )
        
        # b3=st.button("Add to favourites",key=l)
        c1, c2,c3 = st.columns(3)

        with c1:
            b1=st.button("steps to do?", key=j )

        with c2:
            b2=st.button("startup strategy", key=k )

        with c3:
            b3=st.button("Star It",key=l)
        
    
    
    st.markdown(f"[Show Project samples](https://www.google.com/search?q="+x+"+project+using+"+y+"+github)")
    prom="steps to create "+d+" using "+c
    prom2="steps to start buissness startup for "+d+" project"
    if b1:
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prom,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response = completion.choices[0].text
        # print(response)
        st.write(response)
    
    if b2:
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prom2,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response1 = completion.choices[0].text
        # print(response)
        st.write(response1)
    
    if b3:
        inserted=mycol.insert_one(data)
        st.success("Added to favourites")
    
    # st.write(f"**GitHub:** [{recommended_project['Project_title']}]({recommended_project['GitHub']})")
    st.write("-----")

st.sidebar.title("Enter Your Skills")
# st.sidebar.markdown("Please enter your skills separated by commas.")





# Set the app title and sidebar




# Get the user input and transform it into a TF-IDF vector
options = ["HTML & CSS", "React", "Angular","Nodejs","Flask","Flutter","Machine learning","Deep Learning","Data Science","Java","Kotlin","Python","Sql","PyQt5","logistic regression & R"," Apriori and Fp Growth data mining algorithms","blockchain technology and AI","AI and ML","Html & CSS & ASP.NET","Html & CSS & JavaScript & MYSQL.","Html & CSS &  JavaScript & ASP.net","Crypto","3D printing & Bluetooth","Html & CSS & JavaScript & MySQL Database & Django"]

selected_options = st.sidebar.multiselect("Select options:", options)





user_input=""
sta=""
if len(selected_options) > 0:
    for option in selected_options:
        sta=sta+","+option
    # st.write(sta)
    user_input=sta
else:
    
    original_title = '<p class="og" style=" color:Orange; on ">Please select at least one option.</p>'
    st.sidebar.write(original_title, unsafe_allow_html=True)


level_type=["","Easy","Moderate","Tough"]
level=st.sidebar.selectbox("select level", level_type)

project_df = pd.read_excel("Proj_list.xlsx")

if level == "":
    projects_df=project_df
else:
        # df = df[df['Symbol'] == selected_stock]
    projects_df=project_df[project_df["Difficulty_level"]== level]
    


# Load the project dataset


# Create a TF-IDF vectorizer and fit it to the project skills
tfidf = TfidfVectorizer()
tfidf.fit(projects_df["Required_Skills"])

# user_input = st.sidebar.text_input("", "")
user_skills_tfidf = tfidf.transform([user_input])


ques = st.sidebar.text_input("Enter your query related to project?", "")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")

saved=st.sidebar.button("Favourites",key="uni")



# Calculate the cosine similarity between the user skills and the project skills
similarity_scores = cosine_similarity(user_skills_tfidf, tfidf.transform(projects_df["Required_Skills"]))

# Sort the similarity scores and get the top 5 matching projects
top_indices = similarity_scores.argsort()[0][::-1][:25]
top_projects = projects_df.iloc[top_indices]



href=""

# Show the recommended projects
if user_input:
    st.title("Recommended Projects")
    for i, project in top_projects.iterrows():
        show_project(project,i,level)
    recommended_projects_df = pd.DataFrame({
        "Objective": top_projects["Project_domain"],
        "Output": top_projects["Project_title"],
        "Type": top_projects["Project_type"],
        "Desc": top_projects["Description"]
    })
    
    # Add a button to download the recommended projects as a CSV file
    csv = recommended_projects_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="recommended_projects.csv">Download CSV File</a>'
    

elif ques:
    st.title("Answer to your Query")
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=ques,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = completion.choices[0].text
    # print(response)
    st.write(response)

elif saved:
    st.title("Favourites: ")
    for n in mycol.find():
        
        st.write("**Objective:** " ,n["Project_domain"])
        st.write("**Output:** " ,n['Project_title'])
        st.write("**Type:** " ,n["Project_type"])
        st.sidebar.write(" ")
        st.sidebar.write(" ")
        dele=st.button("Delete", key=n["_id"] ) 
        g=n["_id"]
        st.write("-----")
        if dele:
            myquery = { "_id": n["_id"] }
            mycol.delete_one(myquery)


else:
    st.title("Welcome to Project Predictor")
    st.write("Please enter your skills to get project recommendations.")
    a= ""
    components.html(
        """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    * {box-sizing: border-box;}
    body {font-family: Verdana, sans-serif;}
    .mySlides {display: none;}
    img {vertical-align: middle;}

    /* Slideshow container */
    .slideshow-container {
    max-width: 800px;
    position: relative;
    margin: auto;
    margin-left:30px;
    }

    /* Caption text */
    .text {
    color: #f2f2f2;
    font-size: 15px;
    padding: 8px 12px;
    position: absolute;
    bottom: 8px;
    width: 100%;
    text-align: center;
    }

    /* Number text (1/3 etc) */
    .numbertext {
    color: #f2f2f2;
    font-size: 12px;
    padding: 8px 12px;
    position: absolute;
    top: 0;
    }

    /* The dots/bullets/indicators */
    .dot {
    height: 15px;
    width: 15px;
    margin: 0 2px;
    background-color: #bbb;
    border-radius: 50%;
    display: inline-block;
    transition: background-color 0.6s ease;
    }

    .active {
    background-color: #717171;
    }

    /* Fading animation */
    .fade {
    animation-name: fade;
    animation-duration: 1.5s;
    }

    @keyframes fade {
    from {opacity: .4} 
    to {opacity: 1}
    }

    /* On smaller screens, decrease text size */
    @media only screen and (max-width: 300px) {
    .text {font-size: 11px}
    }

    .animate-charcter
    {
    text-transform: uppercase;
    background-image: linear-gradient(
        -225deg,
        #231557 0%,
        #44107a 29%,
        #ff1361 67%,
        #fff800 100%
    );
    background-size: auto auto;
    background-clip: border-box;
    background-size: 200% auto;
    color: #fff;
    background-clip: text;
    text-fill-color: transparent;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textclip 2s linear infinite;
    display: inline-block;
        font-size: 40px;
        margin-left:29%;
        margin-top:-20px;
    }

    @keyframes textclip {
    to {
        background-position: 200% center;
    }
    }

    </style>
    </head>
    <body style='background-color:rgb(14, 17, 23);;'>



    
    <div class="slideshow-container">
    <h1>"""+a+"""</h1>

    <div class="mySlides fade">
    <div class="numbertext">1 / 6</div>
    <img src="https://dsc.ui.ac.id/wp-content/uploads/2023/02/web-devel.jpg" style="width:685px;height:460px;box-shadow: 7px 7px 15px purple;">
    
    </div>

    <div class="mySlides fade">
    <div class="numbertext">2 / 6</div>
    <img src="https://riseuplabs.com/wp-content/uploads/2021/07/mobile-application-development-guidelines-riseuplabs.jpg" style="width:685px;height:460px;box-shadow: 7px 7px 15px purple;">
    
    </div>

    <div class="mySlides fade">
    <div class="numbertext">3 / 6</div>
    <img src="https://static1.shine.com/l/m/images/blog/Machine_Learning_Interview_Questions.jpg" style="width:685px;height:450px;box-shadow: 7px 7px 15px purple;">

    </div>

    <div class="mySlides fade">
    <div class="numbertext">4 / 6</div>
    <img src="https://www.simplilearn.com/ice9/free_resources_article_thumb/iot-explained-what-it-is-how-it-works-and-its-applications-banner.jpg" style="width:685px;height:450px;box-shadow: 7px 7px 15px purple;">

    </div>

    <div class="mySlides fade">
    <div class="numbertext">5 / 6</div>
    <img src="https://images.livemint.com/img/2021/09/21/1600x900/t1_(2)_1632214319987_1632214326323.jpg" style="width:685px;height:450px;box-shadow: 7px 7px 15px purple;">
    
    </div>

    <div class="mySlides fade">
    <div class="numbertext">6 / 6</div>
    <img src="https://etimg.etb2bimg.com/photo/97787288.cms" style="width:685px;height:450px;box-shadow: 7px 7px 15px purple;">
    
    </div>

    </div>
    <br>

    <div style="text-align:center">
    <span class="dot"></span> 
    <span class="dot"></span> 
    <span class="dot"></span> 
    <span class="dot"></span> 
    <span class="dot"></span> 
    <span class="dot"></span> 
    </div>

    <script>
    let slideIndex = 0;
    showSlides();

    function showSlides() {
    let i;
    let slides = document.getElementsByClassName("mySlides");
    let dots = document.getElementsByClassName("dot");
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";  
    }
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}    
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex-1].style.display = "block";  
    dots[slideIndex-1].className += " active";
    setTimeout(showSlides, 2000); // Change image every 2 seconds
    }
    </script>

    </body>
    </html> 

        """,
    height=600,
    )
    
st.sidebar.markdown(href, unsafe_allow_html=True)  

# Count of skills in dataset
count_df = pd.DataFrame({
    'skills': tfidf.get_feature_names_out(),
    'count': tfidf.transform(projects_df["Required_Skills"]).sum(axis=0).A1
})
count_df = count_df.sort_values('count', ascending=False)

# Show the skill count graph
st.title("Skills Count in Dataset")
fig = px.bar(count_df[:20], x='skills', y='count')
st.plotly_chart(fig)

