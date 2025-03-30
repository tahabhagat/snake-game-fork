# Snake Game with Leaderboard - [Play](https://slitherbite.lockhart.in)

A classic snake game with a competitive twist! Climb the ranks and compete with others in real-time.

## Features
- Play the classic snake game with a modern twist
- Compete with others in real-time on the global leaderboard
- Track your personal best scores and strive to beat them
- Responsive design that works on both desktop and mobile
- Real-time score updates and leaderboard rankings

## Tech Stack
### Frontend
- Vue.js 3
- Vite
- Axios for API communication
- Modern UI with responsive design

### Backend
- Flask (Python)
- SQLAlchemy for database management
- CORS support for cross-origin requests
- Production-ready with Gunicorn and Gevent

## Development Setup

### Frontend
```bash
cd frontend
npm install
npm run dev  # for development
npm run build  # for production build
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # for development
```

## Deployment

### Docker Deployment
The backend service can be deployed using Docker. Here's a sample docker-compose configuration:

```yaml
services:
  snake-game-score-service:
    container_name: snake-game-score-service
    image: ghcr.io/lockhart07/snake-game:latest
    pull_policy: always
    tty: true
    stdin_open: true
    ports:
      - "8000:8000"
    volumes:
      - /mnt/snake-game:/data
    healthcheck:
      test: ["CMD", "python3", "-c", "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', 8000)); s.close()"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
```

To deploy using Docker:
1. Create a directory for persistent data: `mkdir -p /mnt/snake-game`
2. Run the service: `docker-compose up -d`

The service will be available at `http://localhost:8000` and includes:
- Automatic container health checks
- Persistent data storage
- Automatic image updates with `pull_policy: always`

### GitHub Pages Deployment
The frontend is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment process is handled by GitHub Actions.

## License
This project is licensed under the terms of the MIT License - see the [LICENSE](LICENSE) file for details.
