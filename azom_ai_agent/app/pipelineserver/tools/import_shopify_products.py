import csv
import json
import re
import os

# Lista över bilmodeller (kan byggas ut eller hämtas från externt API)
CAR_MODELS = [
    "Volvo", "BMW", "Audi", "Ford", "Toyota", "Mercedes", "Volkswagen", "Skoda", "Opel", "Renault", "Peugeot", "Citroen", "Saab", "Mazda", "Honda", "Hyundai", "Kia", "Nissan", "Mitsubishi", "Suzuki", "Subaru", "Fiat", "Jeep", "Chevrolet", "Dacia", "Seat", "Tesla"
]

# Ange rätt sökväg till din exporterade CSV
CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/products_export.csv')
JSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/products.json')

def extract_compatible_models(text):
    """Försök hitta bilmodeller i text (namn, beskrivning etc)."""
    found = set()
    if not text:
        return []
    for model in CAR_MODELS:
        pattern = r'\\b' + re.escape(model) + r'\\b'
        if re.search(pattern, text, re.IGNORECASE):
            found.add(model)
    return list(found)

def main():
    products = []
    with open(CSV_PATH, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("Title") or row.get("Name")
            description = row.get("Body (HTML)") or row.get("Description") or ""
            price = None
            for price_field in ["Variant Price", "Price", "Price (SEK)"]:
                if row.get(price_field):
                    try:
                        price = float(row[price_field].replace(",", "."))
                        break
                    except Exception:
                        pass
            compatible_models = extract_compatible_models(name + " " + description)
            # Exempel på extrafält: vendor, product_type, tags, sku, barcode
            product = {
                "name": name,
                "description": description,
                "price_sek": price,
                "vendor": row.get("Vendor"),
                "product_type": row.get("Type") or row.get("Product Category"),
                "tags": [t.strip() for t in (row.get("Tags") or "").split(",") if t.strip()],
                "sku": row.get("Variant SKU") or row.get("SKU"),
                "barcode": row.get("Variant Barcode") or row.get("Barcode"),
                "compatible_models": compatible_models,
                # Fält för framtida användning:
                # "success_rate": None,
                # "installation_time": None,
                # "canbus_required": None
            }
            products.append(product)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"{len(products)} produkter exporterade till {JSON_PATH}")
    print("Exempelfält i varje produkt:")
    print(json.dumps(products[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
