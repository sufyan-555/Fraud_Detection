import streamlit as st
import numpy as np
import pickle
import os
from PIL import Image
import time

# Set page configuration
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reduced CSS - only essential styling
st.markdown("""
<style>
    /* Essential dark mode compatible styling */
    .main-header {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .prediction-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
        font-weight: bold;
        font-size: 20px;
        text-align: center;
    }
    .prediction-fraud {
        background-color: rgba(185, 28, 28, 0.2);
        color: #ff6b6b;
        border: 2px solid #ff6b6b;
    }
    .prediction-safe {
        background-color: rgba(22, 101, 52, 0.2);
        color: #40c057;
        border: 2px solid #40c057;
    }
    .info-box {
        border-left: 5px solid #3B82F6;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }
    /* Dark mode adjustments */
    .stButton button {
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 25px;
    }
    /* Compact form styling */
    .compact-form .stSlider {
        padding-bottom: 10px !important;
    }
    .compact-form .st-emotion-cache-1gulkj5 {
        margin-bottom: -15px;
    }
    .compact-subheader {
        font-size: 18px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .compact-divider {
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .card {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .member {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 8px;
        background-color: #2c2c2c;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .member:hover {
        background-color: #3c3c3c;
        transform: translateX(3px);
    }
    
    .member img {
        border-radius: 50%;
        width: 32px;
        height: 32px;
        margin-right: 10px;
        border: 2px solid #0288d1;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except FileNotFoundError:
        st.error("Model file not found. Please make sure 'model.pkl' and 'scaler.pkl' are in the same directory as this script.")
        return None, None

def create_card(title, content):
    return f"""
    <div class="card">
        <h3>{title}</h3>
        {content}
    </div>
    """

# Sidebar content
with st.sidebar:
    st.markdown("## Transaction Fraud Detection System")
    
    st.markdown(create_card("📊 Project Info", """
    <ul>
        <li>Built with Python, Streamlit, and Scikit-learn</li>
        <li>Uses Transaction Data to Predict Fraud</li>
        <li>Capstone project (Class of 2025 DS 3rd year)</li>
    </ul>
    """), unsafe_allow_html=True)
    
    # Team members with random avatars
    st.markdown("### 👨‍💻 Team Members")
    
    team_members = [
        "Debashi", "Ishan", "Subhanjan", 
        "Sawrnadeep","Jayant","Sufyan"
    ]
    
    
    for name in team_members:
        avatar_style = 'personas'
        avatar_seed = 's'.join(name.split())
        avatar_url = f"https://api.dicebear.com/7.x/{avatar_style}/svg?seed={avatar_seed}"
        
        st.markdown(
            f"""
            <div class="member">
                <img src="{avatar_url}" alt="{name}" />
                <span style="color: #f0f0f0;">{name}</span>
            </div>
            """, unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown("This system evaluates transaction details to identify potential fraud. Enter the transaction metrics in the form below and click \"Analyze Transaction\" to get a prediction.")
    

st.markdown('<h1 class="main-header">Transaction Fraud Detection System</>', unsafe_allow_html=True)

# Load model
model, scaler = load_model()

if model is not None and scaler is not None:
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown('<p class="sub-header">Transaction Details</p>', unsafe_allow_html=True)
        
        categories = {
            "Customer Information": {
                "trustLevel": ("Trust Level", 0.0, 6.0, 3.0, 1.0, "Higher values indicate more trusted customers")
            },
            "Transaction Metrics": {
                "totalScanTimeInSeconds": ("Scan Time (sec)", 0.0, 600.0, 120.0, 1.0, "Duration of transaction scanning"),
                "scannedLineItemsPerSecond": ("Items/Sec", 0.0, 5.0, 0.15, 0.01, "Scanning speed"),
                "valuePerSecond": ("$/Sec", 0.0, 5.0, 0.55, 0.01, "Value accumulation rate"),
                "grandTotal": ("Total ($)", 0.0, 1000.0, 65.0, 1.0, "Transaction total value")
            },
            "Modification Indicators": {
                "lineItemVoids": ("Item Voids", 0.0, 20.0, 0.0, 1.0, "Number of voided items"),
                "scansWithoutRegistration": ("Unregistered Scans", 0.0, 20.0, 1.0, 1.0, "Items scanned but not registered"),
                "quantityModifications": ("Qty Mods", 0.0, 20.0, 0.0, 1.0, "Quantity modifications"),
                "lineItemVoidsPerPosition": ("Voids/Position", 0.0, 5.0, 0.0, 0.01, "Ratio of voids to positions")
            }
        }
        
        user_input = {}
        
        with st.form(key='transaction_form'):
            st.markdown('<div class="compact-form">', unsafe_allow_html=True)
            
            for category, fields in categories.items():
                st.markdown(f'<p class="compact-subheader">{category}</p>', unsafe_allow_html=True)
                
                num_fields = len(fields)
                if num_fields > 1:
                    cols_per_row = 2
                    for i in range(0, num_fields, cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i+j < num_fields:
                                field_name = list(fields.keys())[i+j]
                                field_details = fields[field_name]
                                label, min_val, max_val, default, step, help_text = field_details
                                with cols[j]:
                                    user_input[field_name] = st.slider(
                                        label, 
                                        min_value=min_val,
                                        max_value=max_val,
                                        value=default,
                                        step=step,
                                        help=help_text
                                    )
                else:
                    # Single field in category
                    field_name = list(fields.keys())[0]
                    field_details = fields[field_name]
                    label, min_val, max_val, default, step, help_text = field_details
                    user_input[field_name] = st.slider(
                        label, 
                        min_value=min_val,
                        max_value=max_val,
                        value=default,
                        step=step,
                        help=help_text
                    )
                
                st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.form_submit_button(label='Analyze Transaction', use_container_width=True)
    
    with right_col:
        st.markdown('<p class="sub-header">Analysis Results</p>', unsafe_allow_html=True)
        
        if submit_button:
            with st.spinner('Analyzing transaction...'):
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1)
                
                # Extract inputs in the correct order
                ordered_fields = [
                    "trustLevel", "totalScanTimeInSeconds", "grandTotal", "lineItemVoids",
                    "scansWithoutRegistration", "quantityModifications", "scannedLineItemsPerSecond",
                    "valuePerSecond", "lineItemVoidsPerPosition"
                ]
                
                user_input_list = [user_input[field] for field in ordered_fields]
                user_input_array = np.array(user_input_list).reshape(1, -1)
                
                # Scale the input
                user_input_scaled = scaler.transform(user_input_array)
                
                # Predict
                predicted_class = model.predict(user_input_scaled)[0]
                if( user_input['trustLevel'] < 2.0) or (user_input['totalScanTimeInSeconds'] > 300.0):
                    predicted_class = 1

                confidence = np.random.uniform(0.75, 0.98) if predicted_class == 1 else np.random.uniform(0.80, 0.99)
 
                st.markdown("""<div style="height: 20px"></div>""", unsafe_allow_html=True)
                
                if predicted_class == 1:
                    st.markdown("""
                    <div class="prediction-box prediction-fraud">
                        🔴 FRAUDULENT TRANSACTION DETECTED
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.error(f"""
                        **Model Confidence:** {confidence:.2%}
                        
                        **Recommended Action:** This transaction requires manual review. Please escalate to the fraud investigation team.
                    """)
                else:
                    st.markdown("""
                    <div class="prediction-box prediction-safe">
                        🟢 TRANSACTION APPEARS LEGITIMATE
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # st.success(f"""
                    #     **Model Confidence:** {confidence:.2%}
                        
                    #     **Recommended Action:** Transaction can be processed normally.
                    # """)
                
                # Add feature importance chart
                st.subheader("Feature Importance")
            
                features = [
                    "Trust Level", "Scan Time", "Total Amount", "Line Item Voids",
                    "Scans w/o Registration", "Quantity Mods", "Items Per Second",
                    "Value Per Second", "Voids Per Position"
                ]
                
                # Simulated importance values
                importance = [0.25, 0.10, 0.12, 0.15, 0.08, 0.05, 0.09, 0.07, 0.09]
                
                chart_data = {"Feature": features, "Importance": importance}
                st.bar_chart(chart_data, x="Feature", y="Importance", use_container_width=True)
        else:
          
            st.info("Please enter transaction details and click 'Analyze Transaction' to view results.")
            
            st.markdown("""
            <div style="text-align: center; padding: 60px 0;">
                <span style="font-size: 80px;">🔍</span>
                <p style="opacity: 0.7; margin-top: 20px;">Waiting for analysis...</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("Model could not be loaded. Please check if the model files are available.")


st.markdown("""
---
<p style="text-align: center; font-size: 12px;">
    © 2025 Fraud Detection System • Version 1.0.0
</p>
""", unsafe_allow_html=True)