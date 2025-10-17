from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# Page title
st.title("📊 Students Performance Report")
st.write("---")

st.set_page_config(page_title="Home", page_icon=":house:", layout="centered")

# Sidebar with image
st.sidebar.container(horizontal_alignment="center")
st.sidebar.image("photo.png", width=200)  # Adjust width as needed
st.sidebar.markdown("""                   
                    <h3 style='text-align: center;'>
                    Myself<br>Syed Fazlur Rehman
                    <br>AI Enthisiust</h3>""",
    unsafe_allow_html=True)

# Sidebar UI
st.sidebar.header("🔧 Menu")

menu_category = ["📄 Show Raw Data", 
                 "📈 Summary Statistics", 
                 "📊 Stacked Score Distribution", 
                 "📊 Scores Comparison", 
                 "📊 Distribution by category", 
                 "📊 Category Impact on Scores", 
                 "📊 Correlation by Subjects"]

categories = ["Gender", 
            "Race/Ethnicity", 
            "Parental level of Education",
            "Lunch",
            "Test Preparation Course"]

subjects = ["Math Score", 
            "Reading Score", 
            "Writing Score",
            "Average Score"]

# Sidebar: Action menu with radio buttons
menu = st.sidebar.radio(
    "Choose an action:", menu_category
)

def load_data(filename):
    try:
        df = pd.read_csv(filename)        
        #st.success(f"Data loaded successfully from {filename}")
    except FileNotFoundError:
        st.error("File not found in the specified path!")
        st.stop() 
    return df


def load_clean_n_save_df(filename,filename2):
    try:
        df_clean = load_data(filename).copy()  # work on a copy to keep original intact
        # Build a rename map defensively so it works even if original columns vary slightly.
        rename_map = {}
        for col in df_clean.columns:
            c = col.strip().lower()
            c = c.replace(' ', '_')
            rename_map[col] = c

        df_clean = df_clean.rename(columns=rename_map)
        #st.success("Data cleaned and columns renamed sucessfully.")      
        #st.warning('No null column found.' if df_clean.isna().sum()==0 else f'{df_clean.isna().sum()} columns found null.')
    except NameError:
        st.error("Failed to clean or renaming dataset!")

    # Adding Column average score
    df_clean['average_score'] = df_clean[['math_score', 'reading_score', 'writing_score']].mean(axis=1)
    #st.success("Average column added.")
    # Simple pass/fail rule (example): pass if average >= 60
    df_clean['result'] = df_clean['average_score'] >= 60
    #st.success("Passed column added.")
    #print('Added columns: avg_score, passed')
    #st.write(df_clean[['avg_score']].head())

    try:
        out_path = Path(filename2)
        df_clean.to_csv(out_path, index=False)           # index=False avoids writing row numbers as an extra column
        #st.success(f"Cleaned dataset saved successfully to: {out_path.resolve()}")
    except NameError:
        st.error("Failed to save cleaned dataset.")

    
# loading raw data, cleaning it then saving it to clean file
load_clean_n_save_df('datasets/StudentsPerformance.csv','datasets/students_performance_cleaned.csv')

# loading cleaned data
cleaned_df = load_data('datasets/students_performance_cleaned.csv')

def filteredby(col_name):

    df_for_filter = cleaned_df
     # ✅ Initialize selected_row_options to avoid reference before assignment
    #st.write(df.head())
    selected_row_options = []
    col = df_for_filter[col_name].unique().tolist()
    

    selected_row_options = st.multiselect(f"Filter by {col_name.title()}", options=col, default=col)
    filtered = df_for_filter[df_for_filter[col_name].isin(selected_row_options)]
    # ✅ Ensure user selects at least one option
    if not selected_row_options:
        st.warning("⚠️ Please select at least one option to continue.")
        st.stop()  # stop execution until they select something
    return filtered

sns.set_theme(style="darkgrid")
#plt.style.use('dark_background')  # Using a different style for better aesthetics
fig, ax = plt.subplots()
sns.color_palette("rocket")
# Action handling
if menu == menu_category[0]:
    st.subheader("📄 Raw Data")
    st.dataframe(cleaned_df)

elif menu == menu_category[1]:
    st.subheader("📈 Summary Statistics")
    st.write(cleaned_df.describe())

