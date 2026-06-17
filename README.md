# TripMind AI Travel Planner

TripMind is an AI-powered travel planner that builds customized day-by-day travel itineraries. It utilizes a cooperative multi-agent workflow orchestrated by LangGraph to gather destination weather, flights, hotel selections, and attractions, producing a cohesive schedule and budget breakdown matching the user's travel parameters.

---

## Features

- **User Authentication:** Safe signup and login using Bcrypt password hashing and JWT tokens.
- **AI Agent Workflow:** Cooperating specialized agents managed via LangGraph:
  - **Planner Agent:** Normalizes cities and validates request parameters.
  - **Weather Agent:** Evaluates temperature ranges and weather conditions.
  - **Flight Agent:** Proposes flight options using scheduler schemas.
  - **Hotel Agent:** Suggests budget, mid-range, and premium lodging options.
  - **Attraction Agent:** Selects sightseeing spots matching user interests.
  - **Budget Agent:** Evaluates total expenses and provides savings tips.
  - **Itinerary Agent:** Organizes all data into a cohesive day-by-day schedule.
- **Live APIs Integration:** Fetches live resources from Geoapify (attractions and hotels), AviationStack (flights), and OpenWeatherMap (local weather forecasts).
- **Interactive Dashboard:** Modern React client to view itineraries, check budget details, and explore local travel recommendations.

---

## Project Structure

```text
TripMind/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agents
│   │   ├── core/            # Security and config settings
│   │   ├── db/              # SQLAlchemy connection and session setup
│   │   ├── graph/           # LangGraph workflow definition
│   │   ├── models/          # SQLAlchemy Database tables
│   │   ├── routes/          # API endpoint routes
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # Business logic services
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main React Application
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

---

## Setup and Installation

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment variables:**
   Create a `.env` file in the `backend/` directory with the following variables:
   ```env
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5402/tripmind
   OPENAI_API_KEY=your_openai_api_key
   GEOAPIFY_API_KEY=your_geoapify_key
   OPENWEATHER_API_KEY=your_openweather_key
   AVIATIONSTACK_API_KEY=your_aviationstack_key
   SECRET_KEY=your_jwt_secret_key
   ```

5. **Start the FastAPI backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install the dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser to view the application.

---

## API Endpoints

### Authentication
- `POST /auth/register` - Registers a new user.
- `POST /auth/login` - Authenticates user and returns JWT access tokens.
- `POST /auth/google` - Allows user login via Google OAuth credentials.

### Trips
- `POST /trips/` - Creates a new trip and schedules the planning workflow.
- `GET /trips/` - Lists all trips belonging to the logged-in user.
- `GET /trips/{trip_id}` - Retrieves detailed itinerary and agent logs for a trip.
- `PUT /trips/{trip_id}` - Updates a trip configuration.
- `DELETE /trips/{trip_id}` - Deletes a trip record.
