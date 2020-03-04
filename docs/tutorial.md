
# Tutorial

## Writing and loading whip specification files

Whip specifications in text format are expressed in [YAML](https://en.wikipedia.org/wiki/YAML) 
language,  It uses both Python-style indentation to indicate nesting, and a more compact 
format that uses `[]` for lists and `{}` for key-value maps, making YAML 1.2 a superset of JSON.

The whip syntax is explained in more detail on the [whip](https://github.com/inbo/whip) repository,
explaining the available specifications. 

Consider the following data set used in a project, with 3 columns:
* a `eventDate` column, representing the date of occurrence
* a `individualCount` column with the counts of individuals seen on the date
* a `country` column, defining the country of the observation  

An subset of the data could look like this:

eventDate  | individualCount | country
-----------|-----------------|---------
2018-01-03 | 5               |  BA  
2018-04-02 | 20              |  NL
2016-07-06 | 3300            |  BE
2017-03-02 | 2               |  BE
1018-01-08 | 1               |  NL

In the current project, we do know the following about the data:
* The project was running from 2016 until 2018, so date values should be in this range
* The project was happening in Belgium and The Netherlandsa and country need to be either `BE` or `NL`
* Individual counts can not be higher than 100 and should be at least 1 
* Empty values are not allowed (default according to whip specifications)

We can express these rules as [whip specifications](https://github.com/inbo/whip):

```yaml
country:
   allowed: [BE, NL]
eventDate:
    dateformat: '%Y-%m-%d'
    mindate: 2016-01-01
    maxdate: 2018-12-31
individualCount:
    numberformat: x  # needs to be an integer value
    min: 1
    max: 100
```
*(Notice the possibility to include comments)*

These specifications can be saved to a yaml-file (use the extention `.yaml`), e.g. `observations_example.yaml` 
and parsed into Python using the yaml-package:

```python
import yaml

with open("observations_example.yaml") as whip_specs_file:
    specifications = yaml.load(whip_specs_file)
``` 

Similar to loading the file, one can also write the specifications directly in a Python script:

```python
import yaml

whip_specs = """
    country:
       allowed: [BE, NL]
    eventDate:
        dateformat: '%Y-%m-%d'
        mindate: 2016-01-01
        maxdate: 2018-12-31
    individualCount:
        numberformat: x  # needs to be an integer value
        min: 1
        max: 100
    """
 
specifications = yaml.load(whip_specs)  
```
or directly the Python-object itself:
```python
import datetime
specifications = {'individualCount': {'min': 1, 'max': 100, 
                                      'numberformat': 'x'}, 
                  'eventDate': {'dateformat': '%Y-%m-%d', 
                  'maxdate': datetime.date(2018, 12, 31), 
                  'mindate': datetime.date(2016, 1, 1)}, 
                  'country': {'allowed': ['BE', 'NL']}}

```
*(Notice that the dates are coerced to `datetime.date` objects)*

Using one of these approaches, the `specifications` can be used by `pywhip` to control incoming data sets.

## Whip a data set

Pywhip supports a number of data input formats that can be used to apply the whip specifications.

### CSV files

Applying whip specifications to a CSV file is supported by the function `whip_csv`, which requires
a data  file, the whip specifications and the delimiter of the CSV file (`","` for CSV, `"\t"` for TSV,...)

```python
import yaml

from pywhip import whip_csv

with open("observations_example.yaml") as whip_specs_file:
    specifications = yaml.load(whip_specs_file)

observations_whip = whip_csv("observations_data.csv", 
                             specifications, delimiter=',')
```
When the data set is according to the provided whip specifications, a Hooray message prints to stdout:

```
Hooray, your data set is according to the guidelines! 
```

If not, a message alerts you to check the errors:

```
Your dataset does not comply with the specifications, use get_report() for more detailed information.'
```

Default reports are provided as `json` or `html`. It is advised to use a context to store 
store the output as file (e.g. called `report_observations.html`):

```python
with open("report_observations.html", "w") as index_page:
    index_page.write(observations_whip.get_report('html'))
```

By which an [HTML version](report_observations.html) of the error report is generated. Similar, 
a json version of the report can be provided (and returned or saved to file):

```python
import json

with open('report_observations.json', 'w') as json_report:
    json.dump(observations_whip.get_report(), json_report)
```

Which provides a file version of the [json report](report_observations.json).

**Remark:**

In some occasions it is useful to not directly validate the entire data set. In that case,
use the `maxentries` parameter to define the number of lines to validate: 

```python
observations_whip = whip_csv("observations_data.csv", 
                             specifications, delimiter=',',
                             maxentries=50)
```

### Darwin Core Archive

To validate the core file of a [Darwin Core Archive](https://en.wikipedia.org/wiki/Darwin_Core_Archive) 
zipped data set, the packages relies on the [Darwin Core Reader](https://python-dwca-reader.readthedocs.io/en/latest/)
package. To directly apply the specifications on a Darwin Core Archive, use the `whip_dwca` function:

```python
import yaml

from pywhip import whip_dwca

with open("observations_example.yaml") as whip_specs_file:
    specifications = yaml.load(whip_specs_file)

observations_whip = whip_dwca("observations_data.csv", 
                              specifications)
```

Reporting functionalities are the same as the csv-version.


## Whip CSV files from the command line

To apply pywhip for data set validation outside Python, use the command line
interface providing direct application of pywhip on a CSV data set. By installing
the package, the `whip_csv` command will be available from the command line.

To read the documentation:

```bash
whip_csv --help
```

As an example, to whip the data set `observations_data.csv` with a comma as delimiter
using the whip specifications defined in the `observations_example.yaml` file 
and printing the output to an `index.html` as an HTML page:

```bash
whip_csv observations_data.csv observations_example.yaml index.html --delimiter ','
```

    



 


 

