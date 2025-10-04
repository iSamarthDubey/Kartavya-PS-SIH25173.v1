# 🚀 SIEM NLP Assistant - Quick Start Guide

## 🎯 How to Run the Complete Application

### Option 1: 🚀 **EASIEST WAY - Use the Launcher Script**

```bash
# From the project root directory
python run_siem_app.py
```

This script will:
- ✅ Check all prerequisites 
- ✅ Test NLP components
- ✅ Start infrastructure (Elasticsearch + Kibana)
- ✅ Start backend API
- ✅ Start frontend UI
- ✅ Open your browser automatically

---

### Option 2: 🔧 **Manual Step-by-Step**

#### Step 1: Start Infrastructure
```bash
cd docker
docker-compose up -d elasticsearch kibana
```
Wait 2-3 minutes for Elasticsearch to start.

#### Step 2: Start Backend API
```bash
cd ../backend
python test_and_run.py
# Choose "Y" when prompted to start the server
```
Backend will be available at: http://localhost:8000

#### Step 3: Start Frontend UI
```bash
cd ../ui_dashboard
streamlit run streamlit_app.py --server.port 8501
```
Frontend will be available at: http://localhost:8501

---

### Option 3: 🧪 **Test Components Only**

```bash
cd backend
python test_and_run.py
# Choose "N" to just test without starting server
```

---

## 🌐 Access Points

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8501 | Main UI for queries |
| **Backend API** | http://localhost:8000/docs | API documentation |
| **Health Check** | http://localhost:8000/health | System status |
| **Elasticsearch** | http://localhost:9200 | Raw data access |
| **Kibana** | http://localhost:5601 | Data visualization |

---

## 🧪 Test Queries

Try these natural language queries in the frontend:

```
Show failed login attempts from last hour
Find security alerts with high severity  
Get network traffic on port 443
Show malware detections from yesterday
List successful logins for admin users
Find system errors from specific server
Display user activity for suspicious accounts
```

---

## 🔧 Troubleshooting

### Port Conflicts
If you get port errors:
```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501
netstat -tulpn | grep :9200

# Kill processes if needed
kill -9 <PID>
```

### Docker Issues
```bash
# Stop all containers
docker-compose down

# Clean up
docker system prune -f

# Restart
docker-compose up -d
```

### Python Import Errors
```bash
# Install missing packages
cd backend
pip install -r requirements.txt

# Or install Streamlit
pip install streamlit
```

---

## 🛑 How to Stop Everything

1. **Stop frontend**: Press `Ctrl+C` in the Streamlit terminal
2. **Stop backend**: Press `Ctrl+C` in the backend terminal  
3. **Stop infrastructure**: 
   ```bash
   cd docker
   docker-compose down
   ```

---

## 🎉 Quick Demo Flow

1. **Start the app**: `python run_siem_app.py`
2. **Open frontend**: http://localhost:8501
3. **Try a query**: "Show failed login attempts"
4. **View results**: See tables, charts, and recommendations
5. **Check API**: http://localhost:8000/docs for technical details

---

## 📱 Features You Can Test

- ✅ **Natural Language Processing**: Convert English to SIEM queries
- ✅ **Entity Extraction**: Automatically find IPs, usernames, time ranges
- ✅ **Intent Classification**: Understand what type of security query you want
- ✅ **Data Visualization**: Auto-generate charts based on query type
- ✅ **Smart Recommendations**: Get actionable security insights
- ✅ **Mock Data**: Works even without real SIEM connection
- ✅ **RESTful API**: Integration-ready backend

---

**🏆 Your SIEM NLP Assistant is ready for SIH 2025 demo!**