from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------- PAGE SETUP ----------------------
st.title("📊 Students Performance Report")
st.write("---")
st.set_page_config(page_title="Home", page_icon=":house:", layout="centered")

# ---------------------- SIDEBAR CONFIGURATION ----------------------
st.sidebar.container(horizontal_alignment="center")
st.sidebar.image("photo.png", width=200)  # Display profile image
st.sidebar.markdown("""                   
                    <h3 style='text-align: center;'>
                    Myself<br>Syed Fazlur Rehman
                    <br>AI Enthisiust</h3>""",
    unsafe_allow_html=True)

# Sidebar navigation header
st.sidebar.header("🔧 Menu")

# ---------------------- MENU OPTIONS ----------------------
menu_category = [
    "📄 Show Raw Data", 
    "📈 Summary Statistics", 
    "📊 Stacked Score Distribution", 
    "📊 Scores Comparison", 
    "📊 Proportion by Key Factor", 
    "📊 Category Impact on Scores", 
    "📊 Correlation by Subjects"
]

# Available categorical filters
categories = [
    "Gender", 
    "Race/Ethnicity", 
    "Parental level of Education",
    "Lunch",
    "Test Preparation Course"
]

# Core academic subjects
subjects = [
    "Math Score", 
    "Reading Score", 
    "Writing Score",
    "Average Score"
]

# Sidebar: Action menu
menu = st.sidebar.radio("Choose an action:", menu_category)

# ---------------------- DATA LOADING ----------------------
def load_data(filename):
    """Load CSV dataset and handle missing file errors."""
    try:
        df = pd.read_csv(filename)        
    except FileNotFoundError:
        st.error("File not found in the specified path!")
        st.stop() 
    return df

def load_clean_n_save_df(filename, filename2):
    """Clean, standardize, and save dataset with computed columns."""
    try:
        df_clean = load_data(filename).copy()  # Work on a copy
        rename_map = {}
        # Clean column names
        for col in df_clean.columns:
            c = col.strip().lower().replace(' ', '_')
            rename_map[col] = c

        df_clean = df_clean.rename(columns=rename_map)
        #st.success("Data cleaned and columns renamed successfully.")      
    except NameError:
        st.error("Failed to clean or rename dataset!")

    # Add computed columns
    df_clean['average_score'] = df_clean[['math_score', 'reading_score', 'writing_score']].mean(axis=1)
    #st.success("Average column added.")
    df_clean['result'] = df_clean['average_score'] >= 60
    #st.success("Passed column added.")

    # Save cleaned dataset
    try:
        out_path = Path(filename2)
        df_clean.to_csv(out_path, index=False)
    except NameError:
        st.error("Failed to save cleaned dataset.")

# Process and clean data once
load_clean_n_save_df('datasets/StudentsPerformance.csv', 'datasets/students_performance_cleaned.csv')

# Load cleaned data
cleaned_df = load_data('datasets/students_performance_cleaned.csv')

# ---------------------- FILTER FUNCTION ----------------------
def filteredby(col_name):
    """Filter dataset interactively using a category."""
    df_for_filter = cleaned_df
    col = df_for_filter[col_name].unique().tolist()
    selected_row_options = st.multiselect(f"Filter by {col_name.title()}", options=col, default=col)
    filtered = df_for_filter[df_for_filter[col_name].isin(selected_row_options)]

    # Require at least one selection
    if not selected_row_options:
        st.warning("⚠️ Please select at least one option to continue.")
        st.stop()
    return filtered

# ---------------------- PLOT STYLE ----------------------
plt.style.use('dark_background')
fig, ax = plt.subplots()
sns.color_palette("rocket")

# ---------------------- MENU HANDLER ----------------------

# ---------- OPTION 1: RAW DATA ----------
if menu == menu_category[0]:
    st.subheader("📊 Dataset Overview")
    st.write("This section presents the refined student performance dataset, showcasing all relevant variables after data cleaning and preprocessing for analysis.")
    st.dataframe(cleaned_df)

# ---------- OPTION 2: SUMMARY STATISTICS ----------
elif menu == menu_category[1]:
    st.subheader("📑 Statistical Overview")
    st.write("The following descriptive statistics provide insight into the distribution, spread, and central tendency of core academic performance metrics.")
    st.write(cleaned_df.describe())

# ---------- OPTION 3: STACKED SCORE DISTRIBUTION ----------
elif menu == menu_category[2]:
    st.subheader("📊 Score Distribution Across Categories")
    st.write(
        "This visualization illustrates how student performance in the selected subject is distributed across different categorical groups."
    )
    col1, col2 = st.columns([5,3])
    with col1:
        selected_col = st.selectbox("Select Category:", categories, key='col')
        bn = st.slider("Number of Bins", min_value=5, max_value=100, value=15, step=1)    
    with col2:
        subject = st.selectbox("**Select Subject:**", subjects)
        kde = st.checkbox("Kernel Density Estimate", value=False)    
    
    # Create histogram
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(
        data=cleaned_df,
        x=subject.replace(" ", "_").lower(),
        hue=selected_col.replace(" ", "_").lower(),
        bins=bn,
        kde=kde,
        multiple="stack",
        ax=ax,
        legend=False
    )

    # Add custom legend
    unique_vals = cleaned_df[selected_col.replace(" ", "_").lower()].unique()
    for val in unique_vals:
        ax.bar(0, 0, label=str(val).title())
    ax.legend(title=selected_col.title(), loc='upper left')

    # Chart labels
    ax.set_xlabel(subject.title())
    ax.set_ylabel("Count")
    ax.set_title(f"{subject.title()} Distribution by {selected_col.title()}")
    plt.tight_layout()
    st.pyplot(fig)

