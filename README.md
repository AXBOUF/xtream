# Contributed to a local car wash business
Transitioned Local Legacy Car wash business to end to end automated pipeline and modernized. 

# Mapping the structure (lossely coupled)
Structuring project dir map. 


## Note 
How to activate python env in windows powershell 

```powershell

python -m venv venv # universal 

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser # upper line allows permission 

.\venv\Scripts\Activate

pip install ---

pip freeze > requirements.txt

```
```sh 
#!/usr/bin/env bash 
```


Recommended approach

Use absolute paths in modular scripts if the folder location is fixed.

If you want to make it flexible, pass the folder as a script argument:

```sh
#!/usr/bin/env bash

BASE_DIR="$1"

if [[ -z "$BASE_DIR" ]]; then
  echo "Usage: $0 /path/to/dataschema"
  exit 1
fi

# ...rest of the script...

./organise_by_month "/workspaces/xtream/project0/dataschema"

```