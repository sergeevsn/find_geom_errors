## find_geom_error.py

Finds geometry assignment errors in SEG-Y shot gathers.
Based on simple assumption that the maximum trace energy is on 
the receiver closest to the source. At the same time, there must be 
the smallest offset. If not, we have geometry error. 

At least FFID and OFFSET must be present in trace headers.

SEG-Y File name must be provided in command line
Results text file is set below in parameters


Uses SegyIO for file reading https://github.com/equinor/segyio

tqdm for progress https://github.com/tqdm/tqdm

### Install
```bash
git clone https://github.com/sergeevsn/find_geom_errors.git
cd find_geom_errors
python -m venv .venv
pip install -r requirements.txt
```

### Test run
```bash
python3 find_geomerty_error.py test.sgy
```