elif menu == menu_category[2]:
    col1, col2 = st.columns([5,3])
    with col1:
        selected_col = st.selectbox("Select Category:", categories,key='col')
        bn = st.slider("Number of Bins", min_value=5, max_value=100, value=15, step=1)    
    with col2:
        subject = st.selectbox("**Select Subject:**", subjects)
        kde = st.checkbox("Kernel Density Estimate", value=False)    
        
    st.subheader("📊 Proportion of Scores Across Categories")
    
    

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.histplot(
        data=cleaned_df,
        x=subject.replace(" ", "_").lower(),
        hue=selected_col.replace(" ", "_").lower(),
        bins=bn,
        kde=kde,
        multiple="stack",
        ax=ax
    )

    # Format X-axis labels
    ax.set_xlabel(subject.title())
    ax.set_ylabel("Count")

    # Beautify tick labels
    ax.set_xticklabels(
        [label.get_text().replace("_", " ").title() for label in ax.get_xticklabels()],
        rotation=0
    )

    # Format legend labels dynamically
    handles, labels = ax.get_legend_handles_labels()
    labels = [label.replace("_", " ").title() for label in labels]
    ax.legend(handles, labels, title=selected_col.title())

    # Optional: Add a dynamic title
    ax.set_title(f"{subject.title()} Distribution by {selected_col.title()}")
    st.pyplot(fig)

elif menu == menu_category[3]:

    col1, col2 = st.columns([3,5])
    with col1:
        selected_col = st.selectbox("Select Category:", categories)
    with col2:
        filter_col = selected_col.replace(" ","_").lower()    
        filtered_df = filteredby(filter_col)

    st.subheader(f"📊 Average Scores by {selected_col}")
    avg_scores = filtered_df.groupby(filter_col)[["math_score", "reading_score", "writing_score","average_score"]].mean()
    avg_scores.plot(kind="bar", ax=ax, rot=45 if filter_col == 'parental_level_of_education' else 0)
    ax.set_title(f"Scores by {selected_col}")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average Score")
        
    ax.set_xticklabels([label.get_text().replace("_", " ").title() for label in ax.get_xticklabels()])
    ax.set_xlabel(selected_col.title())

    # Format legend labels
    handles, labels = ax.get_legend_handles_labels()
    labels = [label.replace("_", " ").title() for label in labels]
    ax.legend(handles, labels, title="Scores")
    st.pyplot(fig)

elif menu == menu_category[4]:

    selected_col = st.selectbox("Select Category:", categories)
    filter_col = selected_col.replace(" ","_").lower()    

    #st.subheader(f"📊 Percentage by {selected_col}")
    fig, ax = plt.subplots(figsize=(6,6))    
    # Create pie chart
    values = cleaned_df[filter_col].value_counts()

    labels = [label.replace("_", " ").title() for label in values.index]
    
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,          # ✅ outer labels (this adds them)
        autopct='%1.0f%%',      # show percentages inside
        startangle=120,
    )
    ax.set_title(f"{selected_col.title()} Distribution")

    # ✅ Add legend aligned to the corner
    ax.legend(
        wedges,
        labels,
        title=selected_col.title(),
        loc="lower left",      # <--- change corner here
        bbox_to_anchor=(1, 0.5, 0.5, 0.5),  # move legend fully outside pie
    )

    # ✅ Tighten layout & remove unnecessary whitespace
    fig.subplots_adjust(left=0.05, right=0.75, top=0.9, bottom=0.05)
    
    #fig.tight_layout()
    st.pyplot(fig)
elif menu == menu_category[5]:
    st.subheader('How Different Factors Influence Student Achievement')
    
    col1, col2 = st.columns([5,3])
    with col1:
        selected_col = st.selectbox("Select Category:", categories,key='col')
    with col2:
        subject = st.selectbox("**Select Subject:**", subjects)
        ssize = st.slider("Scatter size: ", min_value=1, max_value=10, value=4, step=1)    

    ax.set_title(f"{subject} Distribution by {selected_col}")
    
    sns.swarmplot(data=cleaned_df, 
                x=subject.lower().replace(" ","_"), 
                y=selected_col.replace(" ","_").lower(),
                size=ssize,
                hue="result",
                ax=ax
                )  # seaborn computes mean by default for barplot
    ax.set_xlabel(selected_col.title())
    ax.set_ylabel(subject.title())  
    ax.set_yticklabels([label.get_text().capitalize() for label in ax.get_yticklabels()])
    # ✅ Capitalize legend (hue) labels
    handles, labels = ax.get_legend_handles_labels()
    labels = ['Pass' if label == 'True' else 'Fail' for label in labels]
    ax.legend(handles, labels, title="Result")

    st.pyplot(fig)

elif menu == menu_category[6]:
    st.subheader('Correlation Between Subjects')

    sns.heatmap(cleaned_df[['math_score','reading_score','writing_score','average_score']].corr(), annot=True, cmap='coolwarm')
    ax.set_title("Inter-Subject Correlation Analysis")
    ax.set_xticklabels([label.get_text().replace("_score", "").title() for label in ax.get_xticklabels()])
    ax.set_yticklabels([label.get_text().replace("_score", "").title() for label in ax.get_yticklabels()], rotation=90)
    st.pyplot(fig)
    
#labeldistance=1.1       # move labels slightly outward
    #handles, labels = ax.get_legend_handles_labels()
    #labels = [label.replace("_", " ").title() for label in labels]
    #ax.legend(handles, labels,loc="bottom right")
    

