# Weather Forecast

In this repo I will develop a Weather Forecast set of tools.

spider.py is (my first) spider which crawls over the Aemet observation stations and downloads all the available data.

Other scripts to visualize are being developed.


## Dependencies
pandas package is used to handle the data and save/load to/from files taking care of repetitions, nans... the pandas package can be simply installed as

```
sudo apt-get install python3-pandas
```

## TO-DO
- [ ] log level should go to config.ini
- [ ] parser/header in the functions should be self-contained
- [X] Clean the repository of old/useless scripts
- [X] Use pandas in the plotting scripts
