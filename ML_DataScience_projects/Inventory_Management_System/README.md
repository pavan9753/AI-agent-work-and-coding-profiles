# Inventory Management System

Interactive Jupyter notebooks for adding products, updating stock, and simulating purchases with JSON-backed inventory and sales records.

**Source repository:** [pavan9753/Inventory_Management_System](https://github.com/pavan9753/Inventory_Management_System)

## Run locally

From this directory:

```bash
python -m venv .venv
```

Activate the environment, then install and start Jupyter:

```bash
python -m pip install -r requirements.txt
python -m jupyter notebook
```

Open `Adding_Products.ipynb` or `Purchasing_Product.ipynb` and run the cells in order. Keep `records.json` and `sales.json` in this directory; the notebooks read these relative paths. The purchasing notebook uses interactive `input()` prompts, so run it in Jupyter or another notebook environment.

## Included files

- `Adding_Products.ipynb` — add product records and adjust inventory quantities.
- `Purchasing_Product.ipynb` — browse products, add items to a cart, and record demo purchases.
- `records.json`, `sales.json` — sample inventory and sales data.

These notebooks are an educational file-based demo. They are not a transactional or multi-user inventory service.
