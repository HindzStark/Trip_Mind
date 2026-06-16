import streamlit as st
import httpx
import time
import datetime

# Configure page settings
st.set_page_config(
    page_title="TripMind AI - Plan Your Perfect Trip",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Centralized API settings
API_BASE_URL = "http://localhost:8000"

# Inject Custom Google Fonts, Material Icons, and harmonious Slate/Teal CSS styling
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
<style>
    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f7f9fb;
        color: #191c1e;
    }
    
    /* Center Layout Elements */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Primary and Accent Headers */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
    }

    /* Custom Glass Cards */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
    }
    .glass-card-subtle {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Interactive Elements Hover/Active */
    .stButton>button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #0d9488 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2) !important;
    }
    
    /* Google OAuth Button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        background-color: #ffffff;
        color: #1f2937;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.2s;
        margin-bottom: 16px;
    }
    .google-btn:hover {
        background-color: #f9fafb;
    }
    .google-logo {
        width: 18px;
        height: 18px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "current_trip_id" not in st.session_state:
    st.session_state.current_trip_id = None
if "page" not in st.session_state:
    st.session_state.page = "auth"

# Helper to verify token and return headers
def get_auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ----------------- AUTH PAGE -----------------
def render_auth_page():
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h1 style='font-size: 40px;'>TripMind AI</h1><p style='color: #45464d; font-size: 18px;'>Plan your perfect trip in seconds using multi-agent intelligence</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
        
        with tab_login:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # Google OAuth Simulator (Uses real POST /auth/google endpoint with a simulated valid OIDC token)
            if st.button("Continue with Google", key="google_login"):
                with st.spinner("Logging in with Google..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/auth/google",
                            json={"id_token": "simulated_google_oauth_token"}
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_email = "google_user@example.com"
                            st.session_state.user_name = "Google User"
                            st.session_state.page = "dashboard"
                            st.success("Successfully logged in with Google!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Google login failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Server connection failed: {e}")
            
            st.markdown("<div style='text-align: center; margin: 1rem 0; color: #76777d;'>or sign in with email</div>", unsafe_allow_html=True)
            
            login_email = st.text_input("Email Address", key="login_email_input")
            login_password = st.text_input("Password", type="password", key="login_pass_input")
            
            if st.button("Sign In", key="email_login_btn", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Signing in..."):
                        try:
                            resp = httpx.post(
                                f"{API_BASE_URL}/auth/login",
                                data={"username": login_email, "password": login_password}
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.token = data["access_token"]
                                st.session_state.user_email = login_email
                                st.session_state.page = "dashboard"
                                st.success("Login successful!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
                        except Exception as e:
                            st.error(f"Could not connect to backend server: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with tab_signup:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            signup_name = st.text_input("Full Name", key="signup_name_input")
            signup_email = st.text_input("Email Address", key="signup_email_input")
            signup_password = st.text_input("Password", type="password", key="signup_pass_input")
            
            if st.button("Create Account", key="email_signup_btn", use_container_width=True):
                if not signup_name or not signup_email or not signup_password:
                    st.error("All fields are required.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            resp = httpx.post(
                                f"{API_BASE_URL}/auth/register",
                                json={
                                    "email": signup_email,
                                    "full_name": signup_name,
                                    "password": signup_password
                                }
                            )
                            if resp.status_code == 201:
                                st.success("Account created successfully! Please log in.")
                            else:
                                st.error(resp.json().get("detail", "Registration failed."))
                        except Exception as e:
                            st.error(f"Could not connect to backend server: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------- MAIN APP HEADER -----------------
def render_app_header():
    col_logo, col_nav, col_profile = st.columns([1, 2, 1])
    with col_logo:
        st.markdown("<h2 style='margin: 0; padding-top: 10px; color: #0f172a;'>TripMind AI</h2>", unsafe_allow_html=True)
    with col_nav:
        pass
    with col_profile:
        col_name, col_logout = st.columns([2, 1])
        with col_name:
            st.markdown(f"<p style='margin: 0; padding-top: 15px; text-align: right; font-weight: 500;'>{st.session_state.user_email}</p>", unsafe_allow_html=True)
        with col_logout:
            if st.button("Sign Out", key="logout_btn"):
                st.session_state.token = None
                st.session_state.user_email = None
                st.session_state.user_name = None
                st.session_state.current_trip_id = None
                st.session_state.page = "auth"
                st.rerun()
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# ----------------- PLAN FORM VIEW -----------------
def render_new_plan_view():
    st.markdown("<h3>Plan a New Adventure</h3>", unsafe_allow_html=True)
    
    form_col1, form_col2 = st.columns([1, 1.2])
    
    with form_col1:
        st.image(
            "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=800&q=80",
            caption="Where would you like to go?",
            use_container_width=True
        )
        st.markdown("""
        <div class="glass-card-subtle">
            <span class="material-symbols-outlined" style="vertical-align: middle; color: #0d9488; margin-right: 5px;">info</span>
            <strong>Multi-Agent Intelligence</strong>
            <p style="font-size: 13px; color: #45464d; margin: 5px 0 0 0;">
                TripMind spins up 7 specialized autonomous agents: Planner, Weather, Flight, Hotel, Attraction, Budget, and Itinerary to build your personalized plan.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with form_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        col_city1, col_city2 = st.columns(2)
        with col_city1:
            source_city = st.text_input("Departure City", placeholder="e.g. Delhi", value="Delhi")
        with col_city2:
            destination_city = st.text_input("Destination City", placeholder="e.g. Rome", value="Rome")
            
        col_days, col_date = st.columns(2)
        with col_days:
            trip_days = st.number_input("Duration (Days)", min_value=1, max_value=30, value=5)
        with col_date:
            start_date = st.date_input("Start Date", value=datetime.date.today() + datetime.timedelta(days=30))
            
        col_budget, col_travel = st.columns([1.5, 1])
        with col_budget:
            budget = st.number_input("Total Budget (INR)", min_value=1000, value=250000, step=5000)
        with col_travel:
            travel_included = st.checkbox("Include Travel Days", value=True, help="Set to True if departure/arrival days consume part of your trip.")
            
        col_adults, col_kids = st.columns(2)
        with col_adults:
            adults = st.number_input("Adults", min_value=1, value=2)
        with col_kids:
            children = st.number_input("Children", min_value=0, value=1)
            
        interests_list = [
            "Culture", "Food", "Nature", "Adventure", "Temples", "Shopping", 
            "Nightlife", "Family", "Photography", "History", "Architecture", "Relaxation"
        ]
        selected_interests = st.multiselect("Travel Interests (Select up to 5)", interests_list, default=["History", "Food", "Nature"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate AI Plan 🪄", key="generate_plan_btn", use_container_width=True):
            if not source_city or not destination_city:
                st.error("Please provide both departure and destination cities.")
            elif len(selected_interests) > 5:
                st.error("Please select a maximum of 5 interests.")
            else:
                payload = {
                    "source_city": source_city,
                    "destination_city": destination_city,
                    "trip_days": trip_days,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "travel_included": travel_included,
                    "budget": budget,
                    "adults": adults,
                    "children": children,
                    "interests": ", ".join(selected_interests)
                }
                
                with st.spinner("Registering trip parameters..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/trips/",
                            json=payload,
                            headers=get_auth_headers()
                        )
                        if resp.status_code == 201:
                            trip_data = resp.json()
                            st.session_state.current_trip_id = trip_data["id"]
                            st.session_state.page = "loading"
                            st.rerun()
                        else:
                            st.error(f"Trip creation failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Could not connect to backend server: {e}")
                        
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- WORKFLOW LOADING PAGE -----------------
def render_loading_page():
    st.markdown("<div style='text-align: center; margin-top: 3rem;'><h1 style='color: #0d9488;'>TripMind AI is crafting your perfect journey...</h1><p style='color: #45464d;'>Our multi-agent graph is executing and fetching real live details.</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        work_log_title = st.markdown("<h4 style='margin-top: 20px; font-size: 14px; text-transform: uppercase; color: #76777d; letter-spacing: 0.1em;'>Multi-Agent Progress Logs</h4>", unsafe_allow_html=True)
        log_placeholder = st.empty()
        
        agent_steps = [
            ("Initializing Agent Graph Workflow", "Understanding trip parameters"),
            ("Planner Agent", "Normalizing locations and validating realistic place/budget constraints"),
            ("Weather Agent", "Querying OpenWeather for historical and real-time forecast data"),
            ("Flight Agent", "Searching Aviationstack for outbound and return airline listings"),
            ("Hotel Agent", "Scraping Geoapify Places for local hotels, hostels, and lodgings"),
            ("Attraction Agent", "Fetching sightseeing spots and check child-friendly parameters"),
            ("Budget Agent", "Compiling itemized balance estimates and generating savings options"),
            ("Itinerary Agent", "Synthesizing schedule timelines and creating your packing list")
        ]
        
        # Poll DB status in a loop
        max_polls = 20
        poll_count = 0
        success = False
        
        while poll_count < max_polls:
            try:
                resp = httpx.get(
                    f"{API_BASE_URL}/trips/{st.session_state.current_trip_id}",
                    headers=get_auth_headers()
                )
                if resp.status_code == 200:
                    trip_data = resp.json()
                    status = trip_data["status"]
                    
                    # Estimate UI progress logs based on polling attempts and actual state
                    current_idx = min(poll_count, len(agent_steps) - 1)
                    if status == "completed":
                        progress_bar.progress(100)
                        status_text.markdown("<strong style='color: #0d9488;'>✓ Journey compilation completed!</strong>", unsafe_allow_html=True)
                        success = True
                        break
                    elif status == "failed":
                        progress_bar.progress(0)
                        status_text.markdown("<strong style='color: #ba1a1a;'>❌ Agent planning execution failed.</strong>", unsafe_allow_html=True)
                        break
                    else:
                        step_val = int(((current_idx + 1) / len(agent_steps)) * 90)
                        progress_bar.progress(step_val)
                        status_text.markdown(f"Running: <em>{agent_steps[current_idx][0]}</em>", unsafe_allow_html=True)
                        
                        # Render cumulative logs
                        log_html = "<ul style='list-style-type: none; padding-left: 0; font-size: 14px; line-height: 1.8;'>"
                        for i in range(current_idx + 1):
                            log_html += f"<li style='color: #0d9488;'>✓ {agent_steps[i][1]}</li>"
                        log_html += "</ul>"
                        log_placeholder.markdown(log_html, unsafe_allow_html=True)
                        
                else:
                    st.error(f"Failed to fetch status: {resp.text}")
                    break
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")
                break
                
            time.sleep(5)
            poll_count += 1
            
        if success:
            st.success("Plan generated successfully! Redirecting...")
            time.sleep(2)
            st.session_state.page = "itinerary"
            st.rerun()
        else:
            if st.button("Return to Dashboard", key="return_dash_failed_btn"):
                st.session_state.page = "dashboard"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- ITINERARY VIEW PAGE -----------------
def render_itinerary_page():
    # Fetch details of current trip
    try:
        resp = httpx.get(
            f"{API_BASE_URL}/trips/{st.session_state.current_trip_id}",
            headers=get_auth_headers()
        )
        if resp.status_code != 200:
            st.error(f"Could not load trip: {resp.text}")
            if st.button("Return to Dashboard", key="ret_dash_err_btn"):
                st.session_state.page = "dashboard"
                st.rerun()
            return
        trip = resp.json()
    except Exception as e:
        st.error(f"Error connecting to server: {e}")
        return

    # Back to Dashboard button
    if st.button("← Back to Dashboard", key="back_to_dashboard_btn"):
        st.session_state.page = "dashboard"
        st.rerun()
        
    # Destination Header Title
    st.markdown(f"""
    <div class="glass-card" style="position: relative; overflow: hidden; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 30px; border-radius: 16px;">
        <h1 style="color: #ffffff !important; margin: 0; font-size: 36px;">{trip['destination_city']} Explorer</h1>
        <p style="color: #94a3b8; font-size: 16px; margin: 8px 0 0 0;">
            Departure: {trip['source_city']} • Duration: {trip['trip_days']} Days • Start Date: {trip['start_date']} • Travelers: {trip['adults']} Adults, {trip['children']} Children
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vibe Summary Paragraph
    itinerary_data = trip.get("itinerary") or {}
    if itinerary_data.get("summary"):
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #0d9488;">
            <strong>AI Vibe Summary:</strong>
            <p style="font-size: 15px; color: #45464d; margin: 8px 0 0 0; line-height: 1.6;">
                {itinerary_data['summary']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Bento Columns Layout
    col_left, col_right = st.columns([1, 1.8])
    
    with col_left:
        # Flights Card
        st.markdown("<h4>✈️ Flight Options</h4>", unsafe_allow_html=True)
        flights_data = trip.get("flights") or {}
        if flights_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            for idx, flight in enumerate(flights_data.get("flight_options", [])):
                st.markdown(f"""
                <div class="glass-card-subtle">
                    <div style="display: flex; justify-content: space-between; font-weight: 600;">
                        <span>{flight.get('airline', 'Flight Option')}</span>
                        <span style="color: #0d9488;">{flight.get('total_price_inr', 0):,} INR</span>
                    </div>
                    <p style="font-size: 13px; color: #76777d; margin: 5px 0 0 0;">
                        Flight: {flight.get('flight_number', 'N/A')} • Departs: {flight.get('departure_time', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No flights data found.")
            
        # Weather Card
        st.markdown("<h4>🌤️ Weather Forecast</h4>", unsafe_allow_html=True)
        weather_data = trip.get("weather") or {}
        if weather_data:
            st.markdown(f"""
            <div class="glass-card">
                <p><strong>Current Weather:</strong> {weather_data.get('current_weather', 'N/A')} ({weather_data.get('current_temp', 'N/A')})</p>
                <p><strong>Estimated Trip Weather:</strong> {weather_data.get('estimated_weather', 'N/A')}</p>
                <p><strong>Estimated Temp Range:</strong> {weather_data.get('estimated_temp', 'N/A')}</p>
                <div class="glass-card-subtle" style="margin-top: 10px;">
                    <span style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: #76777d;">Best Time to Visit:</span>
                    <p style="font-size: 13px; margin: 3px 0 0 0;">{weather_data.get('best_weather', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No weather data found.")
            
        # Packing List Card
        st.markdown("<h4>📋 Weather-Based Packing List</h4>", unsafe_allow_html=True)
        if itinerary_data.get("packing_list"):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            for item in itinerary_data["packing_list"]:
                st.checkbox(item, key=f"pack_{item}_{trip['id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No packing list found.")
            
    with col_right:
        # Hotel Cards
        st.markdown("<h4>🏨 Accommodation Options</h4>", unsafe_allow_html=True)
        hotels_data = trip.get("hotels") or []
        if hotels_data:
            st.markdown('<div class="glass-card" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px;">', unsafe_allow_html=True)
            for hotel in hotels_data:
                tier_color = "#0d9488" if hotel.get("tier") == "premium" else ("#3b82f6" if hotel.get("tier") == "mid-range" else "#76777d")
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <strong style="font-size: 15px; color: #0f172a;">{hotel.get('hotel_name')}</strong>
                            <span style="font-size: 10px; font-weight: 600; text-transform: uppercase; background-color: {tier_color}15; color: {tier_color}; padding: 2px 6px; border-radius: 4px;">{hotel.get('tier')}</span>
                        </div>
                        <p style="font-size: 12px; color: #76777d; margin: 4px 0 0 0;">📍 {hotel.get('neighborhood')}</p>
                        <p style="font-size: 13px; color: #45464d; margin: 8px 0 0 0; line-height: 1.4;">{hotel.get('description')}</p>
                    </div>
                    <div style="margin-top: 15px; border-top: 1px solid #e2e8f0; padding-top: 10px; display: flex; justify-content: space-between; align-items: end;">
                        <span style="font-size: 11px; color: #76777d;">{hotel.get('nightly_rate_inr', 0):,} INR/night</span>
                        <strong style="color: #0f172a; font-size: 15px;">{hotel.get('total_cost_inr', 0):,} INR</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No hotels data found.")
            
        # Budget Analysis Card
        st.markdown("<h4>📊 Budget Analysis</h4>", unsafe_allow_html=True)
        budget_data = trip.get("budget_breakdown") or {}
        if budget_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # Gauge progress bar
            limit = trip["budget"]
            est_total = budget_data.get("total_estimated_cost_inr", 0)
            is_over = budget_data.get("is_over_budget", False)
            pct = min(int((est_total / limit) * 100), 100)
            
            status_lbl = "OVER BUDGET" if is_over else "ON TRACK"
            status_color = "#ba1a1a" if is_over else "#0d9488"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 15px; color: #45464d;">Estimated Cost: <strong>{est_total:,} INR</strong> / {limit:,} INR</span>
                <span style="font-size: 11px; font-weight: 600; background-color: {status_color}15; color: {status_color}; padding: 4px 8px; border-radius: 4px;">{status_lbl}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct)
            
            # Expenses Categories list
            st.markdown("<div style='margin-top: 20px; font-weight: 600; font-size: 14px;'>Itemized Expenses</div>", unsafe_allow_html=True)
            for exp in budget_data.get("itemized_expenses", []):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid #f1f5f9;">
                    <span><strong>{exp.get('category')}</strong> <span style="font-size:11px; color:#76777d;">({exp.get('details')})</span></span>
                    <span>{exp.get('cost_inr', 0):,} INR</span>
                </div>
                """, unsafe_allow_html=True)
                
            # Savings suggestions
            suggestions = budget_data.get("savings_suggestions", [])
            if suggestions:
                st.markdown("<div style='margin-top: 20px; font-weight: 600; font-size: 14px; color: #0d9488;'>AI Savings Recommendations</div>", unsafe_allow_html=True)
                for s in suggestions:
                    st.markdown(f"""
                    <div style="background-color: #0d948808; border: 1px solid #0d948820; border-radius: 8px; padding: 8px 12px; margin-top: 8px; font-size: 13px; line-height: 1.4;">
                        💡 {s}
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No budget analysis details found.")

    # Day-by-Day Itinerary List
    st.markdown("<h4>📅 Proposed Day-by-Day Itinerary</h4>", unsafe_allow_html=True)
    if itinerary_data.get("days"):
        for day in itinerary_data["days"]:
            with st.expander(f"Day {day.get('day')} — {day.get('date')} ({day.get('hotel', 'Hotel Stays')})", expanded=True):
                # Summary details of the day
                st.markdown(f"<p style='font-size: 14px; color: #76777d;'>🍽️ <strong>Meals planned:</strong> {day.get('meals', 'N/A')}</p>", unsafe_allow_html=True)
                if day.get("notes"):
                    st.markdown(f"<p style='font-size: 13px; color: #45464d; background-color: #f8fafc; padding: 8px 12px; border-radius: 6px;'>📝 <em>Note: {day.get('notes')}</em></p>", unsafe_allow_html=True)
                
                # Daily activity slots
                st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-top: 10px;'>", unsafe_allow_html=True)
                for act in day.get("activities", []):
                    # Check if activity is child-friendly if children is configured
                    child_badge = ""
                    if trip["children"] > 0 and act.get("child_friendly", True):
                        child_badge = "<span style='font-size: 9px; font-weight: 600; text-transform: uppercase; background-color: #0d948815; color: #0d9488; padding: 2px 5px; border-radius: 3px; margin-left: 5px;'>Child Friendly</span>"
                        
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <span style="font-size: 10px; font-weight: 600; text-transform: uppercase; color: #76777d; tracking-wider: 0.05em;">{act.get('time_of_day')}</span>
                            <div style="margin-top: 3px; display: flex; align-items: center;">
                                <strong style="font-size: 14px; color: #0f172a;">{act.get('name')}</strong>
                                {child_badge}
                            </div>
                            <p style="font-size: 12px; color: #45464d; margin: 6px 0 0 0; line-height: 1.4;">{act.get('description')}</p>
                        </div>
                        <div style="margin-top: 10px; border-top: 1px dashed #f1f5f9; padding-top: 8px; display: flex; justify-content: space-between; font-size: 11px; color: #76777d;">
                            <span>Fee: {act.get('cost_inr', 0):,} INR</span>
                            <span>Duration: {act.get('duration_minutes', 0)} mins</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No day itinerary plan found.")

# ----------------- DASHBOARD / TRIP LIST VIEW -----------------
def render_dashboard_page():
    render_app_header()
    
    # Load all trips for this user
    try:
        resp = httpx.get(
            f"{API_BASE_URL}/trips/",
            headers=get_auth_headers()
        )
        trips = resp.json() if resp.status_code == 200 else []
    except Exception:
        trips = []
        
    tab_new, tab_list = st.tabs(["Create New Plan", "My Saved Trips"])
    
    with tab_new:
        render_new_plan_view()
        
    with tab_list:
        st.markdown("<h3>My Trips</h3>", unsafe_allow_html=True)
        if not trips:
            st.info("You haven't planned any trips yet! Use the 'Create New Plan' tab to get started.")
        else:
            # Display list of trips in a beautiful tabular grid
            for trip in trips:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                col_name, col_meta, col_status, col_action = st.columns([1.5, 2, 1, 1])
                
                with col_name:
                    st.markdown(f"<h4>📍 {trip['destination_city']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #76777d; font-size: 13px;'>From {trip['source_city']}</span>", unsafe_allow_html=True)
                with col_meta:
                    st.markdown(f"<p style='margin: 0; padding-top: 5px;'><strong>Dates:</strong> {trip['start_date']} ({trip['trip_days']} Days)</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 0; color: #45464d;'><strong>Budget:</strong> {trip['budget']:,} INR</p>", unsafe_allow_html=True)
                with col_status:
                    stat = trip['status']
                    color = "#0d9488" if stat == "completed" else ("#ff9f1c" if stat == "processing" else "#ba1a1a")
                    st.markdown(f"<span style='font-size: 11px; font-weight: 600; text-transform: uppercase; background-color: {color}15; color: {color}; padding: 4px 10px; border-radius: 4px;'>{stat}</span>", unsafe_allow_html=True)
                with col_action:
                    if stat == "completed":
                        if st.button("View Plan 🗺️", key=f"view_{trip['id']}", use_container_width=True):
                            st.session_state.current_trip_id = trip["id"]
                            st.session_state.page = "itinerary"
                            st.rerun()
                    elif stat == "processing":
                        if st.button("Resume ⏱️", key=f"view_{trip['id']}", use_container_width=True):
                            st.session_state.current_trip_id = trip["id"]
                            st.session_state.page = "loading"
                            st.rerun()
                    else:
                        st.markdown("<p style='font-size: 12px; color: #ba1a1a;'>Failed. Try creating again.</p>", unsafe_allow_html=True)
                        
                st.markdown('</div>', unsafe_allow_html=True)

# ----------------- MAIN APP CONTROLLER -----------------
def main():
    if st.session_state.page == "auth" and not st.session_state.token:
        render_auth_page()
    elif st.session_state.page == "loading":
        render_loading_page()
    elif st.session_state.page == "itinerary":
        render_itinerary_page()
    else:
        render_dashboard_page()

if __name__ == "__main__":
    main()
