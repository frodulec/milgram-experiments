import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Add seaborn import
from typing import List, Dict
import uuid
import datetime
import numpy as np
from dashboard_charts import (
    participant_model_violin_plot,
    provider_comparison_plot,
    plot_final_voltage_by_model,
    provider_refusal_ratio_plot,
    refusal_ratio_plot,
    participant_model_provider_violin_plot,
    ridge_voltage_by_provider,
    lollipop_mean_voltage,
    heatmap_voltage_model_provider,
    ecdf_voltage_by_provider,
)
from utils.general import get_provider_name, load_experiments



st.set_page_config(
    page_title="Milgram Experiment Dashboard",
    page_icon="⚡",
    layout="wide"
)




def main():
    st.title("⚡ Milgram Experiment Dashboard")
    
    # Load all experiments
    experiments = load_experiments()

    old_experiments = load_experiments(folder="results_19.08.2025")
    experiments.extend(old_experiments)
    
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

    # Filter by model
    model_filter = st.multiselect(
        "Filter by Participant Model",
        options=df["Participant Model"].unique(),
        default=df["Participant Model"].unique()
    )
    df = df[df["Participant Model"].isin(model_filter)]

    # Add provider information to the dataframe
    for i, row in df.iterrows():
        df.at[i, "Provider"] = get_provider_name(row["Participant Model"])
    
    # if model contains also provider, for example openai/gpt-5, leave only the model
    df['Participant Model'] = df['Participant Model'].apply(lambda x: x.split('/')[-1])

    # Model comparison
    st.header("Model Comparison")
    model_groups = df.groupby("Participant Model")
    
    model_stats = model_groups.agg({
        "Final Voltage": ["mean", "max", "count"],
        "Cost": ["mean", "sum"],
        "Messages Count": ["mean"]
    }).reset_index()
    
    st.dataframe(model_stats)

    _, mid_section, _ = st.columns([1, 2, 1])
    with mid_section:
    # Visualizations
        st.header("Experiment Visualizations")
        
        # Set a consistent theme for all seaborn plots
        sns.set_theme(style="whitegrid")
        

        st.subheader("Final Voltage by Participant Model")
        participant_model_violin_plot(df)
        st.subheader("Final Voltage by Participant Model Provider")
        participant_model_provider_violin_plot(df)
        # plot_final_voltage_by_model(df)
        # st.subheader("Final Voltage by Provider")
        # provider_comparison_plot(df)
        st.subheader("Provider Refusal Ratio")
        provider_refusal_ratio_plot(df)

        # st.subheader("Ridge: Final Voltage Distributions by Provider")
        # ridge_voltage_by_provider(df)

        # st.subheader("Mean Final Voltage with 95% CI by Provider")
        # lollipop_mean_voltage(df, group_by="Provider")

        # st.subheader("Mean Final Voltage by Model × Provider")
        # heatmap_voltage_model_provider(df)

        # st.subheader("ECDF of Final Voltage by Provider")
        # ecdf_voltage_by_provider(df)
    
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
        format_func=lambda x: f"{x[:20]} - {filtered_df[filtered_df['ID']==x]['Timestamp'].iloc[0]} - {filtered_df[filtered_df['ID']==x]['Participant Model'].iloc[0]} - {filtered_df[filtered_df['ID']==x]['Final Voltage'].iloc[0]}"
    )
    
    if selected_exp:
        # Find the selected experiment
        exp_file = filtered_df[filtered_df["ID"]==selected_exp]["Filename"].iloc[0]

        try:
            with open(os.path.join("results", exp_file), "r") as f:
                exp_details = json.load(f)
        except Exception as e:
            with open(
                os.path.join("results_19.08.2025", exp_file), "r") as f:
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
        
        if st.button("Delete Experiment"):
            os.remove(os.path.join("results", exp_file))
            st.rerun()

if __name__ == "__main__":
    main()