
import logging

from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def parse_due_date(due_date_str, invoice_date=None):
#     try:
#         # Try direct parsing with a known format
#         due_date = datetime.strptime(due_date_str, "%d-%m-%Y").date()
#         logging.info(f"Parsed due date: {due_date}")
#         return due_date
#     except ValueError:
#         logging.warning(f"Direct parsing failed for: {due_date_str}")
#
#     # Check for natural language expressions
#     if 'days from invoice date' in due_date_str.lower() and invoice_date:
#         days_match = re.search(r'(\d+)\s*days', due_date_str.lower())
#         if days_match:
#             days = int(days_match.group(1))
#             due_date = invoice_date + timedelta(days=days)
#             logging.info(f"Calculated due date from invoice date: {due_date}")
#             return due_date
#         else:
#             logging.error("Failed to extract number of days from due date string.")
#             raise ValueError(f"Unable to process due date: {due_date_str}")
#
#     # Fallback to dateparser for dynamic formats
#     due_date = dateparser.parse(due_date_str)
#     if due_date:
#         logging.info(f"Dateparser successfully parsed due date: {due_date}")
#         return due_date.date()
#
#     # If all else fails, raise an error
#     logging.error(f"Failed to parse due date: {due_date_str}")
#     raise ValueError(f"Unsupported due date format: {due_date_str}")
#
# # Example usage
# invoice_date = datetime.strptime("01-01-2025", "%d-%m-%Y").date()  # Example invoice date
# due_date_str = "30 days from invoice date"
#
# try:
#     parsed_date = parse_due_date(due_date_str, invoice_date)
#     print(f"Final due date: {parsed_date}")
# except ValueError as e:
#     print(f"Error processing due date: {e}")


def parse_date(date_text):
    """
    Parses a date from a given text in various formats and returns it in ISO 8601 format (YYYY-MM-DD).
    If parsing fails, returns None.

    Args:
        date_text (str): The input date text to be parsed.

    Returns:
        str or None: The parsed date in ISO 8601 format, or None if parsing fails.
    """
    try:
        # Attempt to parse the date text
        parsed_date = parser.parse(date_text)
        # Format the date to ISO 8601 (YYYY-MM-DD) and return it
        return parsed_date.strftime('%Y-%m-%d')
    except (ValueError, TypeError) as e:
        # If parsing fails, return None
        print(f"Error parsing date: {e}")
        return None