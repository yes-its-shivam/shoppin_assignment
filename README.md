# AI Shoppin Assistant

## Comparative Conceptual Map
We analyzed various approaches to building a shopping assistant, comparing:
- **Machine Learning Models**: ML-based recommendation engines that improve with data but require training.
- **LLM-Powered Agents**: Our approach leverages a large language model to interpret queries dynamically, offering greater adaptability.

| Approach                | Pros                                           | Cons                                            |
|-------------------------|-----------------------------------------------|------------------------------------------------|
| Rule-Based Systems      | Simple, deterministic, explainable           | Limited adaptability, high maintenance        |
| Machine Learning Models | Data-driven, improves over time              | Requires extensive training and labeled data  |
| LLMs                    | not flexible and robust, hallucinate         | require more context, or maybe finetuning     |
| LLM-Powered Agents      | Flexible, context-aware, requires no training| Can generate unexpected responses sometimes  |

## Short Written Analysis
Our AI shopping assistant demonstrates strong performance in:
- **Accuracy**: High precision in understanding queries.
- **Efficiency**: Fast response times due to pre-structured tools.
- **User Experience**: Seamless interaction without requiring pre-defined templates.

However, areas for improvement include response consistency and error handling for ambiguous queries.

## Design Decisions
- **Agent Architecture**: Uses Ollama to process queries and map them to predefined tool calls.
- **Tool Selection**: Functions in `tools.py` handle core shopping operations, ensuring modularity and maintainability.
- **LLM Agent**: Defined agent in `agent.py` handle core query parsing, understaning, and robustness.
- **Logging**: Implements JSON-based logging for debugging and analytics.

## Challenges & Improvements
**Challenges Faced:**
1. Handling ambiguous queries requiring contextual understanding.
2. Efficiently mapping natural language to structured tool calls.
3. Ensuring consistent responses across different query formats.

**Improvements Implemented:**
- Optimized regex-based parsing for tool calls.
- Enhanced logging for future usecases and finetunings.

## Open Questions & References
- How can we further improve accuracy for vague queries?
- What can be used to make it more robust, over different runs agent tends to answer incompletely

---
## Installation
```bash
# Clone the repository
git clone https://github.com/yes-its-shivam/shoppin_assignment.git

# Navigate to the project directory
cd shoppin_assignment

# Install dependencies
pip install ollama
python agent.py
```

## Result logs from terminal:
```(base) PS C:\Users\shivam\Desktop\shoppin> python .\agent.py
Shopping Assistant initialized successfully!
user query:  Find a floral skirt under $40 in size S. Is it in stock, and can I apply a discount code ‘SAVE10’?
tool call: [('search_products', {'name': 'floral skirt', 'price_range': 30, 'size': 'S'}), ('check_availability', {'product_id': '<product_id>'}), ('apply_discount', {'base_price': 30, 'promo_code': 'SAVE10'})]
Search_product 'floral skirt' results: [{'id': 1, 'name': 'floral skirt', 'color': 'Pink', 'price': 35, 'size': 'S', 'in_stock': True, 'site': 'SiteA'}] 11111
Assistant: Found: floral skirt in Pink
Price: $35.00
Size: S
Available: Yes
Seller: SiteA
Price after discount:
Original price: $35.00
Discounted price: $31.50
Discount applied: 10.0%

user query:  I need white sneakers (size 8) for under $70 that can arrive by Friday
tool call: [] #clearly something went wrong, maybe need more Cot action here
Assistant: No results found.

user query:  I found a ‘casual denim jacket’ at $80 on SiteA. Any better deals?
tool call:  [('compare_prices', {'product_name': 'casual denim jacket'})]
Assistant: 🔎 Price Comparison:
- SiteA: $80.00
- SiteB: $75.00
- SiteC: $85.00
💰 Best deal: SiteB at **$75.00**!

user query:  I want to buy a cocktail dress from SiteB, but only if returns are hassle-free. Do they accept returns?
tool call:  [('check_return_policy', {'site': 'SiteB'})]
Assistant: Return Policy: Hassle-free returns within 14 days

Goodbye!
