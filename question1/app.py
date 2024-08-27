from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Constants
AUTH_URL = "http://20.244.56.144/test/auth"
PRODUCTS_URL_TEMPLATE = (
    "http://20.244.56.144/test/companies/{company}/categories/{category}/products"
)
AUTH_PAYLOAD = {
    "companyName": "GITAM",
    "clientID": "b2bb00b4-bdbf-484d-bdbc-d644b664d2b2",
    "clientSecret": "muFBpCrTztsGBWmK",
    "ownerName": "O.UMA KRISHNA PAVAN",
    "ownerEmail": "umapavan776@gmail.com",
    "rollNo": "VU21CSEN0100224",
}

# Global variable for storing token information
token_info = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzI0NzM1NTEwLCJpYXQiOjE3MjQ3MzUyMTAsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImIyYmIwMGI0LWJkYmYtNDg0ZC1iZGJjLWQ2NDRiNjY0ZDJiMiIsInN1YiI6InVtYXBhdmFuNzc2QGdtYWlsLmNvbSJ9LCJjb21wYW55TmFtZSI6IkdJVEFNIiwiY2xpZW50SUQiOiJiMmJiMDBiNC1iZGJmLTQ4NGQtYmRiYy1kNjQ0YjY2NGQyYjIiLCJjbGllbnRTZWNyZXQiOiJtdUZCcENyVHp0c0dCV21LIiwib3duZXJOYW1lIjoiTy5VTUEgS1JJU0hOQSBQQVZBTiIsIm93bmVyRW1haWwiOiJ1bWFwYXZhbjc3NkBnbWFpbC5jb20iLCJyb2xsTm8iOiJWVTIxQ1NFTjAxMDAyMjQifQ.TCJNitf9MqWzo9zRITxYFLOKCfKSI0Ur5GeZQcfasus",
    "expires_in": 1724735510,
}


def fetch_token():
    """Fetch the access token from the authentication server."""
    response = requests.post(AUTH_URL, json=AUTH_PAYLOAD)
    if response.status_code == 200:
        data = response.json()
        token_info["access_token"] = data["access_token"]
        token_info["expires_in"] = data["expires_in"]
    else:
        raise Exception("Failed to fetch token")


def get_auth_headers():
    """Return headers for authorization. Fetches a new token if necessary."""
    if not token_info["access_token"]:
        fetch_token()
    return {"Authorization": f"Bearer {token_info['access_token']}"}


def fetch_products(company, category, top, min_price, max_price):
    """Fetch products from the e-commerce API."""
    url = PRODUCTS_URL_TEMPLATE.format(company=company, category=category)
    params = {"top": top, "minPrice": min_price, "maxPrice": max_price}
    headers = get_auth_headers()

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


@app.route('/products', methods=['GET'])
def get_products():
    company = request.args.get('company')
    category = request.args.get('category')
    top = request.args.get('top')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')

    if not all([company, category, top, min_price, max_price]):
        return jsonify({"error": "Missing required query parameters"}), 400

    if not token_info["access_token"]:
        get_token()

    headers = {
        "Authorization": f"Bearer {token_info["access_token"]}"
    }
    products_url = PRODUCTS_URL_TEMPLATE.format(company=company, category=category)
    params = {
        "top": top,
        "minPrice": min_price,
        "maxPrice": max_price
    }

    response = requests.get(products_url, headers=headers, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch products"}), response.status_code


@app.route("/categories/<categoryname>/products", methods=["GET"])
def get_products_by_category(categoryname):
    """Endpoint to get products by category with query parameters."""
    company = request.args.get("company")
    top = request.args.get("top")
    min_price = request.args.get("minPrice")
    max_price = request.args.get("maxPrice")

    if not all([company, top, min_price, max_price]):
        return jsonify({"error": "Missing required query parameters"}), 400

    try:
        products = fetch_products(company, categoryname, top, min_price, max_price)
        return jsonify(products)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
