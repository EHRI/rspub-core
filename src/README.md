# Dependencies on external source code

Run un pip install on `requirements.txt`
in the root directory of `rspub-core`.

```
cd /path/to/your/rspub-core
pip install -r requirements.txt
```

This will install required sources in the directory `src/{name}`.

## Externals

### resync

[resync](https://github.com/resync/resync) is "A Python library and 
client implementing the ResourceSync web synchronization framework". 
We use the [EHRI distribution](https://github.com/EHRI/resync) which 
has been ported to Python3 and has several additions to the code.

