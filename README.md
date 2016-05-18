# Python Darwin Core Archive validator

*Note: this project is in under development. The documentation might not reflect the current functionality.*

## Rationale

The aim of this project is to create an easy to set up suite of validation tests for [Darwin Core Archives](https://en.wikipedia.org/wiki/Darwin_Core_Archive). Using a YAML settings file, the user can define which tests to include and against which conditions to test: these can be general or institution/dataset specific.

## Validation

Tests are performed per row, per term (field) and are independent of each other, i.e. they can be performed in any order. Which tests to perform is defined in a settings file ([example](settings.yaml)), which has the following syntax:

```YAML
Term 1:
  Test 1
  Test 2

Term 2:
  Test 1
  Test 3
```

All validation information will be stored in a dictionary object, referring to the term, the type of test, and some logging information:

* Number of tests that succeeded and failed or the record IDs of those.
* Examples of unique values that failed (with a maximum of 10):

```python
{
    Term: {
        TestType: {
            "ids": [id1, id2,...],
            "sample": [value1,...value10]
        }
    }
}
```

The resulting object will be processed by a report creator, which provides an overview of the current problems for each of the performed tests.

We could rely on the functionality of marshmallow, as provided in following example: https://gist.github.com/bartaelterman/737b92dd3c58d749717e

## Test types

Cerberus already provide a set of [validation rules](http://docs.python-cerberus.org/en/stable/usage.html#validation-rules), which can be used and extended for the validator case. In the following list, the rules available in the DwcaValidator are enlisted.

### type
*(partly cerberus supported)*

Does the data conform to a specific field type?

Cerberus supports following dtypes, which are also supported by the DWCA validator:
* string
* integer
* float
* number (integer or float)
* boolean

Following Cerberus dtypes are not supported by the Dwca Validator:
* dict (formally collections.mapping)
* list (formally collections.sequence, excluding strings)
* set

Following dtypes are added to the Dwca Validator, not supported by Cerberus:
* url
* json

The DWCA Validator uses a custom rule for dates, embedded in dateformat.

```YAML
# Expects: string
# Records without data: are ignored
# Records of wrong data type: is being tested

type: integer
type: float
type: boolean
type: json
type: url
```

It is important to understand that the DwcaReader will read all fields as string types initially. When no `type` validator is added, the value will be interpreted and tested as a string value. By incorporating a `type` validator, DwcaValidator will first try to interpret the value as the type to test it for (e.g. integer, float). When succeeded, the other tests will be applied on the interpreted value (integer, float).

### length

Is the length of the data string equal to the given value?

```YAML
# Expects: integer
# Records without data: are ignored
# Records of wrong data type: only active with strings

length: 8  # Character length is equal to 8
```

**Remark:**

The behaviour of length (and also `minlength` and `maxlength`) depends on the usage of the `length` validation in combination with the `type` validation or not. When no `type` validation is added (or tests for string, which is default in the Dwcareader), the length will interpret the field as string:

```YAML
maxlength: 2  
type : string  
```
will invoke an error for the field : `{'individualCount' : '100'}`. However, when requiring an integer value:

```YAML
maxlength: 2
type : integer
```
the field `{'individualCount' : '100'}` will be converted to `{'individualCount' : 100}` (100 as integer) and `length` will ignore the integer. It makes more sense to test this with the `min` and `max` validators (see further).

### minlength
*(cerberus supported)*

Is the length of the data string larger than the given value (inclusive the value itself)?

```YAML
# Expects: integer
# Records without data: are ignored
# Records of wrong data type: only active with strings

minlength: 8  # Character length is larger than 8
```

### maxlength
*(cerberus supported)*

Is the length of the data string smaller than the given value (inclusive the value itself)?

```YAML
# Expects: integer
# Records without data: are ignored
# Records of wrong data type: only active with strings

maxlength: 20  # Character length is smaller than 20
```

### min
*(cerberus supported)*

Minimum value allowed for any types that implement comparison operators.

```YAML
# Expects: int/float; values will be compared as floats
# Records without data: are ignored
# Records of wrong data type: ignore (data types are tested separately with `type`)

min: 0.5     # float
min: 20     # integer
```

**Remark**

It is important to combine the test with an appropriate data type validation to enable the test when using numeric values

### max
*(cerberus supported)*

Maximum value allowed for any types that implement comparison operators.

```YAML
# Expects: int/float; values will be compared as floats
# Records without data: are ignored
# Records of wrong data type: ignore (data types are tested separately with `type`)

max: 0.75     # float
max: 200     # integer
```

**Remark**

It is important to combine the test with an appropriate data type validation to enable the test when using numeric values

### equals

Does the data value equal to a given numerical value?

```YAML
# Expects: int/float; values will be compared as floats
# Records without data: are ignored
# Records of wrong data type: only active with integer or float (data types are tested separately with `type`)

equals: 0.75     # float
equals: 200     # integer
```

**Remark**
This test is used for numerical values and should be combined with a `type` test to activate the test. The usage is of particular interest if values should be accepted, but the decimal precision is not important. For example: 0.75 will also accept 0.750 and 200 also 200.0. When the value need to be completely the same, the usage of `allowed` (works on strings) is advisable (see next).


### allowed
*(cerberus supported)*

Does the data is the same sequence of characters?

```YAML
# Expects: list with one or more strings
# Records without data: are ignored
# Records of wrong data type: all considered strings

allowed: [male]
allowed: [male, female] # male or female
```

### empty

Empty values are default not accepted. If an empty values should be present for a particular field, `empty` can be put to `True`

```YAML
# Expects: boolean
# Records of wrong data type: only considered strings (default in Dwc)

empty: True
```

### mindate

Does the date/datetime objects fall before a given date?

```YAML
# Expects: date string
# Records without data: are ignored
# Records of wrong data type: fail test

mindate: 1830-01-01  # After 1 Jan 1830
mindate: 2014-10-20 # After 20 October 2014
```

### maxdate

Does the date/datetime objects fall after a given date?

```YAML
# Expects: date string
# Records without data: are ignored
# Records of wrong data type: fail test

mindate: 1830-01-01  # After 1 Jan 1830
mindate: 2014-10-20 # After 20 October 2014
```

### numberformat

Does the float number conform to a specific precision format?

```YAML
# Expects: string and need to be combined with `type` : float validator
# Records without data: are ignored
# Records of wrong data type: fail test

numberformat: '.5' # 5 decimals, left side of the decimal not specified, e.g. 1.12345 or 12.12345
numberformat: '3.5' # 3 digits at the left side of the decimal and 5 decimal digits, e.g. 123.12345
numberformat: '4.' # 4 digits at the left side, right side not specified, e.g. 1234., 1234.12 or also the integer 1234
```

**Remark**

Float numbers are stored in a double-precision floating-point format. Hence, the check for the numberformat is done before the actual conversion to float numbers in order to do the other tests (e.g. min, max,...)

### dateformat

Does the data conform to a specific date format? Possibilities provided at
http://strftime.org/

```YAML
dateformat:['%Y-%m-%d', '%Y-%m', '%Y'] # Will match specific date formats
```

### regex
*(cerberus supported)*

Does the data match a specific regex expression?

```YAML
# Expects: regex expression
# Records without data: are ignored!
# Records of wrong data type: all considered strings

regex: # No example yet
```

### listvalues

Not a test, will just list all unique values in the output.

```YAML
# Expects: boolean
# Records without data: are ignored
# Records of wrong data type: all considered strings

listvalues: true
listvalues: false # Default. Ignored
```

### delimitedvalues

Subfunction to work on delimited data within a field. Will alter the functionality off all functions to work with the delimited data instead of the whole string. Requires `delimiter`.

```YAML
delimitedvalues:
  delimiter: " | "  # Will use this delimiter for separating values.
                    # Depending on how well data is delimited, the
                    # following tests will fail or succeed
  required: true   # No empty delimited values
  type: url
  allowed: [male, female] # Delimited values equal male or female
  minlength: 8       
  maxlength: 8             
  min: 1
  max: 1  
  numberformat: .3f
  regex: ...
  listvalues: true  # List unique delimited values across all records - TODO
  dateformat: ...   # Use datevalues subfunction
  delimitedvalues: ...  # Syntax error
```

### if

Subfunction to perform tests based on the tests on another term. All tests on the other term must succeed (i.e. they are combined with `AND`) before test are performed.

```YAML
if:
    basisOfRecord:              # Another term
      populated: true           # basisOfRecord must be populated
      allowed: HumanObservation # AND basisOfRecord must be "HumanObservation"
    allowed: Event              # Then the main term must be "Event"
    empty: False              # Then the main term can not be empty
```

To combine multiple if-statements, these need to be grouped as follows:

```YAML
if:
    - age:
          min: 20
          type: integer
      allowed: [adult]
    - age:
          min: 20
          type: integer
      maxlength: 6
```

## Cerberus other rules

### readonly
There is no use-case to apply this rule within the context of the DwcaValidator

### nullable
Default True within DwcaValidator, for both '' and None values
