# Financial Products App

This Django app manages financial products data such as deposits, savings, and loans.

## Setup Instructions

1. Install required packages:

```bash
pip install -r requirements.txt
```

2. Configure the API key:

Create or edit the `.env` file in the `backend/final_pjt` directory and add:

```
FINANCIAL_API_KEY=your_api_key_here
```

To obtain an API key, register at [금융감독원 금융상품통합비교공시 오픈API](https://finlife.fss.or.kr/finlife/api/apiGuide/guideApi.do)

3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Loading Data

### Sample Data (for testing)

To load sample data without requiring an API key:

```bash
python manage.py load_sample_products
```

### Real Data

To fetch real financial product data from the API:

```bash
python manage.py update_financial_products --type all
```

Options for the `--type` parameter:
- `deposit`: Fetch only deposit products
- `saving`: Fetch only saving products
- `mortgage`: Fetch only mortgage loan products
- `credit`: Fetch only credit loan products
- `all`: Fetch all types of products (default)

You need a valid API key configured in your `.env` file for this to work.

## API Endpoints

### Product Listings
- `GET /products/financial-products/`: List all financial products
- `GET /products/deposits/`: List all deposit products
- `GET /products/savings/`: List all saving products
- `GET /products/loans/`: List all loan products

### Detail Views
- `GET /products/financial-products/{id}/`: Get details of a specific financial product
- `GET /products/deposits/{id}/`: Get details of a specific deposit product
- `GET /products/savings/{id}/`: Get details of a specific saving product
- `GET /products/loans/{id}/`: Get details of a specific loan product

### Search and Filtering
- `GET /products/search/?q={query}`: Search across all product types
- `GET /products/top-rates/{type}/`: Get top interest rate products (type: deposit or saving)
- `GET /products/lowest-rate-loans/`: Get loan products with the lowest interest rates

### User Favorites
- `GET /products/user/favorites/`: Get user's favorite products (requires authentication)
- `POST /products/user/favorites/{id}/add/`: Add product to favorites (requires authentication)
- `DELETE /products/user/favorites/{id}/remove/`: Remove product from favorites (requires authentication)

### Admin Operations
- `POST /products/admin/update-all/`: Update all financial products (requires admin)
- `POST /products/admin/update-deposits/`: Update deposit products (requires admin)
- `POST /products/admin/update-savings/`: Update saving products (requires admin)
- `POST /products/admin/update-mortgage-loans/`: Update mortgage loan products (requires admin)
- `POST /products/admin/update-credit-loans/`: Update credit loan products (requires admin)
