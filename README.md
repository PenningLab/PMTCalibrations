# PMTCalibrations

## Connencting to LabPC:

ssh lzer@129.64.54.228

## Running Jupyter notebook remotely:

Choose open port on remote machine (remote_port)
Choose open port on local machine (local_port)

- On remote Host:

`user@remote_host$ jupyter notebook --no-browser --port=[remote_port] [notebookname]`

example terminal output (with remote_port=8889): 
```
[I 17:10:01.321 NotebookApp] JupyterLab beta preview extension loaded from /home/lzer/anaconda3/lib/python3.6/site-packages/jupyterlab
[I 17:10:01.321 NotebookApp] JupyterLab application directory is /home/lzer/anaconda3/share/jupyter/lab
[I 17:10:01.381 NotebookApp] Serving notebooks from local directory: /data/share/binlk
[I 17:10:01.382 NotebookApp] 0 active kernels
[I 17:10:01.382 NotebookApp] The Jupyter Notebook is running at:
[I 17:10:01.382 NotebookApp] http://localhost:8889/?token=ac5337b51a13939643efb646c3410831b83edf0260c10ef3
[I 17:10:01.382 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 17:10:01.382 NotebookApp]
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://localhost:8889/?token=ac5337b51a13939643efb646c3410831b83edf0260c10ef3
```

Copy the token

- On local Host:

local_user@local_host$ ssh -N <-f> -L localhost:[local_port]:localhost:[remote_port] user@remote_host

*Optional `-f` argument sends ssh tunnel process to background*

- In browser:

Go to `localhost:[local_port]`

  - Enter token


## Reading out DDC10 .bin file

Use scripts in `binaries/BinFlieReader2lk.py`

#### Read event into array

Due to size of array required to read in all data (in most cases) plots are made on event by event basis

`BinFileReader.ReadBinFile([filename],[number\_of\_channels],[event#])`

#### Convert .bin file to .txt

`BinFileReader.B2T([filename],[number\_of\_channels],[channel])`

channel: channel to be converted

Output: creates a .txt file with the data for one channel. Output filename is same as input (different extension obviously)
