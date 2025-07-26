"""
AWS Lambda handler for the FastAPI application.
"""
from mangum import Mangum
from api.main import app

# Create the Lambda handler using Mangum
handler = Mangum(app) 