# 🛡️ SIEM NLP Assistant

**Intelligent Security Information and Event Management (SIEM) system with Natural Language Processing capabilities.**

Transform natural language queries into actionable security insights using advanced ML-powered query understanding, retrieval-augmented generation, and real-time SIEM integration.

## 🚀 **Quick Start**

### 1. **Setup Environment**
```bash
# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm
```

### 2. **Start SIEM Stack**
```bash
# Start Elasticsearch + Kibana
cd docker
docker-compose up -d
```

### 3. **Run Applications**
```bash
# Start FastAPI backend
cd backend
python main.py

# Start Streamlit dashboard  
streamlit run ui_dashboard/streamlit_app.py
```

## 🤖 **Core Features**

### **🧠 Enhanced NLP Parser**
- **Machine Learning**: TF-IDF + LogisticRegression for intent classification
- **Confidence Scoring**: Reliability metrics for all predictions
- **Advanced Entities**: IPs, domains, ports, time ranges, security events
- **Smart Fallback**: Graceful degradation to pattern-based parsing

### **🔍 RAG Pipeline**
- **Contextual Understanding**: Retrieval-augmented query generation
- **Vector Search**: FAISS/Elasticsearch dense vector storage
- **Multi-turn Context**: Conversation memory and state management

### **🔌 SIEM Integration**
- **Elasticsearch**: Native query DSL generation and execution
- **Wazuh**: REST API connector for alert management
- **Real-time Search**: Live log analysis and threat detection

### **📊 Response Formatting**
- **Human-readable**: Natural language summaries of findings
- **Visual Charts**: Plotly-based security dashboards
- **Export Options**: JSON, CSV, and formatted reports

- All dependencies use the latest stable versions (no version pinning)
- Use `scripts/update_dependencies.ps1` (Windows) or `scripts/update_dependencies.sh` (Linux/Mac) to update all dependencies
- Check for outdated packages: `python -m pip list --outdated`

## Architecture

The project is organized into several key components:

- **SIEM Connectors**: Interface with different SIEM platforms
- **NLP Parser**: Process natural language queries
- **RAG Pipeline**: Retrieve relevant context for query generation
- **Response Formatter**: Format results for presentation
- **Context Manager**: Maintain conversation state

## License

See LICENSE file for details.
