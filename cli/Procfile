web: pip install -r backend/requirements.txt && pip install -e cli/ && python -c "
import subprocess
import threading
import time
import os

def start_backend():
    os.environ['API_HOST'] = '0.0.0.0'
    os.environ['API_PORT'] = '8000'
    os.environ['ENVIRONMENT'] = 'production'
    os.chdir('backend')
    subprocess.run(['python', 'main.py'])

def start_web():
    time.sleep(8)
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import uvicorn

    app = FastAPI(title='SYNRGY - Conversational Assistant')

    @app.get('/', response_class=HTMLResponse)
    def home():
        return '''
        <html><body style=\"background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-family: system-ui; text-align: center; padding: 50px;\">
        <h1 style=\"font-size: 4em;\">SYNRGY - Conversational Assistant</h1>
        <p style=\"font-size: 1.5em;\">AI Powered Security Analysis</p>
        <a href=\"/api/docs\" style=\"background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; display: inline-block; margin: 20px;\">API Docs</a>
        <a href=\"/health\" style=\"background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; display: inline-block; margin: 20px;\">Health</a>
        </body></html>
        '''
    
    @app.get('/health')
    def health():
        return {'status': 'healthy', 'platform': 'heroku'}
    
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)

backend_thread = threading.Thread(target=start_backend, daemon=True)
backend_thread.start()
start_web()
"
