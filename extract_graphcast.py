# %% Step 0: Settings
import xarray as xr, pandas as pd, numpy as np

TEST = False    
RES = '240x121_equiangular_with_poles_conservative'
ERA5_PATH = f'gs://weatherbench2/datasets/era5/1959-2023_01_10-6h-{RES}.zarr'
GC_PATH   = f'gs://weatherbench2/datasets/graphcast/2020/date_range_2019-11-16_2021-02-01_12_hours-{RES}.zarr'

LEADS = [1, 3, 5, 7]          

LAT_MIN, LAT_MAX = 48.0, 51.0
LON_MIN, LON_MAX = 360 - 125.0, 360 - 120.0

def region_mean(da):
    lat = da.latitude.values
    lon = da.longitude.values
    lats = lat[(lat >= LAT_MIN) & (lat <= LAT_MAX)]
    lons = lon[(lon >= LON_MIN) & (lon <= LON_MAX)]
    box = da.sel(latitude=lats, longitude=lons)
    w = np.cos(np.deg2rad(box.latitude))     
    return box.weighted(w).mean(['latitude', 'longitude']), lats, lons

if TEST:
    INIT_START, INIT_END = '2020-08-01', '2020-08-31 12:00'
    OBS_START,  OBS_END  = '2020-08-01', '2020-09-10'
    STUDY = slice('2020-08-01', '2020-09-10')
    TAG = 'test'
else:
    INIT_START, INIT_END = '2019-12-24', '2020-12-31 12:00'
    OBS_START,  OBS_END  = '2019-12-31', '2021-01-10'
    STUDY = slice('2020-01-01', '2020-12-31 12:00')
    TAG = '2020'


S = {'token': 'anon'}

era5 = xr.open_zarr(ERA5_PATH, storage_options=S, decode_timedelta=True)
gc   = xr.open_zarr(GC_PATH, storage_options=S, decode_timedelta=True)
print('GraphCast init time range:', gc.time.min().values, '~', gc.time.max().values)
print('Has 2m_temperature:', '2m_temperature' in gc.data_vars)

avail = pd.to_timedelta(gc.prediction_timedelta.values)
print('Lead time dtype:', gc.prediction_timedelta.dtype, '| available lead times (days):', [x / pd.Timedelta(days=1) for x in avail])
missing = [d for d in LEADS if pd.Timedelta(days=d) not in avail]
if missing:
    raise SystemExit(f'These lead times (days) are not in the dataset: {missing}. Edit LEADS in Step 0.')

obs_box, lats_e, lons_e = region_mean(era5['2m_temperature'].sel(time=slice(OBS_START, OBS_END)))
obs = obs_box.load() - 273.15
print('ERA5 region: lat', [float(x) for x in sorted(lats_e)], 'lon', [float(x) for x in sorted(lons_e)],
      '->', len(lats_e) * len(lons_e), 'grid cells')
obs.to_series().rename('ERA5_obs').to_csv(f'raw_era5_{TAG}.csv')

raw = {}
for d in LEADS:
    f_da = gc['2m_temperature'].sel(time=slice(INIT_START, INIT_END),
                                    prediction_timedelta=pd.Timedelta(days=d))   # pick the lead time first, then average over the region
    f_box, lats_g, lons_g = region_mean(f_da)
    raw[f'GraphCast_{d}day'] = (f_box.load() - 273.15).to_series()
print('GraphCast region: lat', [float(x) for x in sorted(lats_g)], 'lon', [float(x) for x in sorted(lons_g)],
      '->', len(lats_g) * len(lons_g), 'grid cells')
pd.DataFrame(raw).rename_axis('init_time').to_csv(f'raw_graphcast_{TAG}.csv')
print('Raw data saved')


obs = pd.read_csv(f'raw_era5_{TAG}.csv', index_col=0, parse_dates=True)['ERA5_obs']
raw = pd.read_csv(f'raw_graphcast_{TAG}.csv', index_col='init_time', parse_dates=True)

cols = {}
for d in LEADS:
    s = raw[f'GraphCast_{d}day'].copy()
    s.index = s.index + pd.Timedelta(days=d)        # key step: convert init time to valid time
    cols[f'GraphCast_{d}day'] = s

df = pd.DataFrame(cols)
df.insert(0, 'ERA5_obs', obs)
df = df.dropna().loc[STUDY]
df.index.name = 'valid_time'
df.to_csv(f'vancouver_graphcast_aligned_{TAG}.csv')
print('Aligned data saved:', df.shape)
print(df.head())



for d in LEADS:
    c = f'GraphCast_{d}day'
    sh = {k: round((df[c] - df['ERA5_obs'].shift(-2 * k)).abs().mean(), 2) for k in (-1, 0, 1)}
    pers = (df['ERA5_obs'] - df['ERA5_obs'].shift(2 * d)).abs().mean()
    print(f'{d}-day lead | MAE at shift -1/0/+1 day: {sh} | persistence baseline: {pers:.2f}')
