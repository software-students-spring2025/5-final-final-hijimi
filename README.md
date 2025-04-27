# Smart Shop Recommendation System

An advanced product recommendation system and search engine with real product data and images. The application offers personalized product recommendations for users based on their preferences and past interactions, as well as powerful search functionality.

## Features

- **Advanced Search**: Search for products across multiple fields (name, description, categories, etc.)
- **Category Filtering**: Find products by specific categories
- **Brand Filtering**: Filter products by brand
- **Personalized Recommendations**: Get product recommendations tailored to user preferences
- **Real Product Images**: All products display real images
- **Rating-based Sorting**: Products can be sorted by rating, price, and other attributes
- **Detailed Product Views**: See comprehensive product details including specifications

## Architecture

The system consists of:

- **MongoDB Database**: Contains product data, user profiles, and interaction history
- **FastAPI Backend**: Provides API endpoints for search and recommendations
- **Recommender Engine**: Generates personalized product recommendations
- **Frontend**: Clean, responsive UI for interacting with the system

## Setup and Installation

### Prerequisites

- Docker Desktop
- Docker Compose

### Running the Application

1. **Start Docker Desktop** (on macOS, open the Docker Desktop application)

2. **Clone the repository**:
   ```
   git clone https://github.com/your-repo/smart-shop-recommendation.git
   cd smart-shop-recommendation
   ```

3. **Run with Docker Compose**:
   ```
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:8080
   - API Documentation: http://localhost:8000/docs

### Development Setup

For local development:

1. **Start the database only**:
   ```
   docker-compose up -d mongodb
   ```

2. **Set up Python virtual environment**:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r api/requirements.txt -r recommender/requirements.txt
   ```

3. **Run the API**:
   ```
   MONGO_URI=mongodb://localhost:27017/mydatabase uvicorn api.app:app --reload
   ```

4. **For frontend development**, you can simply open the `frontend/index.html` file in your browser.

## API Endpoints

The system provides the following API endpoints:

- `GET /recommendations/{user_id}`: Get personalized recommendations for a specific user
- `GET /search?q={query}`: Search for products across all fields
- `GET /products`: List all products with filtering and sorting options
- `GET /products/{product_id}`: Get details for a specific product
- `GET /brands`: Get a list of all available brands
- `GET /categories`: Get a list of all available categories

## Data Structure

The MongoDB database contains three collections:

1. **Products**: Product information (name, description, price, categories, brand, etc.)
2. **Users**: User profiles with preference information
3. **Interactions**: Records of user-product interactions (views, purchases, etc.)

## Examples

### Search for Gaming Products

```
GET /search?q=gaming&sort_by=rating
```

### Get Recommendations for User

```
GET /recommendations/user1?brand=Apple
```

### Filter Products by Category and Brand

```
GET /products?category=Laptops&brand=Dell&sort_by=price&sort_order=asc
```

## License

[MIT License](LICENSE)
