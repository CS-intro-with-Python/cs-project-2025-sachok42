# Euler Diagram Visualizer

A full-stack web application for creating, visualizing, and managing Euler diagrams with user authentication and cloud storage.

## Features

- **Interactive Diagram Creation**: Create Euler diagrams with up to 10 sets
- **User Authentication**: Secure login and registration system
- **Save & Load**: Store your diagrams in the cloud and access them anytime
- **Export**: Download diagrams as SVG files
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Visualization**: See your diagram update as you type
- **Smart Labeling**: Automatically displays elements in intersection regions

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

4. **Open your browser** and navigate to:
```
http://localhost:5000
```

## Usage

### Getting Started

1. **Register**: Create a new account at `/register`
2. **Login**: Sign in with your credentials
3. **Create Diagram**: 
   - Enter set names (e.g., "Fruits", "Red Items")
   - Add elements separated by commas (e.g., "apple, banana, orange")
   - Click "Update Diagram" to visualize

### Features Guide

- **Update Diagram**: Regenerates the visualization with current data
- **Save Diagram**: Stores the current diagram to your account
- **Download SVG**: Exports the diagram as an SVG file
- **Load Saved Diagrams**: View and restore previously saved diagrams
- **Zoom & Pan**: Use mouse scroll to zoom, click and drag to pan

### Tips

- You can use 1-10 sets simultaneously
- Each set can contain up to 15 elements
- Elements in multiple sets will appear in intersection regions
- Hover over any region to see details
- Use clear, descriptive names for better organization

## File Structure

```
.
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── database.db            # SQLite database (auto-created)
└── templates/
    ├── index.html         # Main application interface
    ├── login.html         # Login page
    └── register.html      # Registration page
```

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: D3.js, Venn.js
- **Authentication**: Werkzeug password hashing

## Security Notes

⚠️ **Important**: This application uses a development secret key. For production use:

1. Change the `app.secret_key` in `app.py` to a secure random string
2. Use HTTPS
3. Consider using a more robust database (PostgreSQL, MySQL)
4. Add rate limiting and CSRF protection

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password

### Diagrams Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `name`: Diagram name
- `diagram_data`: JSON data of sets and elements
- `thumbnail`: SVG preview (truncated)
- `created_at`: Timestamp

## API Endpoints

- `POST /register`: Create new user account
- `POST /login`: Authenticate user
- `GET /logout`: End user session
- `GET /`: Main application (requires auth)
- `POST /save_diagram`: Save current diagram
- `GET /load_thumbnails`: Get user's saved diagrams
- `GET /load_diagram/<id>`: Load specific diagram
- `DELETE /delete_diagram/<id>`: Delete diagram

## Troubleshooting

**Database errors**: Delete `database.db` and restart the app to recreate tables

**Port already in use**: Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

**Diagram not displaying**: Ensure all JavaScript libraries are loading (check browser console)

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Feel free to submit issues and pull requests.