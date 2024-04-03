import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()
    
PORT = int(os.getenv('PORT', 8000))
HOST = '0.0.0.0'

if __name__ == "__main__":
    uvicorn.run('api.app:app', host=HOST, port=PORT, reload=True)