import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os

# Set Google API key for Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyAVG2knhuN9dqibATIidO8swr2keFvsLlY"

# Initialize session state for chat messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Streamlit app layout
st.title("Critical Infrastructure Climate Impact Advisor")

# Initialize LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        max_output_tokens=512
    )
except Exception as e:
    st.error(f"Error initializing Gemini model: {e}")
    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
    with st.chat_message("assistant"):
        st.markdown(f"Error: {e}")
    st.stop()

# Define prompt template for LLM
prompt_template = PromptTemplate(
    input_variables=["data", "query"],
    template="You are a data consultant specializing in critical infrastructure resilience. Based on this data about climate impacts on infrastructure: {data}, answer this query: {query} with concise, actionable advice."
)

# Placeholder for DataFrame
# INSERT YOUR PANDAS DATAFRAME HERE
df = pd.DataFrame([
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on roads",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on roads",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockage of drainage systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, flooding",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, flooding",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, flooding",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of the drainage system due to increase in heavy precipitation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Upgrading of the drainage system due to increase in heavy rain",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Upgrading of the drainage system due to increase in heavy rain",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Roadway flooding - road closure",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Roadway flooding - road closure",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Roadway flooding - pavement damage",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the road infrastructure caused by flash floods.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Roadway flooding - pavement damage",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the road infrastructure caused by flash floods.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Surface pavement deterioration",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased pavement maintenance due to increase in precipitation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Instability of slopes - need for slope stabilization and debris clearance",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of slopes due to increase in precipitation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Instability of slopes - road blockage from debris flow",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to increase in precipitation",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Instability of slopes - road damage from debris flow",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the road caused by increased precipitations",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Debris on the road and safety conditions",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to strong winds",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Noise barriers, panels, gantry and signals damage",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages associated to strong winds",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Vehicle instability (safety conditions)",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to strong winds",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Air surface temperature increase (High temperatures)",
        "Effect on the insfrastructure": "Surface pavement deterioration",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased pavement maintenance due to temperature increase",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Structural damage on pavements due to freeze-thaw cycles",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages associated to low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Structural damage on pavements due to freeze-thaw cycles",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to low temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Damage to drainage systems",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages associated to low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Road",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Damage to drainage systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to low temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on tracks causing blockages and obstructing train movements.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation on superstructure elements.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on tracks causing blockages and obstructing train movements.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation on superstructure elements.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow and ice accumulation on train exteriors.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintentance due to snow accumulation on trains and increased energy consumption.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on the catenary systems that may cause damage and power supply interruptions.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintentance due to snow accumulation on the catenary elements.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Snow accumulation on the catenary systems that may cause damage and power supply interruptions.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the catenary caused by snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Signal and switch malfunction.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance for ensuring system reliability due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Signal and switch malfunction.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the platform, rail track or trains due to debris or landslides. Safety conditions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to embankment failure due to changes in precipitation.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the platform, rail track or trains due to debris or landslides. Safety conditions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to embankment failure due to changes in precipitation.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the platform, rail track or trains due to debris or landslides.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by embankment failure due to changes in precipitation.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the platform, rail track or trains due to debris or landslides.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by embankment failure due to changes in precipitation.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the platform and obstruction of the track due to debris or landslides. Instability of slopes",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of slopes due to changes in precipitation.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, potentially causing flooding.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, potentially causing flooding.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rain",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, potentially causing flooding.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of the drainage system due to increased precipitation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, potentially causing flooding.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the drainage system due to increased precipitation",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Cumulated sedimentation and obstruction of the drainage system, potentially causing flooding.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the drainage system due to increased precipitation",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the track bed due to acumulated sedimentation or flooding",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to damage to the track bed",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the track bed due to acumulated sedimentation or flooding",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to damage to the track bed",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the track bed due to acumulated sedimentation or flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damage in the track bed due to acumulated sedimentation or flooding.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the track bed due to acumulated sedimentation or flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damage in the track bed due to acumulated sedimentation or flooding.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Deterioration of the rail track and platform",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance for damage to the track bed (ballast) due to changes in precipitation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages on the steel components due to corrosion.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenange of the steel elements due to changes in precipitation.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damage to the ballast due to saturation.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the ballast caused by changes in precipitation.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damage to the ballast due to saturation.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the ballast caused by changes in precipitation.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Signal and electrical system malfunction.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to signal and electrical systems malfunction due to heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Signal and electrical system malfunction.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the signal and electrical systems caused by heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Noise barriers, panels, gantry and signals damage.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to strong winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Noise barriers, panels, gantry and signals deterioration",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to strong winds.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Noise barriers, panels, gantry and signals deterioration",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by strong winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage on the raik track and platform",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive Capex due to damages on the rail track and platform associated to strong winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage on the raik track and platform",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage on the catenary elements and power lines.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive Capex due to damages on the catenary elements due to strong winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage on the catenary elements and power lines.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of the catenary elements due to high winds.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage on the catenary elements and power lines.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to power outages caused by high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Increased need for cooling",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased energy consumption due to temperature increase (stations)",
        "Proposed climate indicators": "Cooling degree days"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Deterioration of the elements in the track rails",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance on track rails due to buckling caused by high temperatures",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Degradation of ballast and track components.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to high temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Deterioration of the catenary elements due to thermal expansion",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to thermal expansion of the catenary",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Deterioration of the catenary elements due to thermal expansion",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high temperatures affecting the power lines.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Malfunction in signal equipment and electronic control systems.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high temperatures affecting the signaling and control systems.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Damages on the catenary elements due to cold",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive Capex due to lack of electrical contact between pantograph and catenary",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Deterioration of the catenary elements due to cold",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to lack of electrical contact between pantograph and catenary",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Railway",
        "Climate driver": "Changes in Temperature (Low temperatures)",
        "Effect on the insfrastructure": "Malfunction and operational shutdown due to failure of the electrical facilities due to cold",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to lack of electrical contact between pantograph and catenary",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockage of entrances and exists due to excessive snow accumulation",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation causing blockage of entrances and exits",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockage of entrances and exists due to excessive snow accumulation",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation  to avoid blockage of entrances and exits",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Overloading of tunnel's ventilation systems",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation causing the overloading of the ventilation systems.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Overloading of tunnel's ventilation systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation  to avoid the malfunction of the ventilation systems.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Damages on equipments, vehicles, or people due to slide or collapse of heavy snow buildup on the upper areas of entrances.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to snow collapse in the entrances or structures of the tunnel.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Damages on equipments, vehicles, or people due to slide or collapse of heavy snow buildup on the upper areas of entrances, that may cause the stop of operations.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to damages on the infrastructure equipments or assets due to snow collapse in the entrances/exits.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Drainage system saturation causing the interruption of the normal operation of the infrastructure in safety conditions (risk of flooding, increased humidity, creation of hazardous ice patches, etc.)",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to drainage systems saturation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Drainage system saturation causing the interruption of the normal operation of the infrastructure in safety conditions (risk of flooding, increased humidity, creation of hazardous ice patches, etc.)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation  to avoid the saturation of drainage systems.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Potential structural damage (cracks or deformations) or partial structural collapse due to additional snow loads.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to structural damages caused by additional snow loads on the infrastructure.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Potential structural damage (cracks or deformations) or partial structural collapse due to additional snow loads.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to the closure of the tunnel caused by structural damages.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Potential structural damage (cracks or deformations) or partial structural collapse due to additional snow loads.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation to avoid additional snow loads to the tunnel's structure.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Impacts on electrical and mechanical systems located at the entrances or exterior areas.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintentance due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Impacts on electrical and mechanical systems located at the entrances or exterior areas (e.g., short circuits or failures in lighting, signaling and ventilation systems).",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation on electrical and mechanical systems.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the equipments of the tunnel (e.g., electrical and mechanical equipment)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages associated to heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Damages in the equipments of the tunnel (e.g., electrical and mechanical equipment)",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to the affection of tunnel equipments by heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Drainage system saturation causing the interruption of the normal operation of the infrastructure in safety conditions (increased risk of flooding)",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to drainage systems saturation.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Drainage system saturation causing the interruption of the normal operation of the infrastructure in safety conditions (increased risk of flooding)",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to drainage systems saturation.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Drainage system saturation causing the interruption of the normal operation of the infrastructure in safety conditions (increased risk of flooding)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to heavy rains to avoid the saturation of drainage systems.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Deterioration of structural materials due to prolonged water exposure.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to heavy rains.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Structural damages in the tunnel entrances/exits if they get affected by landslides or falling debris.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages associated to heavy rains.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Structural damages in the tunnel entrances/exits if they get affected by landslides or falling debris.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to landslides/debris affecting the tunnel entrances/exits.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Ventilation systems malfuntion, creating preassure imbalances.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased energy consumption to maintain airflow balance.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Obstruction of the accesses for vehicles or trains.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Blockage of entrances and exists due to high winds that can carry debris and other materials to entrances/exits.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to high winds.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage to external structures or equipments of the tunnels.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the external structure or equipments of the tunnel due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage to external structures or equipments of the tunnels.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Afection of the power and communication lines in the tunnel.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the power and communication systems connected to the tunnel.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Afection of the power and communication lines in the tunnel.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to power and communication systems' disruption due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Expansion and deformation of structural materials of the tunnel structure.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the tunnel structure due to high temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Potential damages to the pavement or rail tracks inside the tunnel due to prolonged heat temperatures.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to high temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Potential damages to the pavement or rail tracks inside the tunnel due to prolonged heat temperatures.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the pavements or rail tracks infrastructure inside the tunnel due to high temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Potential damages to the pavement or rail tracks inside the tunnel due to prolonged heat temperatures.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the pavements or rail tracks infrastructure inside the tunnel due to high temperatures.",
        "Proposed climate indicators": "Number of consecutive days with daily maximum temperature >40\u00b0C??"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Reduce efficiency of ventilation and cooling systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased energy consumption to maintain safe temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Reduce efficiency of ventilation and cooling systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased energy consumption to maintain safe temperatures.",
        "Proposed climate indicators": "Cooling degree days"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Deterioration of tunnel equipments (e.g., electrical and mechanical equipment)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages and deterioration of tunnel's equipment.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Ice formation on tunnel floors and walls that compromise safety.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintentance due to cold temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Deterioration of tunnel equipments (e.g., electrical and mechanical equipment)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages and deterioration of tunnel's equipment.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Tunnels",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Need of additional investment on heating and defrosting systems",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased energy consumption to maintain safe temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Accumulation of snow on bridge surface, structural elements and access points.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Accumulation of snow on bridge surface, structural elements and access points.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Structural overloading due to prolonged snow accumulation.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the bridge structure caused by snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockages of the drainage systems of the bridges, potentially leading to water pooling and freezing.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to snow accumulation in the drainage systems.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockages of the drainage systems of the bridges, potentially leading to water pooling and freezing.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to snow accumulation.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Flooding of the bridge deck (roads or rail tracks).",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to flooding caused by heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Flooding of the bridge deck (roads or rail tracks).",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to flooding caused by heavy rains.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Structural stress from water flow and scour that can potentially undermine the foundations, implying risk of partial or total collapse during extreme flooding.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages on the bridge structure caused by extreme precipitations.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Water infiltration and material degradation due to continuous exposure to rainwater.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to heavy rains.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Saturation of the drainage systems of the bridges, potentially leading to water pooling.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to heavy rains.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Saturation of the drainage systems of the bridges, potentially leading to water pooling.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance to clear and upgrade the drainage systems due to heavy rains.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increase erosion near bridge foundations.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance related to erosion control due to heavy rains.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increase erosion near bridge foundations.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the bridge's foundations due to heavy rains.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Risk of fatigue and failure in structural components of the bridge.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the bridge's structure due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Risk of fatigue and failure in structural components of the bridge.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance to prevent long-term damage and need for enhanced monitoring due to high winds.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage in protective barriers, lighting and other auxiliary structures of the bridges.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages in the auxiliary structures caused by high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Damage in protective barriers, lighting and other auxiliary structures of the bridges.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of the protective and auxiliary structures due to high winds.",
        "Proposed climate indicators": "Annual mean windspeed at 10 m"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Blockage of the lanes and obstruction of routes due to windborne debris.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Temporary closures during storm winds due to safety concerns.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to high winds.",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Thermal expansion of the bridge materials.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by high temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Accelerated degradation of certain materials due to high temperatures.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to high temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Damages to expansion joints and bearings.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by high temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Damages to expansion joints and bearings.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to high temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Thermal contraction of the bridge materials.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Ice formation on bridge surfaces.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to low temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Ice formation on bridge surfaces.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Damage on the bridge due to repreated freeze-thaw cycles.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Damages to expansion joints and bearings.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to damages caused by low temperatures.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Bridges",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "Ice accumulation on auxiliary structures (reduced functionality of lighting and safety systems)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to low temperatures.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Structural Stress and Damage",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to spillway blockage causing damage to the dam structure.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Structural Stress and Damage",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to spillway blockage causing damage to the dam structure.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Spillway damage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to extreme water conditions.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Spillway damage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to extreme water conditions.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Erosion of downstream face",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to erosion",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Erosion of downstream face",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to erosion",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Blockage of spillway and intakes",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to sedimentation and reservoir capacity reduction",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Blockage of spillway and intakes",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to sedimentation and reservoir capacity reduction",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Spillway blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Increased water levels in the reservoir may cause damage to the dam",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Spillway blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Increased water levels in the reservoir may cause damage to the dam",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Damage to the dam's maintenance service road",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased maintenance due to landslide",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Damage to the dam's maintenance service road",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased maintenance due to landslide",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Damage to the operational building",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased mainenance cost due to rockflow",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Penstock blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced Power Generation due to debris accumulation",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Penstock blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced Power Generation due to debris accumulation",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Penstock blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced Power Generation due to landslide and rockfall",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme precipitation",
        "Effect on the insfrastructure": "Penstock blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced Power Generation due to landslide and rockfall",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockage of the maintaining road",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations of the road",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Blockage of the operational building",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to the blockage of the operational building",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme temperature (low)",
        "Effect on the insfrastructure": "Blockage of the maintaining road",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Delay in maintaning operations due to blockage of the road",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme temperature (low)",
        "Effect on the insfrastructure": "Blockage of the operational building",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Delay in maintaning operations due to operational building",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme temperature (low)",
        "Effect on the insfrastructure": "Penstock blockage",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced Power Generation due to landslide and rockfall",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Extreme temperature (low)",
        "Effect on the insfrastructure": "Blockage of the spillway",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to ice formation",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Reduced atmosferic humidity",
        "Effect on the insfrastructure": "Plant foliage loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced protection for landslide and erosion",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Dams",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Greater potential for erosion",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Overbank flash/fluvial flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Overbank flash/fluvial flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Lateral erosion",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Lateral erosion",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Bank collapse caused by lateral erosion",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excess bank collapses potentially leading to channel migration/shifting.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Surface erosion and internal damage to longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX in case of large structural damages to embankments and leeves.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Surface erosion and internal damage to longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX in case of large structural damages to embankments and leeves.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Failure of longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Failure of longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean temperature"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Bed erosion (scour)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excessive scour.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Damage of transversal structures (ground and low sills, ramps, weirs)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to hydraulic overloading and structural damage.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Collapse of transversal structures (ground and low sills, ramps, weirs)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Collapse of transversal structures (ground and low sills, ramps, weirs)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Deposition of coarse sediments",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excessive deposition lowering hydrualic conveyance.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Damage to concrete structures caused by abrasion of sediment-laden flows",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance for protecting concrete surfaces in contact with river flow.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Channel migration",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX if channel shifts to the edge of the river corridor causing levees undermining.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Channel migration",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX if channel shifts to the edge of the river corridor causing levees undermining.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX in the first few years after execution of soil bioengineering works when vegetation is not fully rooted yet.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Non-functionality of fish passages (ladders)",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced levels of ecosystem services.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Low water levels",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Low degree of river space utilization, due to decreasing aesthetic value and reduced user benefits, and consequently a reduced level of ecosystem services\u00a0provided\u00a0by\u00a0it",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to restoration works (planting new vegetation).",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "High water temperatures",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services of living plants.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "River training infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX after frosty periods/years to replace frost-bitten vegetation.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Overbank flash/debris flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Overbank flash/debris flooding",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Lateral erosion",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Lateral erosion",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Bank slumps caused by lateral erosion",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excess bank collapses potentially leading to channel migration/shifting.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Surface erosion and internal damage to longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX in case of large structural damages to embankments and leeves.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Failure of longitudinal structures (e.g. vegetated embankments, rip-rap, leeves)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Torrent bed erosion (scour)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excessive scour.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Damage of transversal structures (check dams, ground sills)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to hydraulic overloading and structural damage.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Collapse of transversal structures (check dams, sills)",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to hydraulic overloading and needed reconstruction works.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Deposition of coarse sediments due to debris flows",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance in case of excessive deposition lowering hydrualic conveyance.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Damage to concrete structures caused by abrasion of sediment-laden flows and debris flows",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance for protecting concrete surfaces in contact with torrential flow.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation",
        "Effect on the insfrastructure": "Torrent avulsion on fans",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX if channel shifts to the edge of the river corridor causing levees undermining.",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation (Low)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation (Low)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation (Low)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX in the first few years after execution of soil bioengineering works when vegetation is not fully rooted yet.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in precipitation (Low)",
        "Effect on the insfrastructure": "Low water levels",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Low degree of river space utilization, due to decreasing aesthetic value and reduced user benefits, and consequently a reduced level of ecosystem services\u00a0provided\u00a0by\u00a0it",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to restoration works (planting new vegetation).",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in Temperature (High temperatures)",
        "Effect on the insfrastructure": "High water temperatures",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenue loss",
        "Impact model": "Reduced benefits and reduced levels of ecosystem services of living plants.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance of soil bioengineering works (living plants).",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Torrent control infrastructure",
        "Climate driver": "Change in temperature (Low temperature)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX after frosty periods/years to replace frost-bitten vegetation.",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature < - 31\u00b0C"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables, leading to short circuits, equipment damage, and supply disruptions.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased damage in equipments due to increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables, leading to short circuits, equipment damage, and supply disruptions.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased damage in equipments due to increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables, leading to short circuits, equipment damage, and supply disruptions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations or supply disruptions due to increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables, leading to short circuits, equipment damage, and supply disruptions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations or supply disruptions due to increased frequency of intense precipitation events can cause flooding of electrical substations and underground cables",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Water infiltration and corrosion of electrical components; damage to pole foundations; increased risk of landslides affecting overhead lines.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Damage to pole foiundations and increase risk lanslides due to water infiltration and corrosion of electrical components",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Water infiltration and corrosion of electrical components; damage to pole foundations; increased risk of landslides affecting overhead lines.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Damage to pole foiundations and increase risk lanslides due to water infiltration and corrosion of electrical components",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Water infiltration and corrosion of electrical components; damage to pole foundations; increased risk of landslides affecting overhead lines.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased risk of landslides affecting overhead lines due to water infiltration and corrosion of electrical components; damage to pole foundations; ",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Water infiltration and corrosion of electrical components; damage to pole foundations; increased risk of landslides affecting overhead lines.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased risk of landslides affecting overhead lines due to water infiltration and corrosion of electrical components; damage to pole foundations; ",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Earth movements can damage underground cables, transformer stations, and pole foundations, resulting in service interruptions.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Incresed damages in underground cables, transformer stations, and pole foundations due to earth movements",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Earth movements can damage underground cables, transformer stations, and pole foundations, resulting in service interruptions.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Incresed damages in underground cables, transformer stations, and pole foundations due to earth movements",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Earth movements can damage underground cables, transformer stations, and pole foundations, resulting in service interruptions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations or service disruptons due to earth movements that can damage underground cables, transformer stations, and pole foundations",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Earth movements can damage underground cables, transformer stations, and pole foundations, resulting in service interruptions.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations or service disruptons due to earth movements that can damage underground cables, transformer stations, and pole foundations",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "In Alpine regions, thawing permafrost can cause ground subsidence and instability of pole and tower foundations, increasing the risk of collapse or misalignment.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increase damage due to  thawing permafrost that can cause ground subsidence and instability of pole and tower foundations",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "In Alpine regions, thawing permafrost can cause ground subsidence and instability of pole and tower foundations, increasing the risk of collapse or misalignment.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increase damage due to  thawing permafrost that can cause ground subsidence and instability of pole and tower foundations",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Dry soil can cause shrinkage around pole foundations, reducing their stability; lower soil moisture may affect grounding systems, leading to safety issues.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increase damage due to  thawing permafrost that can cause shrinkage around pole foundations, reducing their stability",
        "Proposed climate indicators": "Return period of 100 years of maximum daily precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in precipitation",
        "Effect on the insfrastructure": "Dry soil can cause shrinkage around pole foundations, reducing their stability; lower soil moisture may affect grounding systems, leading to safety issues.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increase damage due to  thawing permafrost that can cause shrinkage around pole foundations, reducing their stability",
        "Proposed climate indicators": "Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Strong winds and gusts can cause damage to overhead lines, poles, and transformers, leading to power outages; falling trees and branches can disrupt service.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased damage to overhead lines, poles, and transformers due to strong winds and gusts",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in wind intensity",
        "Effect on the insfrastructure": "Strong winds and gusts can cause damage to overhead lines, poles, and transformers, leading to power outages; falling trees and branches can disrupt service.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to falling trees and branches due to strong winds and gusts",
        "Proposed climate indicators": "Average number of days per year with daily mean wind speed  >=20 km/h"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Accumulation of snow or ice on power lines can lead to line breakage or sagging; freezing rain can encase equipment in ice, causing mechanical failures.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increase damages in  power lines due to accumulation of snow or ice oncan lead to line breakage or sagging",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in snow intensity",
        "Effect on the insfrastructure": "Accumulation of snow or ice on power lines can lead to line breakage or sagging; freezing rain can encase equipment in ice, causing mechanical failures.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to freezing rain can encase equipment in ice, causing mechanical failures.",
        "Proposed climate indicators": "Winter months accumulated snow"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "High temperatures can reduce the transmission capacity of cables and transformers, leading to overloads; cold temperatures can cause brittleness in materials and reduce battery performance.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased damages due to overloads because of high temperatures that can reduce the transmission capacity of cables and transformers",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Increased electricity demand for cooling can overload the distribution network; thermal expansion of conductors can lead to sagging lines and increased risk of short circuits.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations due to overaload of the distribution network because of increased electricity demand for cooling",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in temperature (High temperatures)",
        "Effect on the insfrastructure": "Increased electricity demand for cooling can overload the distribution network; thermal expansion of conductors can lead to sagging lines and increased risk of short circuits.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance due to thermal expansion of conductors that can lead to sagging lines and increased risk of short circuits.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Changes in temperature (Low temperatures)",
        "Effect on the insfrastructure": "High temperatures can reduce the transmission capacity of cables and transformers, leading to overloads; cold temperatures can cause brittleness in materials and reduce battery performance.",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase maintenance due to  brittleness in materials and reduce battery performance due to cold temperatures",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Wildfires",
        "Effect on the insfrastructure": "Fire exposure can damage poles, insulators, and transformers; smoke can cause flashovers on high-voltage insulators, leading to power outages.",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Increased damage on poles, insulators, and transformers due to fire exposure",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Energy distribution ",
        "Climate driver": "Wildfires",
        "Effect on the insfrastructure": "Fire exposure can damage poles, insulators, and transformers; smoke can cause flashovers on high-voltage insulators, leading to power outages.",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Stop of operations or  power outages due to fire smoke that can cause flashovers on high-voltage insulators",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low degree of green space utilization, due to decreasing aesthetic value and reduced user benefits, and consequently a reduced level of ecosystem services\u00a0provided\u00a0by\u00a0it",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "High temperature at soil level",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low level of use of green space due to unsuitable conditions for citizens, and consequently a low level of ecosystem services provided by it",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "High temperature at soil level",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low level of use of green space due to unsuitable conditions for citizens, and consequently a low level of ecosystem services provided by it",
        "Proposed climate indicators": "Mean temperature at ground level over threshold"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased maintenance with plants and materials.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to restoration servicies",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Cessation of plant growth",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Increase in required time to generate specific benefits",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Cessation of plant growth",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chemicals tratements due to the decrease in the natural immunity of plants.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Plant foliage loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced benefits",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Biodiversity loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low degree of use of green spaces due to their low attractiveness and consequently a low level of ecosystem services provided by them",
        "Proposed climate indicators": "Average number of days per year with daily maximum temperature >=40\u00b0C"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Biodiversity loss (including pollinators)",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chemicals tretements due to ecolgical disruption.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Depletion of water resources",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with water supplies.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Depletion of water resources",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chemical tretements due to ecolgical disruption.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Extreme heat (including heatwaves)",
        "Effect on the insfrastructure": "Intensified evapotranspiration",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with irrigation costs due to depletion in soil water resources.",
        "Proposed climate indicators": "Monthly mean temperature"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Reduced atmosferic humidity",
        "Effect on the insfrastructure": "Plant foliage loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced benefits",
        "Proposed climate indicators": "Number of days with relative humidity under 40%"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Reduced atmosferic humidity",
        "Effect on the insfrastructure": "Intensified evapotranspiration",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increased irrigation costs to compensate for reduced soil water resources due to lack of water condensation.",
        "Proposed climate indicators": "Number of days with relative humidity under 40%"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Reduced atmosferic humidity",
        "Effect on the insfrastructure": "Biodiversity disruption",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chelicals tretements due to ecolgical disruption.",
        "Proposed climate indicators": "Number of days with relative humidity under 40%"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low degree of green space utilization and consequently a reduced level of ecosystem services\u00a0provided\u00a0by\u00a0it",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Depletion of water resources",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with water supplies.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Depletion of water resources",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chemicals tretements due to the decrease in the natural immunity of plants generated by the fluctuations in the amount of physiologically necessary water.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Low water quality",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "The increasing maintenance costs of irrigation systems due to deposits (limestone, iron, algae) from the water used for irrigation",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Vegetation loss",
        "Type of impact": "Damages",
        "Consequences": "Increase CAPEX",
        "Impact model": "Reactive CAPEX due to green space restoration services by replacing dead plants ",
        "Proposed climate indicators": "SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Low precipitation",
        "Effect on the insfrastructure": "Biodiversity disruption",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chelicals tretements due to ecolgical disruption.",
        "Proposed climate indicators": "Monthly mean precipitation"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Increased solar intensity",
        "Effect on the insfrastructure": "High solar intensity at soil level",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "low level of use of green space due to unsuitable conditions for citizens, and consequently a low level of ecosystem services provided by it",
        "Proposed climate indicators": "Solar radiation intensity at plant level"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Increased solar intensity",
        "Effect on the insfrastructure": "Plant foliage loss",
        "Type of impact": "Operations",
        "Consequences": "Revenues loss",
        "Impact model": "Reduced benefits",
        "Proposed climate indicators": "Solar radiation intensity at plant level"
    },
    {
        "Infrastructure": "Green spaces",
        "Climate driver": "Increased solar intensity",
        "Effect on the insfrastructure": "Biodiversity disruption",
        "Type of impact": "Maintenance",
        "Consequences": "Increase OPEX",
        "Impact model": "Increase in maintenance costs with chemicals tretements due to the decrease in the natural immunity of plants generated by the fluctuations in the amount of physiologically necessary water.",
        "Proposed climate indicators": "Solar radiation intensity at plant level"
    }
])  # INSERT YOUR DATAFRAME HERE (e.g., df = pd.DataFrame(your_data) or df = pd.read_excel("your_file.xlsx"))

# Ensure DataFrame is provided
try:
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("No valid DataFrame provided. Please insert a pandas DataFrame.")
    data_str = df.to_string()
except Exception as e:
    st.error(f"Error with DataFrame: {e}")
    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
    with st.chat_message("assistant"):
        st.markdown(f"Error: {e}")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about climate impacts on infrastructure"):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get LLM response
    try:
        chain = prompt_template | llm
        response = chain.invoke({"data": data_str, "query": prompt})
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Append assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
    except Exception as e:
        error_msg = f"Error processing query: {e}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.markdown(error_msg)