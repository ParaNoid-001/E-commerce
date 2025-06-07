# import logging
# import sys

# def setup_logging():
#     logging.basicConfig(
#         level=logging.INFO,  # Minimum level to log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.StreamHandler(sys.stdout),  # Log to console
#             logging.FileHandler('app.log'),    # Log to a file
#         ]
#     )

# # Call this early in your application startup
# setup_logging()