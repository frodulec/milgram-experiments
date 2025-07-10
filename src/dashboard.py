import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
import uuid
import datetime

st.set_page_config(
    page_title="Milgram Experiment Dashboard",
    page_icon="⚡",
    layout="wide"
)

def load_experiments() -> List[Dict]:
    """Load all experiment results from the results directory."""
    experiments = []
    
    # Check if results directory exists
    if not os.path.exists("results"):
        st.warning("Results directory not found. No experiments to display.")
        return []
    
    # Iterate through all json files in the results directory, without subfolders
    for filename in os.listdir("results"):
        if filename.startswith("experiment_") and filename.endswith(".json"):
            try:
                with open(os.path.join("results", filename), "r") as f:
                    data = json.load(f)
                    data["filename"] = filename  # Add filename for reference
                    experiments.append(data)
            except Exception as e:
                st.error(f"Error reading file {filename}: {e}")
    
    return experiments

def main():
    st.title("⚡ Milgram Experiment Dashboard")
    
    # Load all experiments
    experiments = load_experiments()
    
    if not experiments:
        st.info("No experiment data found. Run some experiments first.")
        return
    
    # Display summary stats
    st.header("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Experiments", len(experiments))
    with col2:
        avg_cost = sum(exp.get("cost", 0) for exp in experiments) / len(experiments)
        st.metric("Average Cost", f"${avg_cost:.4f}")
    with col3:
        avg_voltage = sum(exp.get("final_voltage", 0) for exp in experiments) / len(experiments)
        st.metric("Average Final Voltage", f"{avg_voltage:.1f}V")
    with col4:
        max_voltage = max(exp.get("final_voltage", 0) for exp in experiments)
        st.metric("Maximum Voltage", f"{max_voltage}V")
    
    # Create a dataframe for better viewing
    exp_data = []
    for exp in experiments:
        timestamp = exp.get("timestamp", 0)
        date_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "Unknown"
        
        config = exp.get("config", {})
        
        exp_data.append({
            "ID": exp.get("id", "Unknown"),
            "Timestamp": date_str,
            "Cost": exp.get("cost", 0),
            "Final Voltage": exp.get("final_voltage", 0),
            "Max Rounds": config.get("max_rounds", 0),
            "Participant Model": config.get("participant_model", {}).get("model", "Unknown"),
            "Learner Model": config.get("learner_model", {}).get("model", "Unknown"),
            "Professor Model": config.get("professor_model", {}).get("model", "Unknown"),
            "Messages Count": len(exp.get("messages", [])),
            "Filename": exp.get("filename", "Unknown")
        })
    
    
    df = pd.DataFrame(exp_data)
    
    # Visualizations
    st.header("Experiment Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Final Voltage Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        df["Final Voltage"].hist(bins=15, ax=ax)
        ax.set_xlabel("Voltage (V)")
        ax.set_ylabel("Count")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Cost vs. Messages Count")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df["Messages Count"], df["Cost"])
        ax.set_xlabel("Number of Messages")
        ax.set_ylabel("Cost ($)")
        st.pyplot(fig)
    
    # Model comparison
    st.header("Model Comparison")
    model_groups = df.groupby("Participant Model")
    
    model_stats = model_groups.agg({
        "Final Voltage": ["mean", "max", "count"],
        "Cost": ["mean", "sum"],
        "Messages Count": ["mean"]
    }).reset_index()
    
    st.dataframe(model_stats)
    
    # Detailed experiment data
    st.header("All Experiments")
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        model_filter = st.multiselect(
            "Filter by Participant Model",
            options=df["Participant Model"].unique(),
            default=[]
        )
    
    with col2:
        voltage_range = st.slider(
            "Final Voltage Range",
            min_value=int(df["Final Voltage"].min()),
            max_value=int(df["Final Voltage"].max()),
            value=(int(df["Final Voltage"].min()), int(df["Final Voltage"].max()))
        )
    
    # Apply filters
    filtered_df = df
    if model_filter:
        filtered_df = filtered_df[filtered_df["Participant Model"].isin(model_filter)]
    
    filtered_df = filtered_df[
        (filtered_df["Final Voltage"] >= voltage_range[0]) & 
        (filtered_df["Final Voltage"] <= voltage_range[1])
    ]
    
    st.dataframe(filtered_df)
    
    # Experiment details
    st.header("Experiment Details")
    selected_exp = st.selectbox(
        "Select experiment to view details",
        options=filtered_df["ID"].tolist(),
        format_func=lambda x: f"{x} - {filtered_df[filtered_df['ID']==x]['Timestamp'].iloc[0]}"
    )
    
    if selected_exp:
        # Find the selected experiment
        exp_file = filtered_df[filtered_df["ID"]==selected_exp]["Filename"].iloc[0]
        with open(os.path.join("results", exp_file), "r") as f:
            exp_details = json.load(f)
        
        # Show messages
        st.subheader("Conversation")
        messages = exp_details.get("messages", [])
        
        for i, msg in enumerate(messages):
            speaker = msg.get("speaker", "Unknown")
            text = msg.get("text", "")
            
            if speaker == "Professor":
                st.markdown(f"**Professor**: {text}")
            elif speaker == "Participant":
                st.markdown(f"**Participant**: {text}")
            elif speaker == "Learner":
                st.markdown(f"**Learner**: {text}")
            elif speaker == "SHOCKING_DEVICE":
                st.markdown(f"**⚡ SHOCK ⚡**: {text}")
            else:
                st.markdown(f"**{speaker}**: {text}")

if __name__ == "__main__":
    main()