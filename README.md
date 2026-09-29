# PriceScout — Product Comparison & Analytics

A Streamlit product-comparison interface built around the supplied
`Web_Scraping_Product_Price_Dataset.xlsx`.

## Features
- Product search by name, category, or store
- Filters for category, store, availability, price, rating, and discount
- Product-card and table views
- Store/product comparison
- Interactive price, rating, category, and discount charts
- Direct product links from the dataset
- Download filtered results as CSV

## Run in VS Code / terminal

```bash
pip install -r requirements.txt
streamlit run app.py
```

The Excel dataset is already included in this folder, so no upload step is
required for the supplied data.

## Dataset used
The workbook contains the `Product_Data` sheet with 1,000 product records
and 12 columns, including product name, category, price, rating,
availability, store, product link, reviews, original price, and discount.
