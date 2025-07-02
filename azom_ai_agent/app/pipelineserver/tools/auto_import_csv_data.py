import os
import csv
import json
import re
from collections import defaultdict

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Bilmodell-lista för automatisk extraktion
CAR_MODELS = [
    "Volvo", "BMW", "Audi", "Ford", "Toyota", "Mercedes", "Volkswagen", "Skoda", "Opel", "Renault", "Peugeot", "Citroen", "Saab", "Mazda", "Honda", "Hyundai", "Kia", "Nissan", "Mitsubishi", "Suzuki", "Subaru", "Fiat", "Jeep", "Chevrolet", "Dacia", "Seat", "Tesla"
]

def extract_compatible_models(text):
    found = set()
    if not text:
        return []
    for model in CAR_MODELS:
        pattern = r'\\b' + re.escape(model) + r'\\b'
        if re.search(pattern, text, re.IGNORECASE):
            found.add(model)
    return list(found)

def guess_type_and_import(filename, rows):
    lower_keys = [k.lower() for k in rows[0].keys()]
    # Produktdata
    if "title" in lower_keys or "name" in lower_keys:
        products = []
        for row in rows:
            name = str(row.get("Title") or row.get("Name") or "")
            description = str(row.get("Body (HTML)") or row.get("Description") or "")
            if not name.strip() and not description.strip():
                continue  # hoppa över rader utan namn och beskrivning
            price = None
            for price_field in ["Variant Price", "Price", "Price (SEK)"]:
                if row.get(price_field):
                    try:
                        price = float(row[price_field].replace(",", "."))
                        break
                    except Exception:
                        pass
            compatible_models = extract_compatible_models(name + " " + description)
            product = {
                "name": name,
                "description": description,
                "price_sek": price,
                "vendor": row.get("Vendor"),
                "product_type": row.get("Type") or row.get("Product Category"),
                "tags": [t.strip() for t in (row.get("Tags") or "").split(",") if t.strip()],
                "sku": row.get("Variant SKU") or row.get("SKU"),
                "barcode": row.get("Variant Barcode") or row.get("Barcode"),
                "compatible_models": compatible_models
            }
            products.append(product)
        return ("products.json", products)
    # Felsökning
    if "issue" in lower_keys or "steps" in lower_keys or "problem" in lower_keys:
        troubleshooting = []
        for row in rows:
            troubleshooting.append({
                "model": row.get("Model") or row.get("Bilmodell"),
                "issue_keywords": [k.strip() for k in (row.get("Issue Keywords") or row.get("Problem") or "").split(",") if k.strip()],
                "steps": [s.strip() for s in (row.get("Steps") or row.get("Åtgärd") or "").split(";") if s.strip()]
            })
        return ("troubleshooting.json", troubleshooting)
    # FAQ/support
    if "question" in lower_keys or "faq" in lower_keys:
        faqs = []
        for row in rows:
            faqs.append({
                "question": row.get("Question") or row.get("FAQ"),
                "answer": row.get("Answer") or row.get("Svar")
            })
        return ("faq.json", faqs)
    # Lagerstatus
    if "stock" in lower_keys or "lager" in lower_keys or "inventory" in lower_keys:
        stock = []
        for row in rows:
            stock.append({
                "sku": row.get("SKU"),
                "stock": row.get("Stock") or row.get("Lager") or row.get("Inventory"),
                "location": row.get("Location")
            })
        return ("stock.json", stock)
    # Recensioner
    if "review" in lower_keys or "rating" in lower_keys:
        reviews = []
        for row in rows:
            reviews.append({
                "product": row.get("Product") or row.get("Produkt"),
                "review": row.get("Review") or row.get("Recension"),
                "rating": row.get("Rating") or row.get("Betyg")
            })
        return ("reviews.json", reviews)
    # Okänd typ – spara som "other_<filename>.json"
    return (f"other_{os.path.splitext(os.path.basename(filename))[0]}.json", rows)

def main():
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    for csv_file in csv_files:
        path = os.path.join(DATA_DIR, csv_file)
        with open(path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print(f"{csv_file}: Ingen data.")
                continue
            json_name, data = guess_type_and_import(csv_file, rows)
            json_path = os.path.join(DATA_DIR, json_name)
            # Om det är lager, koppla till produkter via SKU om möjligt
            if json_name == "stock.json":
                prod_path = os.path.join(DATA_DIR, "products.json")
                if os.path.exists(prod_path):
                    with open(prod_path, encoding="utf-8") as pf:
                        products = json.load(pf)
                    stock_dict = {s['sku']: s for s in data if s.get('sku')}
                    for p in products:
                        if p.get('sku') and p['sku'] in stock_dict:
                            p['stock'] = stock_dict[p['sku']]['stock']
                    with open(prod_path, "w", encoding="utf-8") as pf:
                        json.dump(products, pf, ensure_ascii=False, indent=2)
                    print(f"Lagerstatus kopplad till produkter via SKU.")
            # Spara JSON
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)
            print(f"{csv_file} -> {json_name} ({len(data)} rader)")

if __name__ == "__main__":
    main()
