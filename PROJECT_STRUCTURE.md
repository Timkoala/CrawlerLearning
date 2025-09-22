# Project Structure
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py        # Application settings
├── web/
│   ├── __init__.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── jobs.html
│   │   ├── settings.html
│   │   └── results.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── crawler/
│   ├── __init__.py
│   ├── engine.py          # Crawler engine
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── base_spider.py # Base spider class
│   ├── middlewares.py     # Proxy and anti-detection middlewares
│   ├── pipelines.py       # Data processing pipelines
│   └── utils.py           # Utility functions
├── models/
│   ├── __init__.py
│   └── job.py             # Job and result models
└── README.md