# Cars Manufacturing Data Analysis

Exploratory data analysis of the included U.S. car auction dataset. The notebook looks at prices, mileage, brands, years, colors, states, and simple derived fields.

**Source repository:** [pavan9753/Cars_Manufacturing_data_Analysis](https://github.com/pavan9753/Cars_Manufacturing_data_Analysis)

## Run locally

From this directory:

```bash
python -m venv .venv
```

Activate the environment, then install and launch Jupyter:

```bash
python -m pip install -r requirements.txt
python -m jupyter notebook cars.ipynb
```

Run the cells in order. The notebook reads `USA_cars_datasets.csv` from this directory. Some cells export spreadsheet output; `openpyxl` is included for that step.

## Included files

- `cars.ipynb` — analysis notebook.
- `USA_cars_datasets.csv` — source dataset used by the notebook.
