# Shopify Product Scraper

A Python-based web scraping tool for extracting product information from Shopify stores.

## Requirements

- Python 3.7+
- Beautiful Soup 4
- Requests
- Pandas
- lxml

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shopify-product-scraper.git
   cd shopify-product-scraper
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the scraper:
   ```bash
   python scraper.py
   ```

2. The scraped data will be saved in a CSV file in the `output` directory.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
