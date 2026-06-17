import { useState, useEffect } from 'react';
import { 
  Compass, Plane, Sun, Cloud, Plus, LogOut, Loader2, 
  CheckSquare, Square, DollarSign, Calendar, MapPin, 
  Users, Heart, ArrowLeft, AlertTriangle, Info, Map, 
  ChevronDown, ChevronUp, User, Sparkles, Navigation,
  Activity, CloudSun, Eye, Trash2, CheckCircle2, Briefcase
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const AGENT_STEPS = [
  { title: "Initializing Agent Graph Workflow", desc: "Understanding trip parameters" },
  { title: "Planner Agent", desc: "Normalizing locations and validating realistic place/budget constraints" },
  { title: "Weather Agent", desc: "Querying OpenWeather for historical and real-time forecast data" },
  { title: "Flight Agent", desc: "Searching Aviationstack for outbound and return airline listings" },
  { title: "Hotel Agent", desc: "Scraping Geoapify Places for local hotels, hostels, and lodgings" },
  { title: "Attraction Agent", desc: "Fetching sightseeing spots and checking child-friendly parameters" },
  { title: "Budget Agent", desc: "Compiling itemized balance estimates and generating savings options" },
  { title: "Itinerary Agent", desc: "Synthesizing schedule timelines and creating your packing list" }
];

const INTERESTS_LIST = [
  "Culture", "Food", "Nature", "Adventure", "Temples", "Shopping", 
  "Nightlife", "Family", "Photography", "History", "Architecture", "Relaxation"
];

const stripEmojis = (text) => {
  if (typeof text !== 'string') return text;
  
  return text.replace(/[\u{1F300}-\u{1F9FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1F004}\u{1F0CF}\u{1F170}-\u{1F251}\u{2B50}\u{2605}\u{2606}]/gu, '').trim();
};

function App() {
  
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [userEmail, setUserEmail] = useState(localStorage.getItem('user_email') || null);
  const [page, setPage] = useState(token ? 'dashboard' : 'auth');
  const [authMode, setAuthMode] = useState('login');
  const [currentTripId, setCurrentTripId] = useState(null);
  
  
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authLoading, setAuthLoading] = useState(false);

  
  const [trips, setTrips] = useState([]);
  const [currentTrip, setCurrentTrip] = useState(null);
  const [tripsLoading, setTripsLoading] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const [activeTab, setActiveTab] = useState('new');

  
  const [formData, setFormData] = useState({
    source_city: '',
    destination_city: '',
    trip_days: '',
    start_date: '',
    travel_included: true,
    budget: '',
    adults: '',
    children: '',
    interests: []
  });

  
  const [pollingProgress, setPollingProgress] = useState(0);
  const [pollingStatusText, setPollingStatusText] = useState('');
  const [pollingLogs, setPollingLogs] = useState([]);
  const [pollingError, setPollingError] = useState(null);
  const [activeInterval, setActiveInterval] = useState(null);

  
  const [checklistStates, setChecklistStates] = useState({});
  const [expandedDays, setExpandedDays] = useState({});

  
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('user_email', userEmail);
      fetchTrips();
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('user_email');
      setTrips([]);
    }
  }, [token]);

  
  const fetchTrips = async () => {
    if (!token) return;
    setTripsLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/trips/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 200) {
        const data = await res.json();
        setTrips(data);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (e) {
      console.error("Fetch trips failed", e);
    } finally {
      setTripsLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUserEmail(null);
    setCurrentTripId(null);
    setCurrentTrip(null);
    setFormData({
      source_city: '',
      destination_city: '',
      trip_days: '',
      start_date: '',
      travel_included: true,
      budget: '',
      adults: '',
      children: '',
      interests: []
    });
    if (activeInterval) {
      clearInterval(activeInterval);
      setActiveInterval(null);
    }
    setPage('auth');
  };

  
  const formatDuration = (mins) => {
    if (!mins || isNaN(mins)) return '0 mins';
    const m = parseInt(mins, 10);
    if (m < 60) return `${m} mins`;
    
    const d = Math.floor(m / 1440);
    const remMin = m % 1440;
    const h = Math.floor(remMin / 60);
    const min = remMin % 60;
    
    let result = [];
    if (d > 0) result.push(`${d}d`);
    if (h > 0) result.push(`${h}h`);
    if (min > 0) result.push(`${min}m`);
    
    return result.join(' ');
  };

  
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      setAuthError("Please fill in both email and password fields.");
      return;
    }
    setAuthLoading(true);
    setAuthError(null);
    try {
      const formParams = new URLSearchParams();
      formParams.append('username', loginEmail);
      formParams.append('password', loginPassword);

      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formParams
      });

      let data = {};
      const responseText = await res.text();
      try {
        if (responseText) {
          data = JSON.parse(responseText);
        }
      } catch (jsonErr) {
        console.error("Could not parse JSON response", jsonErr);
      }

      if (res.status === 200) {
        setFormData({
          source_city: '',
          destination_city: '',
          trip_days: '',
          start_date: '',
          travel_included: true,
          budget: '',
          adults: '',
          children: '',
          interests: []
        });
        setToken(data.access_token);
        setUserEmail(loginEmail);
        setPage('dashboard');
      } else {
        setAuthError(data.detail || "Incorrect email or password. Please check your credentials and try again.");
      }
    } catch (err) {
      setAuthError("Unable to connect to the server. Please check your internet connection or verify if the backend is running.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    if (!signupName || !signupEmail || !signupPassword) {
      setAuthError("All registration fields are required.");
      return;
    }
    if (!agreeTerms) {
      setAuthError("You must agree to the Terms and Conditions to proceed.");
      return;
    }
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: signupEmail,
          full_name: signupName,
          password: signupPassword
        })
      });

      let data = {};
      const responseText = await res.text();
      try {
        if (responseText) {
          data = JSON.parse(responseText);
        }
      } catch (jsonErr) {
        console.error("Could not parse JSON response", jsonErr);
      }

      if (res.status === 201) {
        setAuthMode('login');
        setLoginEmail(signupEmail);
        setAuthError("Registration successful! Please log in with your credentials.");
      } else {
        setAuthError(data.detail || "Registration failed. Please try a different email address.");
      }
    } catch (err) {
      setAuthError("Unable to connect to the server. Please check your internet connection or verify if the backend is running.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleGoogleSimulator = async () => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: "simulated_google_oauth_token" })
      });
      let data = {};
      const responseText = await res.text();
      try {
        if (responseText) {
          data = JSON.parse(responseText);
        }
      } catch (jsonErr) {
        console.error("Could not parse JSON response", jsonErr);
      }

      if (res.status === 200) {
        setFormData({
          source_city: '',
          destination_city: '',
          trip_days: '',
          start_date: '',
          travel_included: true,
          budget: '',
          adults: '',
          children: '',
          interests: []
        });
        setToken(data.access_token);
        setUserEmail('google_user@example.com');
        setPage('dashboard');
      } else {
        setAuthError(data.detail || "Google OIDC authentication failed. Please try again.");
      }
    } catch (err) {
      setAuthError("Google authentication simulator offline. Please try email login instead.");
    } finally {
      setAuthLoading(false);
    }
  };

  
  const handleNavNewTrip = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    const isFormDirty = formData.source_city || formData.destination_city || formData.trip_days || formData.start_date || formData.budget || formData.adults || formData.children || formData.interests.length > 0;
    
    if (isFormDirty) {
      const executeForm = window.confirm("You have a trip plan in progress. Would you like to generate this trip itinerary now?");
      if (executeForm) {
        handleCreateTripSubmit();
        return;
      }
      
      const discardForm = window.confirm("Are you sure you want to discard this trip plan and start a new empty form?");
      if (!discardForm) {
        return; 
      }
    }
    
    
    setFormData({
      source_city: '',
      destination_city: '',
      trip_days: '',
      start_date: '',
      travel_included: true,
      budget: '',
      adults: '',
      children: '',
      interests: []
    });
    
    if (activeInterval) {
      clearInterval(activeInterval);
      setActiveInterval(null);
    }
    
    setCurrentTripId(null);
    setCurrentTrip(null);
    setPage('dashboard');
    setActiveTab('new');
  };

  
  const handleCreateTripSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!formData.source_city || !formData.destination_city) {
      alert("Please enter both departure and destination cities.");
      return;
    }
    
    const daysVal = parseInt(formData.trip_days, 10);
    const budgetVal = parseInt(formData.budget, 10);
    const adultsVal = parseInt(formData.adults, 10);
    const childrenVal = parseInt(formData.children, 10) || 0;

    if (isNaN(daysVal) || daysVal < 1) {
      alert("Please enter a valid trip duration (at least 1 day).");
      return;
    }
    if (isNaN(budgetVal) || budgetVal < 1000) {
      alert("Please enter a valid total budget (at least 1,000 INR).");
      return;
    }
    if (isNaN(adultsVal) || adultsVal < 1) {
      alert("Please enter at least 1 adult traveler.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/trips/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          source_city: formData.source_city,
          destination_city: formData.destination_city,
          trip_days: daysVal,
          start_date: formData.start_date || new Date().toISOString().split('T')[0],
          travel_included: !!formData.travel_included,
          budget: budgetVal,
          adults: adultsVal,
          children: childrenVal,
          interests: formData.interests.join(', ')
        })
      });
      const data = await res.json();
      if (res.status === 201) {
        setCurrentTripId(data.id);
        startPollingWorkflow(data.id);
      } else {
        alert(data.detail || "Trip planning setup failed.");
      }
    } catch (err) {
      alert("Cannot register trip parameters. Please check if the backend server is running.");
    }
  };

  
  const startPollingWorkflow = (tripId) => {
    setPage('loading');
    setPollingProgress(0);
    setPollingError(null);
    setPollingLogs([]);
    
    if (activeInterval) {
      clearInterval(activeInterval);
    }
    
    let counter = 0;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/trips/${tripId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.status === 200) {
          const tripDetails = await res.json();
          const status = tripDetails.status;
          
          const currentStepIdx = Math.min(counter, AGENT_STEPS.length - 1);
          setPollingStatusText(AGENT_STEPS[currentStepIdx].title);
          
          
          const newLogs = [];
          for (let i = 0; i <= currentStepIdx; i++) {
            newLogs.push(AGENT_STEPS[i].desc);
          }
          setPollingLogs(newLogs);

          if (status === 'completed') {
            setPollingProgress(100);
            clearInterval(interval);
            setActiveInterval(null);
            setTimeout(() => {
              viewTripDetails(tripId);
            }, 1000);
          } else if (status === 'failed') {
            setPollingError("AI generation encountered a glitch.");
            clearInterval(interval);
            setActiveInterval(null);
          } else {
            const progressPct = Math.min(Math.round(((currentStepIdx + 1) / AGENT_STEPS.length) * 90), 90);
            setPollingProgress(progressPct);
          }
        }
      } catch (err) {
        setPollingError("Communication breakdown with backend server.");
        clearInterval(interval);
        setActiveInterval(null);
      }
      
      counter++;
      if (counter > 40) {
        setPollingError("AI agents timed out compiling the request.");
        clearInterval(interval);
        setActiveInterval(null);
      }
    }, 4000);
    
    setActiveInterval(interval);
  };

  
  const viewTripDetails = async (tripId) => {
    setDetailsLoading(true);
    setCurrentTripId(tripId);
    setPage('itinerary');
    try {
      const res = await fetch(`${API_BASE_URL}/trips/${tripId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 200) {
        const data = await res.json();
        setCurrentTrip(data);
        
        const initialExpanded = {};
        if (data.itinerary?.days) {
          data.itinerary.days.forEach(d => {
            initialExpanded[d.day] = true;
          });
        }
        setExpandedDays(initialExpanded);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setDetailsLoading(false);
    }
  };

  
  const toggleChecklistItem = (item) => {
    setChecklistStates(prev => ({
      ...prev,
      [item]: !prev[item]
    }));
  };

  
  const toggleDayExpanded = (dayNum) => {
    setExpandedDays(prev => ({
      ...prev,
      [dayNum]: !prev[dayNum]
    }));
  };

  
  const toggleInterestTag = (interest) => {
    setFormData(prev => {
      const isSelected = prev.interests.includes(interest);
      const updated = isSelected 
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest];
      
      if (updated.length > 5) return prev; 
      return { ...prev, interests: updated };
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      
      {}
      {page === 'auth' && (
        <div className="flex-1 flex flex-col justify-center items-center p-4 md:p-8 relative overflow-hidden bg-gradient-to-tr from-teal-500/5 via-slate-50 to-blue-500/5">
          <div className="w-full max-w-[1000px] bg-white rounded-3xl shadow-xl overflow-hidden grid grid-cols-1 md:grid-cols-2 border border-slate-200/60 min-h-[560px]">
            
            {}
            <div className="hidden md:flex flex-col justify-between p-12 bg-slate-50/50 border-r border-slate-200/80">
              <div>
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
                  <Compass className="h-8 w-8 text-teal-600 animate-spin-slow" />
                  TripMind AI
                </h1>
                <p className="text-slate-500 text-sm mt-2 font-medium">
                  Your intelligent concierge for effortless global exploration.
                </p>
              </div>

              {}
              <div className="relative rounded-2xl overflow-hidden border border-slate-200/80 shadow-sm aspect-video my-6">
                <img 
                  className="w-full h-full object-cover" 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuA_cwRmpXomVxn6Yw3_SqJ1Hyd80CLs2iR3RPUmXFI3PsKWWXHlI7mwlTiX-B5XdYTQ-BvloYJuXnFRcmgHZk70HM-p3Ycok24JF5WShtgDAkqfWkvx12rzmjItGEmFviNUFmKviomVNNdFS9drvjsHlPVzAve0sydqUZQJo0FooHpCakfo1D34rgwANSbppbF94IZ2w8FfB-pLKqnBe5UJrEZj5JOf3tOqVePpc6cnT5CNJaL33uxBawAA3_k_Q3Pre7NwJSdw6YI" 
                  alt="Scenic exploration image"
                />
              </div>

              <div>
                <blockquote className="text-slate-600 italic text-sm mb-6 border-l-2 border-teal-500 pl-4 leading-relaxed font-semibold">
                  "The best journeys aren't planned by maps, but by understanding the traveler's soul."
                </blockquote>
                <div className="flex items-center gap-3">
                  <div className="h-[3px] w-12 bg-teal-600 rounded-full"></div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                    Premium Intelligence
                  </span>
                </div>
              </div>
            </div>

            {}
            <div className="p-8 md:p-12 flex flex-col justify-center">
              {authMode === 'login' ? (
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome Back</h2>
                  <p className="text-slate-500 text-sm mb-6">Sign in to resume your latest itinerary planning.</p>
                  
                  {authError && (
                    <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-xl text-xs mb-4">
                      {authError}
                    </div>
                  )}

                  <button 
                    onClick={handleGoogleSimulator}
                    disabled={authLoading}
                    className="w-full flex items-center justify-center gap-3 py-3 border border-slate-200 rounded-xl hover:bg-slate-50 active:scale-95 transition-all text-sm font-semibold text-slate-800 cursor-pointer"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                    </svg>
                    Continue with Google
                  </button>

                  <div className="relative flex items-center justify-center my-6">
                    <div className="flex-grow border-t border-slate-200"></div>
                    <span className="px-4 text-slate-400 text-xs font-semibold uppercase tracking-widest bg-white">
                      or use email
                    </span>
                    <div className="flex-grow border-t border-slate-200"></div>
                  </div>

                  <form onSubmit={handleLoginSubmit} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Email Address</label>
                      <input 
                        type="email" 
                        placeholder="alex@tripmind.ai"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1 ml-1">
                        <label className="block text-xs font-bold text-slate-500">Password</label>
                        <a href="#" className="text-xs text-teal-600 font-semibold hover:underline">Forgot?</a>
                      </div>
                      <input 
                        type="password" 
                        placeholder="••••••••"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all"
                      />
                    </div>
                    <button 
                      type="submit" 
                      disabled={authLoading}
                      className="w-full py-3 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2 mt-6 active:scale-95 shadow-md shadow-slate-900/10 cursor-pointer"
                    >
                      {authLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                      Sign In
                    </button>
                  </form>
                  <p className="mt-8 text-center text-xs text-slate-500 font-semibold">
                    New to TripMind?{' '}
                    <button onClick={() => setAuthMode('signup')} className="text-teal-600 font-bold hover:underline cursor-pointer">
                      Sign up
                    </button>
                  </p>
                </div>
              ) : (
                <div>
                  <button 
                    onClick={() => setAuthMode('login')}
                    className="flex items-center gap-1 text-slate-500 hover:text-slate-950 font-bold text-xs mb-4 transition-colors cursor-pointer"
                  >
                    <ArrowLeft className="h-4 w-4" /> Back to Login
                  </button>
                  
                  <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Create Account</h2>
                  <p className="text-slate-500 text-sm mb-6">Begin your journey with personalized travel insights.</p>

                  {authError && (
                    <div className="p-3 bg-teal-50 border border-teal-200 text-teal-700 rounded-xl text-xs mb-4">
                      {authError}
                    </div>
                  )}

                  <form onSubmit={handleSignupSubmit} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Full Name</label>
                      <input 
                        type="text" 
                        placeholder="Alex Traveler"
                        value={signupName}
                        onChange={(e) => setSignupName(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Email Address</label>
                      <input 
                        type="email" 
                        placeholder="alex@tripmind.ai"
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Password</label>
                      <input 
                        type="password" 
                        placeholder="Min. 8 characters"
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all"
                      />
                    </div>
                    <div className="flex items-start gap-2 pt-2">
                      <input 
                        type="checkbox" 
                        id="terms"
                        checked={agreeTerms}
                        onChange={(e) => setAgreeTerms(e.target.checked)}
                        className="mt-1 h-4 w-4 text-teal-600 focus:ring-teal-500 border-slate-300 rounded cursor-pointer"
                      />
                      <label htmlFor="terms" className="text-slate-500 text-xs font-semibold select-none cursor-pointer">
                        I agree to the <a href="#" className="text-teal-600 hover:underline font-bold">Terms of Service</a> and <a href="#" className="text-teal-600 hover:underline font-bold">Privacy Policy</a>.
                      </label>
                    </div>
                    <button 
                      type="submit" 
                      disabled={authLoading}
                      className="w-full py-3 bg-teal-700 text-white font-bold rounded-xl mt-6 hover:bg-teal-800 transition-all flex items-center justify-center gap-2 active:scale-95 shadow-md shadow-teal-700/10 cursor-pointer"
                    >
                      {authLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                      Create Account
                    </button>
                  </form>
                  <p className="mt-8 text-center text-xs text-slate-500 font-semibold">
                    Already have an account?{' '}
                    <button onClick={() => setAuthMode('login')} className="text-slate-900 font-bold hover:underline cursor-pointer">
                      Log In
                    </button>
                  </p>
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {}
      {page !== 'auth' && (
        <div className="flex-1 flex flex-col md:flex-row">
          
          {}
          <aside className="w-full md:w-[260px] bg-white p-6 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-200/80">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <Compass className="h-6 w-6 text-teal-600" />
                <span className="font-bold text-lg tracking-tight text-slate-900">TripMind AI</span>
              </div>
              <div className="p-3.5 bg-slate-50 border border-slate-200/60 rounded-xl mb-6">
                <span className="text-[10px] text-slate-400 block font-bold uppercase tracking-wider">Signed in as</span>
                <span className="text-xs font-bold truncate block text-slate-700 mt-0.5">{userEmail}</span>
              </div>
              <nav className="space-y-2">
                <button 
                  onClick={handleNavNewTrip}
                  className="w-full flex items-center gap-2 px-4 py-3 bg-slate-900 hover:bg-slate-800 rounded-xl font-bold transition-all text-sm text-white cursor-pointer shadow-sm shadow-slate-900/10"
                >
                  <Plus className="h-4 w-4 text-white" /> New Trip Form
                </button>
                <button 
                  onClick={() => { 
                    if (activeInterval) {
                      clearInterval(activeInterval);
                      setActiveInterval(null);
                    }
                    setPage('dashboard'); 
                    setActiveTab('saved'); 
                    fetchTrips(); 
                  }}
                  className={`w-full flex items-center gap-2 px-4 py-3 rounded-xl font-semibold transition-all text-sm cursor-pointer ${
                    page === 'dashboard' && activeTab === 'saved'
                      ? 'bg-slate-100 text-slate-900 font-bold border border-slate-200/50'
                      : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                  }`}
                >
                  <Briefcase className="h-4 w-4" /> My Saved Trips
                </button>
              </nav>
            </div>
            
            <div className="mt-8 md:mt-0 pt-6 border-t border-slate-200/80">
              <button 
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-slate-200 hover:bg-slate-50 rounded-xl text-slate-500 hover:text-slate-800 transition-colors text-xs font-semibold cursor-pointer"
              >
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          </aside>

          {}
          <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-[1200px] mx-auto w-full">
            
            {}
            {page === 'dashboard' && (
              <div className="space-y-8">
                
                {}
                <div className="flex border-b border-slate-200 gap-6">
                  <button 
                    onClick={() => setActiveTab('new')}
                    className={`pb-3 text-lg font-bold border-b-2 transition-all cursor-pointer ${
                      activeTab === 'new' 
                        ? 'border-teal-700 text-slate-900' 
                        : 'border-transparent text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    Create New Plan
                  </button>
                  <button 
                    onClick={() => { setActiveTab('saved'); fetchTrips(); }}
                    className={`pb-3 text-lg font-bold border-b-2 transition-all flex items-center gap-2 cursor-pointer ${
                      activeTab === 'saved' 
                        ? 'border-teal-700 text-slate-900' 
                        : 'border-transparent text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    My Saved Trips
                    {trips.length > 0 && (
                      <span className="bg-slate-200 text-slate-800 text-xs px-2 py-0.5 rounded-full font-bold">
                        {trips.length}
                      </span>
                    )}
                  </button>
                </div>

                {activeTab === 'new' ? (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {}
                    <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200/60 p-6 md:p-8 shadow-sm">
                      <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-6 flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-teal-600" /> Plan a New Adventure
                      </h3>
                      
                      <form onSubmit={handleCreateTripSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Departure City</label>
                            <input 
                              type="text" 
                              placeholder="e.g. Delhi"
                              value={formData.source_city}
                              onChange={(e) => setFormData(prev => ({ ...prev, source_city: e.target.value }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Destination City</label>
                            <input 
                              type="text" 
                              placeholder="e.g. Rome"
                              value={formData.destination_city}
                              onChange={(e) => setFormData(prev => ({ ...prev, destination_city: e.target.value }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Duration (Days)</label>
                            <input 
                              type="number" 
                              min="1" 
                              max="30"
                              placeholder="e.g. 5"
                              value={formData.trip_days}
                              onChange={(e) => setFormData(prev => ({ ...prev, trip_days: e.target.value === '' ? '' : parseInt(e.target.value) }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Start Date</label>
                            <input 
                              type="date" 
                              value={formData.start_date}
                              onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                          <div className="md:col-span-2">
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Total Budget (INR)</label>
                            <input 
                              type="number" 
                              min="1000"
                              placeholder="e.g. 250000"
                              value={formData.budget}
                              onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value === '' ? '' : parseInt(e.target.value) }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                          <div className="flex items-center gap-2 md:pt-4 pl-1">
                            <input 
                              type="checkbox" 
                              id="travel_days"
                              checked={formData.travel_included}
                              onChange={(e) => setFormData(prev => ({ ...prev, travel_included: e.target.checked }))}
                              className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-slate-300 rounded cursor-pointer"
                            />
                            <label htmlFor="travel_days" className="text-slate-600 text-xs font-semibold select-none cursor-pointer">
                              Include Travel Days
                            </label>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Adult Travelers</label>
                            <input 
                              type="number" 
                              min="1"
                              placeholder="e.g. 2"
                              value={formData.adults}
                              onChange={(e) => setFormData(prev => ({ ...prev, adults: e.target.value === '' ? '' : parseInt(e.target.value) }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 mb-1 ml-1">Children</label>
                            <input 
                              type="number" 
                              min="0"
                              placeholder="e.g. 1"
                              value={formData.children}
                              onChange={(e) => setFormData(prev => ({ ...prev, children: e.target.value === '' ? '' : parseInt(e.target.value) }))}
                              autoComplete="off"
                              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all font-semibold"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-slate-500 mb-2 ml-1">
                            Travel Interests (Select up to 5)
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {INTERESTS_LIST.map((interest) => {
                              const isSelected = formData.interests.includes(interest);
                              return (
                                <button
                                  type="button"
                                  key={interest}
                                  onClick={() => toggleInterestTag(interest)}
                                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                                    isSelected 
                                      ? 'bg-teal-50 border-teal-500 text-teal-700 shadow-sm'
                                      : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                                  }`}
                                >
                                  {interest}
                                </button>
                              );
                            })}
                          </div>
                        </div>

                        <button 
                          type="submit"
                          className="w-full py-4 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 transition-all shadow-md active:scale-95 mt-4 cursor-pointer"
                        >
                          Generate AI Itinerary
                        </button>
                      </form>
                    </div>

                    {}
                    <div className="bg-slate-50 border border-slate-200/60 rounded-3xl p-6 md:p-8 flex flex-col justify-between">
                      <div>
                        <h4 className="text-lg font-bold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
                          <Activity className="h-5 w-5 text-teal-600 animate-pulse" />
                          Autonomous Agent Architecture
                        </h4>
                        <p className="text-slate-500 text-xs leading-relaxed mb-6 font-medium">
                          TripMind deploys 8 cooperating AI agents to fetch, analyze, and build your customized route plan:
                        </p>
                        <ul className="space-y-4 text-xs font-semibold text-slate-700">
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">1.</span>
                            <span><strong>Planner Agent</strong>: Feasibility checking & destination mapping.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">2.</span>
                            <span><strong>Weather Agent</strong>: Fetches historic parameters and forecasts.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">3.</span>
                            <span><strong>Flight Agent</strong>: Analyzes aviation routes and costs.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">4.</span>
                            <span><strong>Hotel Agent</strong>: Finds localized lodgings.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">5.</span>
                            <span><strong>Attraction Agent</strong>: Identifies child-friendly sightseeing spots.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">6.</span>
                            <span><strong>Budget Agent</strong>: Estimates expenses and lists savings options.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-teal-600 font-bold">7.</span>
                            <span><strong>Itinerary Agent</strong>: Final timeline mapping and day-by-day notes.</span>
                          </li>
                        </ul>
                      </div>
                      <div className="pt-6 border-t border-slate-200 mt-6 flex justify-between items-center text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                        <span>Multi-Agent LangGraph System</span>
                        <span>v1.0</span>
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="bg-white rounded-3xl border border-slate-200/60 p-6 md:p-8 shadow-sm">
                    <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-6 flex items-center gap-2">
                      <Briefcase className="h-5 w-5 text-slate-700" /> Saved Travel Plans
                    </h3>

                    {tripsLoading ? (
                      <div className="flex flex-col items-center justify-center py-12 gap-2 text-slate-400">
                        <Loader2 className="h-8 w-8 animate-spin" />
                        <span className="text-sm">Loading plans...</span>
                      </div>
                    ) : trips.length === 0 ? (
                      <div className="text-center py-12 text-slate-400">
                        <Compass className="h-12 w-12 mx-auto mb-3 opacity-30" />
                        <p className="text-sm">No planned itineraries yet. Switch to the 'Create New Plan' tab to generate one!</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {trips.map((trip) => {
                          const isCompleted = trip.status === 'completed';
                          const isProcessing = trip.status === 'processing';
                          
                          return (
                            <div 
                              key={trip.id}
                              onClick={() => {
                                if (isCompleted) {
                                  viewTripDetails(trip.id);
                                } else if (isProcessing) {
                                  startPollingWorkflow(trip.id);
                                }
                              }}
                              className="p-5 border border-slate-200 rounded-2xl bg-white hover:bg-slate-50/80 hover:border-slate-300 hover:shadow-sm transition-all flex flex-col justify-between min-h-[160px] cursor-pointer group"
                            >
                              <div>
                                <div className="flex justify-between items-start">
                                  <h4 className="font-bold text-slate-900 text-lg"> {stripEmojis(trip.destination_city)}</h4>
                                  <span className={`text-[10px] font-bold uppercase px-2.5 py-1 rounded-full ${
                                    isCompleted 
                                      ? 'bg-teal-100 text-teal-800' 
                                      : isProcessing 
                                        ? 'bg-blue-100 text-blue-800' 
                                        : 'bg-red-100 text-red-800'
                                  }`}>
                                    {trip.status}
                                  </span>
                                </div>
                                <p className="text-xs text-slate-500 mt-1">From: {stripEmojis(trip.source_city)}</p>
                                
                                <div className="grid grid-cols-2 gap-4 mt-4 text-xs font-semibold text-slate-600">
                                  <div>
                                    <span className="text-slate-400 text-[10px] block font-bold uppercase">Dates</span>
                                    <span>{trip.start_date} ({trip.trip_days} Days)</span>
                                  </div>
                                  <div>
                                    <span className="text-slate-400 text-[10px] block font-bold uppercase">Budget</span>
                                    <span>{trip.budget.toLocaleString()} INR</span>
                                  </div>
                                </div>
                              </div>

                              <div className="pt-4 border-t border-slate-200/50 mt-4 flex justify-end">
                                {isCompleted ? (
                                  <span 
                                    className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold group-hover:bg-slate-800 transition-colors flex items-center gap-1.5 shadow-sm"
                                  >
                                    <Eye className="h-4.5 w-4.5" /> View Plan
                                  </span>
                                ) : isProcessing ? (
                                  <span 
                                    className="px-4 py-2 bg-teal-700 text-white rounded-xl text-xs font-bold group-hover:bg-teal-800 transition-colors flex items-center gap-1.5 shadow-sm"
                                  >
                                    <Loader2 className="h-4 w-4 animate-spin" /> Resume
                                  </span>
                                ) : (
                                  <span className="text-xs text-red-600 font-bold">Execution Failed</span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}

              </div>
            )}

            {}
            {page === 'loading' && (
              <div className="max-w-[600px] mx-auto py-12 space-y-8">
                <div className="text-center space-y-2">
                  <h2 className="text-2xl font-bold text-slate-900 tracking-tight">TripMind AI is planning your journey...</h2>
                  <p className="text-slate-500 text-sm">
                    Our 8 autonomous agents are fetching, cross-referencing, and synthesizing details.
                  </p>
                </div>

                <div className="bg-white rounded-3xl border border-slate-200/60 p-6 md:p-8 shadow-md space-y-6">
                  {pollingError ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex gap-3 items-center">
                        <AlertTriangle className="h-6 w-6 shrink-0" />
                        <div>
                          <span className="font-bold block">Planning Glitch</span>
                          <span className="text-xs">{pollingError}</span>
                        </div>
                      </div>
                      <button 
                        onClick={handleNavNewTrip}
                        className="w-full py-3 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 transition-all active:scale-95 cursor-pointer"
                      >
                        Return to Dashboard
                      </button>
                    </div>
                  ) : (
                    <>
                      {}
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-400">
                          <span className="text-teal-700 flex items-center gap-1">
                            <Loader2 className="h-3 w-3 animate-spin" /> {pollingStatusText || "Initializing"}
                          </span>
                          <span>{pollingProgress}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div 
                            className="bg-teal-600 h-full rounded-full transition-all duration-500" 
                            style={{ width: `${pollingProgress}%` }}
                          ></div>
                        </div>
                      </div>

                      {}
                      <div className="space-y-3 pt-4 border-t border-slate-100">
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest block">Execution Log</span>
                        <div className="space-y-2.5 max-h-[220px] overflow-y-auto">
                          {pollingLogs.map((log, idx) => (
                            <div key={idx} className="flex gap-2 items-start text-xs font-semibold text-teal-700 animate-fade-in">
                              <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-teal-500" />
                              <span>{log}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>

              </div>
            )}

            {}
            {page === 'itinerary' && (
              <div className="space-y-8">
                
                {}
                <button 
                  onClick={handleNavNewTrip}
                  className="flex items-center gap-1.5 text-slate-600 hover:text-slate-950 font-bold text-sm transition-colors cursor-pointer"
                >
                  <ArrowLeft className="h-4 w-4" /> Back to Dashboard
                </button>

                {detailsLoading || !currentTrip ? (
                  <div className="flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
                    <Loader2 className="h-10 w-10 animate-spin text-teal-600" />
                    <span className="text-sm font-semibold">Compiling results layout...</span>
                  </div>
                ) : (
                  <div className="space-y-8 animate-fade-in">
                    
                    {}
                    <div className="space-y-2 border-b border-slate-200 pb-6">
                      <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
                        Itinerary Dashboard: {stripEmojis(currentTrip.destination_city)}
                      </h2>
                      <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500 font-semibold pt-1">
                        <span className="flex items-center gap-1"><MapPin className="h-4 w-4 text-slate-400" /> From: {stripEmojis(currentTrip.source_city)}</span>
                        <span className="flex items-center gap-1"><Calendar className="h-4 w-4 text-slate-400" /> {currentTrip.start_date} ({currentTrip.trip_days} Days)</span>
                        <span className="flex items-center gap-1"><Users className="h-4 w-4 text-slate-400" /> Travelers: {currentTrip.adults} Adults, {currentTrip.children} Children</span>
                      </div>
                    </div>

                    {}
                    {currentTrip.itinerary?.summary && (
                      <div className="p-5 bg-teal-50/70 border border-teal-100 rounded-3xl flex gap-3.5 items-start">
                        <Info className="h-6 w-6 text-teal-700 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-teal-900 block text-sm mb-1">AI Trip Concept</span>
                          <p className="text-teal-800 text-sm leading-relaxed">{stripEmojis(currentTrip.itinerary.summary)}</p>
                        </div>
                      </div>
                    )}

                    {}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      
                      {}
                      <div className="space-y-8 lg:col-span-1">
                        
                        {}
                        <div className="bg-white rounded-3xl border border-slate-200/60 p-6 shadow-sm space-y-4">
                          <h4 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                            <Plane className="h-5 w-5 text-slate-700" /> Outbound / Return Flights
                          </h4>
                          {currentTrip.flights?.flight_options?.length > 0 ? (
                            <div className="space-y-3">
                              {currentTrip.flights.flight_options.map((flight, idx) => (
                                <div key={idx} className="p-4 bg-slate-50 border border-slate-100 rounded-2xl flex flex-col justify-between">
                                  <div className="flex justify-between items-center font-bold text-sm">
                                    <span className="text-slate-900">{stripEmojis(flight.airline)}</span>
                                    <span className="text-teal-700">{flight.total_price_inr ? `${flight.total_price_inr.toLocaleString()} INR` : 'Pricing N/A'}</span>
                                  </div>
                                  <div className="text-xs text-slate-500 mt-2 font-medium">
                                    Flight: {flight.flight_number} • Dept: {flight.departure_time}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-400 italic">No flight options generated.</p>
                          )}
                        </div>

                        {}
                        <div className="bg-white rounded-3xl border border-slate-200/60 p-6 shadow-sm space-y-4">
                          <h4 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                            <CloudSun className="h-5 w-5 text-slate-700" /> Climate Outlook
                          </h4>
                          {currentTrip.weather ? (
                            <div className="space-y-3 text-sm">
                              <p><strong>Current Forecast:</strong> {stripEmojis(currentTrip.weather.current_weather)} ({currentTrip.weather.current_temp})</p>
                              <p><strong>Estimated Weather:</strong> {stripEmojis(currentTrip.weather.estimated_weather)}</p>
                              <p><strong>Estimated Temp:</strong> {currentTrip.weather.estimated_temp}</p>
                              
                              <div className="p-3 bg-slate-50 border border-slate-100 rounded-2xl mt-4">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Best Season to Visit</span>
                                <span className="text-xs font-semibold text-slate-700 block">{stripEmojis(currentTrip.weather.best_weather)}</span>
                              </div>
                            </div>
                          ) : (
                            <p className="text-xs text-slate-400 italic">No climate forecasts found.</p>
                          )}
                        </div>

                        {}
                        <div className="bg-white rounded-3xl border border-slate-200/60 p-6 shadow-sm space-y-4">
                          <h4 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                            <Briefcase className="h-5 w-5 text-slate-700" /> Packing Checklist
                          </h4>
                          {currentTrip.itinerary?.packing_list?.length > 0 ? (
                            <div className="space-y-1.5 max-h-[300px] overflow-y-auto pr-1 font-semibold text-slate-700">
                              {currentTrip.itinerary.packing_list.map((item, idx) => {
                                const cleanItem = stripEmojis(item);
                                if (!cleanItem) return null;
                                const isChecked = checklistStates[cleanItem] || false;
                                return (
                                  <div 
                                    key={idx} 
                                    onClick={() => toggleChecklistItem(cleanItem)}
                                    className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-50 transition-all cursor-pointer select-none"
                                  >
                                    {isChecked ? (
                                      <CheckSquare className="h-5 w-5 text-teal-700 shrink-0" />
                                    ) : (
                                      <Square className="h-5 w-5 text-slate-300 shrink-0" />
                                    )}
                                    <span className={`text-sm font-semibold transition-all ${
                                      isChecked ? 'text-slate-400 line-through font-normal' : 'text-slate-755'
                                    }`}>
                                      {cleanItem}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-400 italic">No checklist generated.</p>
                          )}
                        </div>            </div>

                                  {}
                      <div className="lg:col-span-2 space-y-8">
                        
                        {}
                        <div className="bg-white rounded-3xl border border-slate-200/60 p-6 shadow-sm space-y-4">
                          <h4 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                            <Sun className="h-5 w-5 text-slate-700" /> Local Hotel Suggestions
                          </h4>
                          {currentTrip.hotels?.length > 0 ? (
                            <div className="space-y-4">
                              {currentTrip.hotels.map((hotel, idx) => (
                                <div key={idx} className="p-5 bg-slate-50 border border-slate-100 rounded-2xl space-y-3">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <h5 className="font-bold text-slate-900 text-base">{stripEmojis(hotel.hotel_name)}</h5>
                                      <span className="text-xs text-slate-400 block mt-0.5">neighborhood: {stripEmojis(hotel.neighborhood)}</span>
                                    </div>
                                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-teal-100 text-teal-800">
                                      {hotel.tier || 'Standard'}
                                    </span>
                                  </div>
                                  <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                                    {stripEmojis(hotel.description)}
                                  </p>
                                  <div className="pt-3 border-t border-slate-200/60 flex justify-between items-center text-xs text-slate-500 font-semibold">
                                    <span>Rate: {hotel.nightly_rate_inr?.toLocaleString()} INR / night</span>
                                    <strong className="text-slate-900 text-sm">Total: {hotel.total_cost_inr?.toLocaleString()} INR</strong>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-400 italic">No lodging options found.</p>
                          )}
                        </div>

                        {}
                        <div className="bg-white rounded-3xl border border-slate-200/60 p-6 shadow-sm space-y-4">
                          <h4 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                            <DollarSign className="h-5 w-5 text-slate-700" /> Budget Breakdown
                          </h4>
                          {currentTrip.budget_breakdown ? (
                            <div className="space-y-6">
                              
                              {}
                              <div>
                                <div className="flex justify-between text-xs font-bold text-slate-500 uppercase mb-2">
                                  <span>Total Spent: <strong>{currentTrip.budget_breakdown.total_estimated_cost_inr?.toLocaleString()} INR</strong></span>
                                  <span>Limit: {currentTrip.budget.toLocaleString()} INR</span>
                                </div>
                                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                                  <div 
                                    className={`h-full rounded-full transition-all ${
                                      currentTrip.budget_breakdown.is_over_budget ? 'bg-red-500' : 'bg-teal-600'
                                    }`}
                                    style={{ width: `${Math.min((currentTrip.budget_breakdown.total_estimated_cost_inr / currentTrip.budget) * 100, 100)}%` }}
                                  ></div>
                                </div>
                                {currentTrip.budget_breakdown.is_over_budget && (
                                  <span className="text-[10px] text-red-600 font-bold block mt-1 uppercase tracking-wider">
                                    Limit Exceeded. Check savings suggestions below.
                                  </span>
                                )}
                              </div>

                              {}
                              <div>
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">Itemized Expenses</span>
                                <div className="space-y-2.5">
                                  {currentTrip.budget_breakdown.itemized_expenses?.map((exp, idx) => (
                                    <div key={idx} className="flex justify-between items-center text-xs py-2 border-b border-slate-100 font-semibold">
                                      <div className="space-y-0.5">
                                        <span className="text-slate-800 font-bold block">{stripEmojis(exp.category)}</span>
                                        <span className="text-slate-400 block text-[10px]">{stripEmojis(exp.details)}</span>
                                      </div>
                                      <span className="text-slate-900">{exp.cost_inr?.toLocaleString()} INR</span>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {}
                              {currentTrip.budget_breakdown.savings_suggestions?.length > 0 && (
                                <div className="pt-4 border-t border-slate-100">
                                  <span className="text-xs font-bold text-teal-700 uppercase tracking-widest block mb-2">AI Savings Recommendations</span>
                                  <div className="space-y-2">
                                    {currentTrip.budget_breakdown.savings_suggestions.map((suggestion, idx) => (
                                      <div key={idx} className="p-3 bg-teal-50 border border-teal-100/50 rounded-xl text-xs text-teal-800 leading-relaxed font-semibold">
                                        Savings option: {stripEmojis(suggestion)}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                            </div>
                          ) : (
                            <p className="text-xs text-slate-400 italic">No budget estimates compiled.</p>
                          )}
                        </div>

                      </div>
                    </div>

                    {}
                    <div className="space-y-6 pt-4 border-t border-slate-200">
                      <h3 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
                        <Map className="h-5 w-5 text-slate-700" /> Proposed Daily Route Plan
                      </h3>
                      {currentTrip.itinerary?.days?.length > 0 ? (
                        <div className="space-y-4">
                          {currentTrip.itinerary.days.map((day) => {
                            const isExpanded = expandedDays[day.day] || false;
                            
                            return (
                              <div key={day.day} className="bg-white rounded-2xl border border-slate-200/60 overflow-hidden shadow-sm">
                                
                                {}
                                <div 
                                  onClick={() => toggleDayExpanded(day.day)}
                                  className="p-5 bg-slate-50 flex justify-between items-center cursor-pointer select-none hover:bg-slate-100/50 transition-colors"
                                >
                                  <div>
                                    <h4 className="font-bold text-slate-900 text-base">
                                      Day {day.day} — {day.date}
                                    </h4>
                                    <span className="text-xs text-slate-400 block mt-0.5">Staying: {day.hotel ? stripEmojis(day.hotel) : 'Local Hotel'}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">{day.activities?.length || 0} activities</span>
                                    {isExpanded ? (
                                      <ChevronUp className="h-5 w-5 text-slate-500" />
                                    ) : (
                                      <ChevronDown className="h-5 w-5 text-slate-500" />
                                    )}
                                  </div>
                                </div>

                                {}
                                {isExpanded && (
                                  <div className="p-5 border-t border-slate-100 space-y-4">
                                    <div className="flex flex-wrap gap-4 text-xs font-semibold pb-3 border-b border-slate-100">
                                      <span className="text-slate-500">Meals: {day.meals ? stripEmojis(day.meals) : 'N/A'}</span>
                                    </div>
                                    
                                    {day.notes && (
                                      <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-xl text-xs text-slate-500 font-medium italic">
                                        Note: {stripEmojis(day.notes)}
                                      </div>
                                    )}

                                    <div className="space-y-3 pt-2">
                                      {day.activities?.map((act, actIdx) => (
                                        <div key={actIdx} className="p-4 bg-slate-50 border border-slate-100/50 rounded-xl flex flex-col justify-between md:flex-row md:items-center gap-4">
                                          <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                                {act.time_of_day}
                                              </span>
                                              {currentTrip.children > 0 && act.child_friendly && (
                                                <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-teal-100 text-teal-800">
                                                  Child Friendly
                                                </span>
                                              )}
                                            </div>
                                            <span className="font-bold text-slate-900 block text-sm">{stripEmojis(act.name)}</span>
                                            <p className="text-xs text-slate-500 leading-relaxed font-semibold max-w-[650px]">
                                              {stripEmojis(act.description)}
                                            </p>
                                          </div>
                                          <div className="text-right shrink-0">
                                            <span className="text-xs font-bold text-slate-400 block">
                                              {formatDuration(act.duration_minutes)}
                                            </span>
                                            <strong className="text-slate-900 text-sm block mt-0.5">
                                              {act.cost_inr?.toLocaleString()} INR
                                            </strong>
                                          </div>
                                        </div>
                                      ))}
                                    </div>

                                  </div>
                                )}

                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-400 italic">No routing days calculated.</p>
                      )}
                    </div>
                  </div>
                )}

              </div>
            )}

          </main>
        </div>
      )}

    </div>
  );
}

export default App;
