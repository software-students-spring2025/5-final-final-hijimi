# E-commerce Recommendation Engine: Personalized Shopping Experiences

## 🌟 Project Vision

Welcome to **SmartShop** - our intelligent e-commerce recommendation engine. In today's overwhelming digital marketplace, consumers face an abundance of choices but lack personalized guidance. SmartShop transforms the shopping experience by understanding customer preferences and behaviors, offering tailored product recommendations that feel like advice from a trusted friend.

Our system doesn't just suggest products; it creates meaningful connections between customers and merchandise they'll truly appreciate. Using advanced machine learning algorithms and behavioral analysis, SmartShop learns from each interaction to continuously improve its recommendations, resulting in higher customer satisfaction and increased sales conversion.

## 👥 Team Members

* [Xingjian Zhang](https://github.com/ScottZXJ123) - System Architect & DevOps Lead
* [Hao Yang](https://github.com/Hao-Yang-Hao) - Database Engineer
* [Shenrui Xue](https://github.com/ShenruiXue666) - Backend Developer
* [Yukun Dong](https://github.com/abccdyk) - Frontend Engineer

## 🏆 Build Status

[![API CI/CD](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/api.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/api.yml)
[![Recommender CI/CD](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/recommender.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/recommender.yml)
[![Frontend CI/CD](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/frontend.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/frontend.yml)
[![MongoDB CI/CD](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/mongodb.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-final-hijimi/actions/workflows/mongodb.yml)

## 🏗️ System Architecture

SmartShop employs a modern microservices architecture that enables scalability, resilience, and continuous deployment:

### 🗄️ MongoDB Database
The foundation of our system, storing rich collections of:
* **Products**: Detailed product information including categories, prices, descriptions, and metadata
* **Users**: Customer profiles containing preferences, demographics, and account information
* **Interactions**: A comprehensive record of user behaviors (views, purchases, ratings, time spent)

### 🧠 Recommendation Engine (Python)
The intelligent core of SmartShop, built with:
* Advanced collaborative filtering algorithms
* Content-based recommendation techniques
* Hybrid approach for cold-start problems
* Real-time preference learning and adaptation

Our engine implements multiple recommendation strategies:
* Category-based recommendations from user preferences
* Similar user recommendations (collaborative filtering)
* Popularity-based recommendations as fallback
* Recency and trend-awareness for seasonal items

### 🔌 API Service (FastAPI)
A high-performance bridge between data and presentation:
* RESTful endpoints for product recommendations
* User preference management
* Analytics endpoints for business insights
* Secure authentication and authorization

### 🖥️ Frontend Interface
An elegant, responsive interface providing:
* Personalized product showcases
* Intuitive browsing experience
* Seamless integration with backend services
* Adaptive design for all devices

## 🐳 Docker Hub Images
All Docker images are hosted on Docker Hub:

- [Frontend](https://hub.docker.com/r/ccdyk/5-final-final-hijimi-frontend)
- [MongoDB](https://hub.docker.com/r/ccdyk/5-final-final-hijimi-mongodb)
- [API](https://hub.docker.com/r/ccdyk/5-final-final-hijimi-api)
- [Recommender](https://hub.docker.com/r/ccdyk/5-final-final-hijimi-recommender)

## 🚀 Setup & Running

### Prerequisites
* [Docker](https://www.docker.com/get-started) (v20.10+)
* [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
* Git

### Clone the Repository
```bash
git clone https://github.com/software-students-spring2025/5-final-final-hijimi.git
cd 5-final-final-hijimi
```

### Configuration
1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Configure the following environment variables in `.env`:
```
# MongoDB Configuration
MONGO_INITDB_DATABASE=mydatabase
# Uncomment and set these for production environments
# MONGO_INITDB_ROOT_USERNAME=admin
# MONGO_INITDB_ROOT_PASSWORD=secure_password

# API Configuration
MONGO_URI=mongodb://mongodb:27017/mydatabase
API_PORT_HOST=8000
API_PORT_CONTAINER=8000

# Frontend Configuration
FRONTEND_PORT_HOST=8080
FRONTEND_PORT_CONTAINER=80
```

### Launch the Application
```bash
docker-compose up -d
```

This command:
1. Builds/pulls all necessary container images
2. Creates a Docker network for inter-service communication
3. Initializes the MongoDB with sample data
4. Starts all services in the correct order

### Access the Application
* **Frontend Interface**: http://localhost:8080
* **API Documentation**: http://localhost:8000/docs
* **API Health Check**: http://localhost:8000/health

### Data Import
The system comes pre-loaded with sample data for demonstration purposes. This data is automatically imported when the MongoDB container starts via the `mongodb/init.sh` script. The sample data includes:
* 40+ products across various categories
* 15 sample user profiles with preferences
* 90+ user interaction records

To reset the database to its initial state:
```bash
docker-compose down -v
docker-compose up -d
```

### Customizing Sample Data
To customize the initial dataset:
1. Modify the `mongodb/init_data.json` file
2. Rebuild the MongoDB container:
```bash
docker-compose build mongodb
docker-compose up -d
```

## 🧪 Development & Testing

### Running Unit Tests
Our codebase maintains >80% test coverage for all components.

Before running tests, ensure that MongoDB is running locally.

If you have Docker installed, you can start a MongoDB instance by running:

```bash
docker run -d --name local-mongo -p 27017:27017 mongo
```

#### API Tests
```bash
cd api
pip install -r requirements.txt
pytest -v --cov=api tests/ --cov-report=xml --cov-report=term
```

#### Recommender Tests
```bash
cd recommender
pip install -r requirements.txt
pytest --cov=recommender tests/ --cov-report=term-missing
```

### Local Development
For active development without rebuilding containers:

1. Setup Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies for both components:
```bash
pip install -r api/requirements.txt -r recommender/requirements.txt
```

3. Run MongoDB container:
```bash
docker-compose up -d mongodb
```

4. Run API with hot-reloading:
```bash
cd api
MONGO_URI=mongodb://localhost:27017/mydatabase uvicorn app:app --reload
```

## 📊 How the Recommendation Engine Works

Our recommendation engine employs a sophisticated multi-strategy approach:

1. **Preference Analysis**: The system analyzes user preferences from explicit (selected categories) and implicit (browsing history) sources.

2. **Collaborative Filtering**: We identify users with similar taste profiles and recommend products that these similar users have enjoyed.

3. **Category-Based Filtering**: Products from preferred categories are suggested, prioritizing high-rated items.

4. **Hybrid Ranking**: Recommendations from different strategies are combined using a weighted approach that balances:
   * Recommendation source (collaborative vs. category)
   * Product popularity and ratings
   * User interaction patterns

5. **Fallback Mechanisms**: For new users with limited history, the system defaults to trend-based and popularity-based recommendations.

6. **Continuous Learning**: With each interaction, the system refines its understanding of user preferences.

## 📝 API Documentation

The API exposes several endpoints for accessing recommendations:

* `GET /recommendations/{user_id}` - Get personalized recommendations for a specific user
* `GET /products` - List all available products
* `GET /products/{product_id}` - Get details for a specific product
* `GET /users/{user_id}/preferences` - Get a user's preferences
* `POST /users/{user_id}/preferences` - Update a user's preferences

For complete API documentation, visit http://localhost:8000/docs when the system is running.

## 📈 Future Enhancements

Our roadmap includes:
* Real-time recommendation updates based on session behavior
* A/B testing framework for recommendation strategies
* Integration with external data sources for trend analysis
* Enhanced personalization using natural language processing
* Mobile application development

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

