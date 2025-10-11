import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# Page title

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Sidebar with image
st.sidebar.container(horizontal_alignment="center")
st.sidebar.image("photo.png", width=200)  # Adjust width as needed
st.sidebar.markdown("""                   
                    <h3 style='text-align: center;'>
                    Myself<br>Syed Fazlur Rehman
                    <br>AI Enthisiust</h3>""",
    unsafe_allow_html=True)

st.title("📊 Students Performance Report")
st.write("---")

st.set_page_config(page_title="Home", page_icon=":house:", layout="centered")
df = pd.read_csv('StudentsPerformance.csv')

# Sidebar UI
st.sidebar.header("🔧 Menu")

# Sidebar: Action menu with radio buttons
menu = st.sidebar.radio(
    "Choose an action:",
    ["📄 Show Raw Data", "📈 Summary Statistics", "📊 Score Distribution", "📊 Average Scores"]
)

def filteredby(col_name):
    selected_row_options = []
    col = df[col_name].unique().tolist()
    selected_row_options = st.multiselect(f"Filter by {col_name.title()}", options=col, default=col)
    filtered = df[df[col_name].isin(selected_row_options)]
    return filtered

selected_col = st.selectbox("Select column", ["Gender", "Race/Ethnicity", "Parental Level of Education","Lunch","Test Preparation Course"]).lower()
filtered_df = filteredby(selected_col)

# Action handling
if menu == "📄 Show Raw Data":
    st.subheader("📄 Raw Data")
    st.dataframe(filtered_df)

elif menu == "📈 Summary Statistics":
    st.subheader("📈 Summary Statistics")
    st.write(filtered_df.describe())

elif menu == "📊 Score Distribution":
    st.subheader("📊 Score Distribution")

    subject = st.selectbox("Choose subject to plot", ["math score", "reading score", "writing score"])

    fig, ax = plt.subplots()
    ax.hist(filtered_df[subject], bins=20, color='skyblue', edgecolor='black',)
    ax.set_title(f"{subject.title()} Distribution")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Students")
    st.pyplot(fig)

elif menu == "📊 Average Scores":
    st.subheader(f"📊 Average Scores by {selected_col}")

    avg_scores = filtered_df.groupby(selected_col)[["math score", "reading score", "writing score"]].mean()

    fig, ax = plt.subplots()
    avg_scores.plot(kind="bar", ax=ax, colormap="Set2")
    ax.set_title(f"Average Scores by {selected_col}")
    ax.set_ylabel("Average Score")
    ax.set_ylim(0, 100)
    st.pyplot(fig)


