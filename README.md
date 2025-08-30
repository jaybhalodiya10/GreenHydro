# Green Hydrogen

## Introduction
Green Hydrogen is a toolkit for geospatial analysis of green hydrogen production costs. It helps users estimate the locational cost of producing, storing, transporting, and converting green hydrogen to meet demand in a specified region. The toolkit is designed for flexibility and can be adapted to different countries, regions, and scenarios.

This repository is developed and maintained at: [https://github.com/jaybhalodiya10/GreenHydro](https://github.com/jaybhalodiya10/GreenHydro)

---

## Setting Up the Environment

Follow these steps to set up your environment and get started:

1. **Clone the repository:**
   ```
   git clone https://github.com/jaybhalodiya10/GreenHydro.git
   cd GreenHydro
   ```

2. **Install Mamba (if not already installed):**
   - See [Mamba installation instructions](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)

3. **Create and activate the environment:**
   ```
   mamba env create -f environment.yaml
   mamba activate greenhydrogen
   ```

4. **Install a solver:**
   - The recommended free solver is [Cbc](https://github.com/coin-or/Cbc), which is installed with the environment.
   - For commercial solvers like Gurobi, follow their installation instructions and update the solver setting in `Scripts/optimize_hydrogen_plant.py` if needed.

5. **Set up CDS API key (for weather data):**
   - Register at the [Climate Data Store](https://cds.climate.copernicus.eu/api-how-to) and configure your API key for weather data downloads.

6. **Prepare input data:**
   - Add or update hexagon files and parameter Excel files in the `Data` and `Parameters` folders as needed for your analysis.

---

For more details, see documentation and comments in the code.
