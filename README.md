
# Food-Delivery Application

## Team Name: $\pi$thon

### Required Python Version

Python 3.10+

### Setup Instructions

Clone the repository:
```bash
git clone <https://github.com/benjamink24/COSC-310-project>

cd project-root

### Virtual-environment Instructions

```bash
python -m venv .venv
.venv\Scripts\activate

### Dependency Installations

pip install -r requirements.txt

### How to start the application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

### API Endpoint Paths

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Checks whether the application is running |
| GET | `/restaurants` | Returns available restaurants |
| GET | `/docs` | Returns documentation |

### /docs Path
Interactive Swagger API documentation is available at:

http://127.0.0.1:8000/docs

### Location of Representative Data

project-root\data\restaurants.json

### How to run Tests

```bash
pytest

### Brief Repository Structure
project-root/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   └── main.py
├── data/
│   └── restaurants.json
├── tests/
├── scrum/
│   └── team-agreement.md
├── .gitignore
├── requirements.txt 
└── README.md