# ---------- OPTION 4: SCORE COMPARISON ----------
elif menu == menu_category[3]:
    st.subheader("Mean Academic Performance by Category")
    st.write("This visualization presents the mean student performance across core subjects segmented by category.")
    col1, col2 = st.columns([4,4])
    with col1:
        selected_col = st.selectbox("Select Category:", categories, key="col")
        filter_col = selected_col.replace(" ", "_").lower()
    with col2:
        inv = st.checkbox("Inverse factors", value=False)

    # Group by selected category
    avg_scores = cleaned_df.groupby(filter_col)[[s.lower().replace(" ", "_") for s in subjects]].mean()
    if inv:
        avg_scores = avg_scores.T  # Transpose if inverse view selected

    # Plot grouped averages
    fig, ax = plt.subplots(figsize=(8,5))
    avg_scores.plot(
        kind="bar",
        ax=ax,
        rot=0 if not inv and filter_col != "parental_level_of_education" else 45,
        width=0.75,
        edgecolor="black"
    )

    ax.set_title(f"Score comparison grouped by {selected_col if not inv else 'Subjects'}")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score Secured")
    ax.set_xticklabels([label.get_text().replace("_", " ").title() for label in ax.get_xticklabels()])
    ax.set_xlabel(selected_col.title() if not inv else "Subjects")

    # Format legend
    handles, labels = ax.get_legend_handles_labels()
    labels = [label.replace("_", " ").title() for label in labels]
    ax.legend(handles, labels, title="Scores" if not inv else selected_col.title(), loc='upper left')
    st.pyplot(fig)

# ---------- OPTION 5: PROPORTION BY FACTOR ----------
elif menu == menu_category[4]:
    st.subheader("Proportion of Students by Key Factors")
    st.write("This pie chart illustrates the distribution of students across categories.")
    selected_col = st.selectbox("Select Category:", categories)
    filter_col = selected_col.replace(" ","_").lower()    

    # Create pie chart
    fig, ax = plt.subplots(figsize=(6,6))
    values = cleaned_df[filter_col].value_counts()
    labels = [label.replace("_", " ").title() for label in values.index]
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.0f%%', startangle=120)
    ax.set_title(f"{selected_col.title()} Distribution")

    # Add legend outside chart
    ax.legend(wedges, labels, title=selected_col.title(), loc="lower left", bbox_to_anchor=(1, 0.5, 0.5, 0.5))
    fig.subplots_adjust(left=0.05, right=0.75, top=0.9, bottom=0.05)
    st.pyplot(fig)

# ---------- OPTION 6: FACTOR IMPACT ----------
elif menu == menu_category[5]:
    st.subheader('How Different Factors Influence Student Achievement')
    st.write("Explore how various socio-demographic and academic factors impact student scores through a swarm plot visualization.")
    col1, col2 = st.columns([4,4])
    with col1:
        factor1 = st.selectbox("Select factor 1:", categories+["Result"],key='f1')
        factor2 = st.selectbox("Select factor 2:", categories+["Result"],index=5,key='f2')
    with col2:
        subject = st.selectbox("**Select Subject:**", subjects)
        ssize = st.slider("Scatter size: ", min_value=1, max_value=10, value=4, step=1)    

    ax.set_title(f"{subject} distribution by {factor2}")

    # Ensure factors differ
    if factor1 == factor2:
        st.warning("⚠️ Please select two different factors to continue.")
        st.stop()
        
    # Create swarm plot
    sns.swarmplot(
        data=cleaned_df, 
        x=subject.lower().replace(" ","_"), 
        y=factor1.replace(" ","_").lower(),
        size=ssize,
        hue=factor2.replace(" ","_").lower(),
        ax=ax
    )
    ax.set_ylabel(factor1.title())
    ax.set_xlabel(subject.title())  
    ax.set_yticklabels([label.get_text().capitalize() for label in ax.get_yticklabels()])

    # Customize legend
    handles, labels = ax.get_legend_handles_labels()
    labels = [['Pass' if label == 'True' else 'Fail' for label in labels] if factor2 == "Result" else [label.replace("_", " ").title() for label in labels]][0]
    ax.legend(handles, labels, title=factor2.title(), loc='upper left')
    st.pyplot(fig)

# ---------- OPTION 7: SUBJECT CORRELATION ----------
elif menu == menu_category[6]:
    st.subheader("📊 Subject-Wise Correlation Matrix")
    st.write("The correlation matrix quantifies relationships between core subjects, identifying interdependencies in academic performance.")
    sns.heatmap(cleaned_df[['math_score','reading_score','writing_score','average_score']].corr(), annot=True, cmap='coolwarm')
    ax.set_title("Inter-Subject Correlation Analysis")
    ax.set_xticklabels([label.get_text().replace("_score", "").title() for label in ax.get_xticklabels()])
    ax.set_yticklabels([label.get_text().replace("_score", "").title() for label in ax.get_yticklabels()], rotation=90)
    st.pyplot(fig)
