import ollama

from datetime import datetime, timedelta
import re
import tools

SYSTEM_PROMPT = """
You are a highly skilled virtual AI shopping assistant. You MUST respond **ONLY** using the tool call format provided below. **Do not** add any explanations, extra text, or assumptions.

## Available Tool Calls:

1. **Product Search**  
   Find products based on name, price range, and size.  
   **Format:**  
   TOOL: search_products PARAMS: name="<product_name>", price_range=<number>, size="<size>"

2. **Shipping Estimates**  
   Get estimated shipping costs and delivery details.  
   **Format:**  
   TOOL: estimate_shipping PARAMS: product_name="<name>", location="<location>", delivery_date="<YYYY-MM-DD>"

3. **Apply Discounts**  
   Calculate the final price after applying a promo code.  
   **Format:**  
   TOOL: apply_discount PARAMS: base_price=<number>, promo_code="<code>"

4. **Price Comparison**  
   Compare prices for a product across different sites.  
   **Format:**  
   TOOL: compare_prices PARAMS: product_name="<name>"

5. **Return Policy Lookup**  
   Retrieve the return policy for a specific shopping site.  
   **Format:**  
   TOOL: check_return_policy PARAMS: site="<site_name>"

## Example Valid Responses:

- TOOL: search_products PARAMS: name="floral skirt", price_range=40, size="S"
- TOOL: apply_discount PARAMS: base_price=35, promo_code="SAVE10"

## IMPORTANT RULES:
1. **Understand user queries** and accurately map them to tool calls.  
2. **Use one or more tools** as needed to generate a response.  
3. **Do NOT make up any information**—only use available tool calls.  

"""


def initialize_ollama():
    """Initialize Ollama with better error handling"""
    try:
        ollama.pull('llama3.2')
        print("Shopping Assistant initialized successfully!")
    except Exception as e:
        print(f"Error initializing Ollama: {str(e)}")
        raise

def parse_tool_calls(response):
    """Extract tool calls and add missing compare_prices when necessary."""
    tool_calls = []
    pattern = r'TOOL:\s*(\w+)\s*PARAMS:\s*((?:[a-zA-Z_]\w*=(?:"[^"]*"|\'[^\']*\'|\d+(?:\.\d+)?)\s*,?\s*)*)'

    try:
        matches = re.finditer(pattern, response)
        seen_tools = set()
        product_name = None  
        
        for match in matches:
            tool_name = match.group(1)
            params_str = match.group(2)

            if tool_name in seen_tools:
                continue
            seen_tools.add(tool_name)

            params = {}
            param_pattern = r'([a-zA-Z_]\w*)=("[^"]*"|\'[^\']*\'|\d+(?:\.\d+)?)'
            for param_match in re.finditer(param_pattern, params_str):
                key = param_match.group(1)
                value = param_match.group(2)

                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                elif value.replace(".", "").isdigit():
                    value = float(value) if "." in value else int(value)

                params[key] = value

            if params:
                tool_calls.append((tool_name, params))

                if tool_name == "search_products" and "name" in params:
                    product_name = params["name"]

        # if product_name and "compare_prices" not in seen_tools:
        #     tool_calls.append(("compare_prices", {"product_name": product_name}))

    except Exception as e:
        print(f"Error parsing tool calls: {str(e)}")
        return []

    return tool_calls

def execute_tools(tool_calls, context=None):
    """Execute tools with better context management and error handling"""
    results = {}
    context = context or {}
    
    for tool_name, params in tool_calls:
        try:
            if not hasattr(tools, tool_name):
                results[tool_name] = f"Error: Tool '{tool_name}' not found."
                continue
                
            tool_func = getattr(tools, tool_name)
            
            if tool_name == "apply_discount" and "product_price" in context:
                params["base_price"] = context["product_price"]
            
            elif tool_name == "estimate_shipping":
                if "delivery_date" in params:
                    delivery_date = datetime.strptime(params["delivery_date"], "%Y-%m-%d")
                    if delivery_date < datetime.now():
                        delivery_date = datetime.now() + timedelta(days=7)
                        params["delivery_date"] = delivery_date.strftime("%Y-%m-%d")
            
            result = tool_func(**params)
            
            if tool_name == "search_products" and result:
                context["product_price"] = result[0]["price"]
                context["product_site"] = result[0]["site"]
            
            results[tool_name] = result
            
        except Exception as e:
            results[tool_name] = f"Error executing {tool_name}: {str(e)}"
    
    return results

