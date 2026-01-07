import streamlit as st
import pandas as pd

def format_time(total_seconds):
    """Formats seconds into MM:SS.ss string."""
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"

def main():
    st.set_page_config(page_title="Indoor Track Pacer", page_icon="🏃", layout="centered")

    # Custom CSS for a more "premium" feel and mobile optimization
    st.markdown("""
        <style>
        /* Force a clean light theme with dark text */
        .main {
            background-color: #f8f9fa;
        }
        /* Ensure all text/labels are dark for visibility on light background */
        .stApp, .stMarkdown, p, label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stMetric label {
            color: #1E1E1E !important;
        }
        /* Specific fix for headers and metrics */
        h1, h2, h3, [data-testid="stMetricValue"] > div {
            color: #1E1E1E !important;
            font-family: 'Inter', sans-serif;
        }
        .stButton button {
            background-color: #FF4B4B;
            color: white !important;
            border-radius: 8px;
            font-weight: bold;
            padding: 0.6rem 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #FF6B6B;
            color: white !important;
        }
        /* Make the dataframe readable */
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            color: #1E1E1E !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Indoor Track Pacer")

    # Input Section
    with st.container():
        event_options = ["55m", "60m", "200m", "300m", "400m", "500m", "600m", "800m", "1000m", "1500m", "1600m", "3000m"]
        event_dist_str = st.selectbox("Event Selector", event_options, index=4) # Default 400m
        event_distance = float(event_dist_str.replace('m', ''))

        st.write("**Personal Record (PR)**")
        col1, col2 = st.columns(2)
        with col1:
            pr_min = st.number_input("Minutes", min_value=0, value=0, step=1)
        with col2:
            pr_sec = st.number_input("Seconds", min_value=0.0, max_value=59.99, value=50.0, step=0.1)

        track_dist = st.number_input("Distance per Lap (m)", min_value=1, value=200, step=1)
        
        display_half_laps = st.checkbox("Display half laps")

        if st.button("Pace it", use_container_width=True):
            # Calculations
            total_pr_seconds = (pr_min * 60) + pr_sec
            
            if event_distance == 0:
                st.error("Event distance cannot be zero.")
                return

            total_laps = event_distance / track_dist
            pace_per_lap = total_pr_seconds / total_laps
            
            # Results Display
            st.divider()
            
            if display_half_laps:
                half_lap_pace = pace_per_lap / 2
                st.metric(label="Half Lap Pace", value=format_time(half_lap_pace))
            
            st.metric(label="Full Lap Pace", value=format_time(pace_per_lap))

            # Split Table Generation
            st.subheader("Split Table")
            splits = []
            cumulative_time = 0
            
            # We want a split for every full lap (and possibly the final fractional lap)
            num_full_laps = int(total_laps)
            remainder = total_laps - num_full_laps
            
            for i in range(1, num_full_laps + 1):
                cumulative_time += pace_per_lap
                splits.append({
                    "Lap": f"Lap {i}",
                    "Distance (m)": int(i * track_dist),
                    "Cumulative Split": format_time(cumulative_time)
                })
            
            # If there's a remainder (e.g., 300m on 200m track), add the final split
            if remainder > 0:
                cumulative_time = total_pr_seconds # Precision insurance
                splits.append({
                    "Lap": "Finish",
                    "Distance (m)": int(event_distance),
                    "Cumulative Split": format_time(cumulative_time)
                })

            df = pd.DataFrame(splits)
            st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
