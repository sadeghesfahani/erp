create_function_schema = {
  "name": "create_invoice_from_json",
  "description": "Creates an invoice in Tryton using client and line item details",
  "parameters": {
    "type": "object",
    "properties": {
      "client_id": {
        "type": "integer",
        "description": "The ID of the client (party) in Tryton"
      },
      "currency": {
        "type": "string",
        "description": "The 3-letter currency code, e.g., 'EUR', 'USD'"
      },
      "items": {
        "type": "array",
        "description": "List of invoice items",
        "items": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "integer",
              "description": "The product ID from Tryton"
            },
            "quantity": {
              "type": "number",
              "description": "The quantity of the product"
            },
            "price": {
              "type": "number",
              "description": "The unit price of the product"
            }
          },
          "required": ["product_id", "quantity", "price"]
        }
      }
    },
    "required": ["client_id", "currency", "items"]
  }
}

create_function_example = {
  "client_id": 5,
  "currency": "EUR",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 100.0
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 49.99
    }
  ]
}



def call_functions(functions):
    for function in functions:
        function()

agent_description="""
You are responsible to determine the intention of the user, based on user explanations you should first choose between the following options:
1- invoice
2- expenses
3- assets
4- wiki
5- jobs
6- houses
7- ask for more information

and after you determined the intent of the message, you need to provide the agent with summered and important information with an appropriate format based on what user gave you. if the requirements are not met, you need to ask the user back and forth till you complete all the necessary information and fields. the way you can communicate with the user is by calling the "ask for more information" function.
"""

text_invoice="""
this function start another session with Open AI related to the field of accounting->invoices which contains CROD on invoices and invoice items. furthure instruction will be provided to that a specific agent.
"""