def generate_final_response(tool_results):
    """Generate user-friendly response with proper formatting"""
    response = []
    
    if "search_products" in tool_results:
        products = tool_results["search_products"]
        if products:
            for product in products:
                response.append(f"Found: {product['name']} in {product['color']}")
                response.append(f"Price: ${product['price']:.2f}")
                response.append(f"Size: {product['size']}")
                response.append(f"Available: {'Yes' if product['in_stock'] else 'No'}")
                response.append(f"Seller: {product['site']}\n")
        else:
            response.append("No products found matching your criteria.\n")
    
    if "estimate_shipping" in tool_results:
        shipping = tool_results["estimate_shipping"]
        if isinstance(shipping, dict) and not isinstance(shipping.get('error'), str):
            response.append("Shipping estimate:")
            response.append(f"Cost: ${shipping.get('cost', 'N/A'):.2f}")
            response.append(f"Delivery by: {shipping.get('estimated_delivery', 'N/A')}")
            response.append(f"Delivery feasible: {'Yes' if shipping.get('feasible') else 'No'}\n")
        elif isinstance(shipping, dict) and shipping.get('error'):
            response.append(f"Shipping error: {shipping['error']}\n")
    
    if "apply_discount" in tool_results:
        discount = tool_results["apply_discount"]
        if isinstance(discount, dict):
            response.append("Price after discount:")
            response.append(f"Original price: ${discount.get('original_price', 'N/A'):.2f}")
            response.append(f"Discounted price: ${discount.get('discounted_price', 'N/A'):.2f}")
            response.append(f"Discount applied: {discount.get('discount_applied', 'N/A')}%\n")
    

    if "check_return_policy" in tool_results:
        policy = tool_results["check_return_policy"]
        if isinstance(policy, str):  # 
            response.append(f"Return Policy: {policy}")
        elif isinstance(policy, dict) and "policy" in policy:
            response.append(f"Return Policy: {policy['policy']}")
        else:
            response.append("No return policy information found.")


    if "compare_prices" in tool_results:
        price_data = tool_results["compare_prices"]
        if isinstance(price_data, dict) and price_data:
            response.append("🔎 Price Comparison:")
            best_site, best_price = min(price_data.items(), key=lambda x: x[1])  # Find the lowest price
            for site, price in price_data.items():
                response.append(f"- {site}: ${price:.2f}")
            response.append(f"\n💰 Best deal: {best_site} at **${best_price:.2f}**!\n")
        else:
            response.append("No price comparison data available.\n")

    return "\n".join(response) if response else "No results found."


import time
def run_agent():
    """Main function with improved error handling and user interaction"""
    try:
        initialize_ollama()
        context = {}
        
        while True:
            try:
                # user_query = input("You: ").strip()
                for user_query in ["Find a floral skirt under $40 in size S. Is it in stock, and can I apply a discount code ‘SAVE10’?",
                                "I need white sneakers (size 8) for under $70 that can arrive by Friday",
                                "I found a ‘casual denim jacket’ at $80 on SiteA. Any better deals?",
                                "I want to buy a cocktail dress from SiteB, but only if returns are hassle-free. Do they accept returns?"]:
                    print("user query: ",user_query)
                    if not user_query:
                        print("Please enter a query.")
                        continue
                        
                    if user_query.lower() in ["exit", "quit"]:
                        print("Thank you for shopping with us. Goodbye!")
                        break
                    
                    response = ollama.generate(
                        model='llama3.2',
                        prompt=f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}",
                    )
                    
                    # Process tools
                    tool_calls = parse_tool_calls(response['response'])
                    if not tool_calls:
                        print("I couldn't understand how to process that request. Could you rephrase it?")
                        continue
                        
                    tool_results = execute_tools(tool_calls, context)
                    final_response = generate_final_response(tool_results)
                    
                    print(f"Assistant: {final_response}")
                    time.sleep(3)
                time.sleep(10)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error processing request: {str(e)}")
                print("Please try again with a different query.")
                
    except Exception as e:
        print(f"Critical error: {str(e)}")
        print("Unable to initialize the shopping assistant. Please check your setup and try again.")

if __name__ == "__main__":
    run_agent()


