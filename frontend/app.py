import streamlit as st
import httpx
import time
import datetime

# Configure page settings
st.set_page_config(
    page_title="TripMind AI — Plan Your Perfect Trip",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API base URL
API_BASE_URL = "http://localhost:8000"

# Styling improvements using native styling & minimal custom CSS for clean aesthetics
st.markdown("""
<style>
    /* Clean, modern typography & card layouts */
    .reportview-container {
        background-color: #fafbfc;
    }
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    .custom-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .custom-sub-card {
        background-color: #f8fafc;
        border: 1px solid #edf2f7;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .tag {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        background-color: #e6fffa;
        color: #0d9488;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .tag-blue {
        background-color: #ebf8ff;
        color: #2b6cb0;
    }
    .tag-red {
        background-color: #fff5f5;
        color: #c53030;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "current_trip_id" not in st.session_state:
    st.session_state.current_trip_id = None
if "page" not in st.session_state:
    st.session_state.page = "auth"

# Authorization helper
def get_auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ----------------- AUTH PAGE -----------------
def render_auth_page():
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h1>✈️ TripMind AI</h1><p style='color: #4a5568;'>Your intelligent multi-agent travel planner</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
        
        with tab_login:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            
            # Simulated Google login
            if st.button("Continue with Google", key="google_login", use_container_width=True):
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
                            st.session_state.page = "dashboard"
                            st.success("Successfully logged in with Google!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Google login failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Server connection failed: {e}")
            
            st.markdown("<div style='text-align: center; margin: 1rem 0; color: #a0aec0;'>or</div>", unsafe_allow_html=True)
            
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
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_signup:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- SIDEBAR PROFILE & NAV -----------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### ✈️ TripMind AI")
        st.markdown(f"Signed in as:\n`{st.session_state.user_email}`")
        st.markdown("---")
        
        if st.button("New Trip Form", key="nav_new_trip", use_container_width=True):
            st.session_state.current_trip_id = None
            st.session_state.page = "dashboard"
            st.rerun()
            
        if st.button("Logout", key="nav_logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.current_trip_id = None
            st.session_state.page = "auth"
            st.rerun()

# ----------------- PLAN FORM VIEW -----------------
def render_new_plan_view():
    st.markdown("## 🧭 Plan a New Adventure")
    
    col_form, col_info = st.columns([1.5, 1])
    
    with col_form:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
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
            travel_included = st.checkbox("Include Travel Days", value=True, help="Includes flight transit days in itinerary calculation.")
            
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
        if st.button("Generate AI Itinerary 🪄", key="generate_plan_btn", use_container_width=True):
            if not source_city or not destination_city:
                st.error("Please provide departure and destination cities.")
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
                        st.error(f"Server connection failed: {e}")
                        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_info:
        st.markdown("""
        <div class='custom-card'>
            <h3>🧠 TripMind Autonomous Agents</h3>
            <p>Once you click generate, TripMind deploys 7 cooperating AI agents in the background:</p>
            <ul>
                <li><strong>Planner Agent</strong> normalizes details and checks feasibility.</li>
                <li><strong>Weather Agent</strong> pulls historical and forecast forecasts.</li>
                <li><strong>Flight Agent</strong> estimates real routes and prices.</li>
                <li><strong>Hotel Agent</strong> lists accommodation options.</li>
                <li><strong>Attraction Agent</strong> discovers matching sightseeing spots.</li>
                <li><strong>Budget Agent</strong> verifies cost categories.</li>
                <li><strong>Itinerary Agent</strong> creates a day-by-day travel map.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ----------------- WORKFLOW LOADING PAGE -----------------
def render_loading_page():
    render_sidebar()
    
    st.markdown("<div style='text-align: center; margin-top: 2rem;'><h2>🧭 TripMind AI is planning your journey...</h2><p style='color: #4a5568;'>Our 7 autonomous agents are fetching and analyzing live details.</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        st.markdown("<p style='font-size: 13px; font-weight: 600; text-transform: uppercase; color: #718096; margin-top: 15px;'>Execution log</p>", unsafe_allow_html=True)
        log_placeholder = st.empty()
        
        agent_steps = [
            ("Initializing Agent Graph Workflow", "Understanding trip parameters"),
            ("Planner Agent", "Normalizing locations and validating realistic place/budget constraints"),
            ("Weather Agent", "Querying OpenWeather for historical and real-time forecast data"),
            ("Flight Agent", "Searching Aviationstack for outbound and return airline listings"),
            ("Hotel Agent", "Scraping Geoapify Places for local hotels, hostels, and lodgings"),
            ("Attraction Agent", "Fetching sightseeing spots and checking child-friendly parameters"),
            ("Budget Agent", "Compiling itemized balance estimates and generating savings options"),
            ("Itinerary Agent", "Synthesizing schedule timelines and creating your packing list")
        ]
        
        max_polls = 30
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
                    
                    current_idx = min(poll_count, len(agent_steps) - 1)
                    if status == "completed":
                        progress_bar.progress(100)
                        status_text.markdown("<strong style='color: #0d9488;'>✓ Journey compilation completed!</strong>", unsafe_allow_html=True)
                        success = True
                        break
                    elif status == "failed":
                        progress_bar.progress(0)
                        status_text.markdown("<strong style='color: #e53e3e;'>❌ Agent planning execution failed.</strong>", unsafe_allow_html=True)
                        break
                    else:
                        step_val = int(((current_idx + 1) / len(agent_steps)) * 90)
                        progress_bar.progress(step_val)
                        status_text.markdown(f"Running: <em>{agent_steps[current_idx][0]}</em>", unsafe_allow_html=True)
                        
                        log_html = "<ul style='list-style-type: none; padding-left: 0; font-size: 13px; line-height: 1.6;'>"
                        for i in range(current_idx + 1):
                            log_html += f"<li style='color: #319795;'>✓ {agent_steps[i][1]}</li>"
                        log_html += "</ul>"
                        log_placeholder.markdown(log_html, unsafe_allow_html=True)
                        
                else:
                    st.error(f"Failed to fetch status: {resp.text}")
                    break
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")
                break
                
            time.sleep(4)
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
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- ITINERARY VIEW PAGE -----------------
def render_itinerary_page():
    render_sidebar()
    
    # Fetch details of current trip
    try:
        resp = httpx.get(
            f"{API_BASE_URL}/trips/{st.session_state.current_trip_id}",
            headers=get_auth_headers()
        )
        if resp.status_code != 200:
            st.error(f"Could not load trip details: {resp.text}")
            return
        trip = resp.json()
    except Exception as e:
        st.error(f"Error connecting to server: {e}")
        return

    # Back to Dashboard button
    if st.button("← Back to Dashboard", key="back_to_dashboard_btn"):
        st.session_state.page = "dashboard"
        st.rerun()
        
    st.markdown(f"## 🗺️ Itinerary Dashboard: {trip['destination_city']}")
    st.markdown(f"**From**: {trip['source_city']} | **Duration**: {trip['trip_days']} Days | **Start Date**: {trip['start_date']} | **Travelers**: {trip['adults']} Adults, {trip['children']} Children")
    
    # Vibe Summary Paragraph
    itinerary_data = trip.get("itinerary") or {}
    if itinerary_data.get("summary"):
        st.info(f"💡 **AI Summary**: {itinerary_data['summary']}")

    # Bento columns
    col_left, col_right = st.columns([1, 1.8])
    
    with col_left:
        # Flights Card
        st.markdown("### ✈️ Flights")
        flights_data = trip.get("flights") or {}
        if flights_data:
            for idx, flight in enumerate(flights_data.get("flight_options", [])):
                st.markdown(f"""
                <div class='custom-sub-card'>
                    <div style="display: flex; justify-content: space-between; font-weight: bold;">
                        <span>{flight.get('airline', 'Flight')}</span>
                        <span style="color: #2b6cb0;">{flight.get('total_price_inr', 0):,} INR</span>
                    </div>
                    <div style="font-size: 13px; color: #4a5568; margin-top: 5px;">
                        Flight: {flight.get('flight_number', 'N/A')} • Departure: {flight.get('departure_time', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No flights data found.")
            
        # Weather Card
        st.markdown("### 🌤️ Weather")
        weather_data = trip.get("weather") or {}
        if weather_data:
            st.markdown(f"""
            <div class='custom-card'>
                <p><strong>Current Forecast:</strong> {weather_data.get('current_weather', 'N/A')} ({weather_data.get('current_temp', 'N/A')})</p>
                <p><strong>Estimated Weather:</strong> {weather_data.get('estimated_weather', 'N/A')}</p>
                <p><strong>Estimated Temp:</strong> {weather_data.get('estimated_temp', 'N/A')}</p>
                <div class='custom-sub-card' style="margin-top: 10px;">
                    <span style="font-size: 11px; font-weight: bold; color: #4a5568; text-transform: uppercase;">Best Visit Season:</span>
                    <p style="font-size: 13px; margin-top: 3px;">{weather_data.get('best_weather', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No weather data found.")
            
        # Packing List Card
        st.markdown("### 🎒 Packing Checklist")
        if itinerary_data.get("packing_list"):
            for item in itinerary_data["packing_list"]:
                st.checkbox(item, key=f"pack_{item}_{trip['id']}")
        else:
            st.info("No packing list found.")
            
    with col_right:
        # Hotel Cards
        st.markdown("### 🏨 Hotels")
        hotels_data = trip.get("hotels") or []
        if hotels_data:
            for hotel in hotels_data:
                tier = hotel.get("tier", "Standard").upper()
                st.markdown(f"""
                <div class='custom-card'>
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <span style="font-size: 16px; font-weight: bold;">{hotel.get('hotel_name')}</span>
                        <span class="tag">{tier}</span>
                    </div>
                    <div style="font-size: 12px; color: #718096; margin-top: 3px;">📍 {hotel.get('neighborhood')}</div>
                    <p style="font-size: 13px; color: #4a5568; margin-top: 8px;">{hotel.get('description')}</p>
                    <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #edf2f7; display: flex; justify-content: space-between; align-items: end;">
                        <span style="font-size: 12px; color: #718096;">{hotel.get('nightly_rate_inr', 0):,} INR/night</span>
                        <strong style="color: #2d3748; font-size: 15px;">{hotel.get('total_cost_inr', 0):,} INR</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hotels data found.")
            
        # Budget Analysis Card
        st.markdown("### 📊 Budget Health")
        budget_data = trip.get("budget_breakdown") or {}
        if budget_data:
            limit = trip["budget"]
            est_total = budget_data.get("total_estimated_cost_inr", 0)
            is_over = budget_data.get("is_over_budget", False)
            pct = min(int((est_total / limit) * 100), 100)
            
            status_lbl = "OVER BUDGET" if is_over else "ON TRACK"
            tag_class = "tag-red" if is_over else "tag"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span>Estimated Cost: <strong>{est_total:,} INR</strong> / {limit:,} INR</span>
                <span class="{tag_class}">{status_lbl}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct)
            
            st.markdown("<br><strong>Itemized Costs</strong>", unsafe_allow_html=True)
            for exp in budget_data.get("itemized_expenses", []):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; font-size: 13px; padding: 5px 0; border-bottom: 1px solid #edf2f7;">
                    <span>{exp.get('category')} <span style="font-size:11px; color:#718096;">({exp.get('details')})</span></span>
                    <span>{exp.get('cost_inr', 0):,} INR</span>
                </div>
                """, unsafe_allow_html=True)
                
            suggestions = budget_data.get("savings_suggestions", [])
            if suggestions:
                st.markdown("<br><strong style='color: #0d9488;'>AI Savings Recommendations:</strong>", unsafe_allow_html=True)
                for s in suggestions:
                    st.info(f"💡 {s}")
        else:
            st.info("No budget details found.")

    # Day-by-Day Itinerary List
    st.markdown("### 📅 Proposed Itinerary")
    if itinerary_data.get("days"):
        for day in itinerary_data["days"]:
            with st.expander(f"Day {day.get('day')} — {day.get('date')} ({day.get('hotel', 'Hotel Stays')})", expanded=True):
                st.markdown(f"<p style='font-size: 13px; color: #4a5568;'>🍽️ <strong>Meals:</strong> {day.get('meals', 'N/A')}</p>", unsafe_allow_html=True)
                if day.get("notes"):
                    st.markdown(f"<p style='font-size: 13px; color: #718096; background-color: #f7fafc; padding: 8px 12px; border-radius: 4px;'>📝 Note: {day.get('notes')}</p>", unsafe_allow_html=True)
                
                for act in day.get("activities", []):
                    child_badge = ""
                    if trip["children"] > 0 and act.get("child_friendly", True):
                        child_badge = " <span class='tag'>Child Friendly</span>"
                        
                    st.markdown(f"""
                    <div class='custom-sub-card'>
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <span style="font-size: 10px; font-weight: bold; text-transform: uppercase; color: #a0aec0;">{act.get('time_of_day')}</span>
                                <div style="font-size: 14px; font-weight: bold; color: #2d3748; margin-top: 2px;">{act.get('name')}{child_badge}</div>
                            </div>
                            <span style="font-size: 12px; color: #718096;">{act.get('duration_minutes', 0)} mins • {act.get('cost_inr', 0):,} INR</span>
                        </div>
                        <p style="font-size: 13px; color: #4a5568; margin-top: 6px; line-height: 1.4;">{act.get('description')}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No day itinerary plan found.")

# ----------------- DASHBOARD / TRIP LIST VIEW -----------------
def render_dashboard_page():
    render_sidebar()
    
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
        st.markdown("## 🎒 Saved Itineraries")
        if not trips:
            st.info("You haven't planned any trips yet! Use the 'Create New Plan' tab to generate one.")
        else:
            for trip in trips:
                st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                col_name, col_meta, col_status, col_action = st.columns([1.5, 2, 1, 1])
                
                with col_name:
                    st.markdown(f"<h4>📍 {trip['destination_city']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #718096; font-size: 13px;'>Departure: {trip['source_city']}</span>", unsafe_allow_html=True)
                with col_meta:
                    st.markdown(f"<p style='margin: 0;'><strong>Date:</strong> {trip['start_date']} ({trip['trip_days']} Days)</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 0; color: #4a5568;'><strong>Budget:</strong> {trip['budget']:,} INR</p>", unsafe_allow_html=True)
                with col_status:
                    stat = trip['status']
                    tag_class = "tag" if stat == "completed" else ("tag-blue" if stat == "processing" else "tag-red")
                    st.markdown(f"<span class='{tag_class}'>{stat}</span>", unsafe_allow_html=True)
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
                        st.markdown("<p style='font-size: 12px; color: #c53030; font-weight: bold;'>Execution failed.</p>", unsafe_allow_html=True)
                        
                st.markdown("</div>", unsafe_allow_html=True)

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
