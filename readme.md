# Graphcast 2-m temperature forecast evaluation
## 1. project review
This project aims to evaluate GraphCast forecast which compared with ERA 5 across 1-day, 3-day, 5-day and 7-day in the Southweat British Columbia,2020.
## 2. research question
Main-question:
How does GraphCast’s 2-m temperature error change with lead time (1–7 days)?
Sub-question:
How accurate are the forecasts at each lead time?
How did the forecasts perform during the August 2020 heat event?
## 3. data source
GraphCast and ERA5 from WeatherBench2
Study area is 48.75–51.75°N, 119.25–125.25°W.
Lead times: 1-day, 3-day, 5-day and 7-day.
Variable: 2-m temperature
## 4. methods
The analysis was conducted using Python, xarray, Pandas, NumPy, and matplotlib.
The data processing includes:
Selecting Vancouver area.
Calculating area-weighted average.
Converting temperatures from Kelvin to Celsius.
Aligning GraphCast forecasts with ERA5 by forecast valid time.
Computing slope, bias, error, MAE, RMSE.
Visualizing scatter plots, histogram and dual-axis time-series plot.
## 5. resposibilty files
`extract_graphcast.py`: Data extraction and preprocessing
`my_analysis.ipynb`: Statistical analysis and visualization
`raw_era5_2020.csv`: Extracted ERA5 regional temperatures
`raw_graphcast_2020.csv`: Extracted GraphCast regional forecasts
`vancouver_graphcast_aligned_2020.csv`: Aligned data for analysis
`main_question.jpg`: Scatter plots comparing forecasts with ERA5
`fig2_Sub_question.png`: Forecast error distributions
`fig3_Sub_question.png`: August 2020 temperature and error time series
## 6. reproducibility
1. install the Python dependencies: xarray, pandas, numpy, matplotlib, zarr, gcsfs, and jupyter.
2. Download the repository files.
Open `my_analysis.ipynb` in Jupyter Notebook or VS Code.
Ensure the required CSV files are in the project directory.
Run the notebook cells sequentially to reproduce the analysis and figures.
The GraphCast and ERA5 data are available in WeatherBench2.
https://weatherbench2.readthedocs.io/en/latest/data-guide.html