# Python Darwin Core Archive validator

*Note: this project is in under development. The documentation might not reflect the current functionality.*

## Rationale

The aim of this project is to create an easy to set up suite of validation tests for [Darwin Core Archives](https://en.wikipedia.org/wiki/Darwin_Core_Archive). Using a YAML settings file, the user can define which tests to include and against which conditions to test: these can be general or institution/dataset specific.

## Validation

Tests are performed per row, per term (field) and are independent of each other, i.e. they can be performed in any order. Which tests to perform is defined in a settings file ([example](settings.yaml)), which has the following syntax:

```YAML
Term 1:
- Test 1
- Test 2

Term 2:
- Test 1
- Test 3
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

Cerberus already provide a set of [validation rules](http://docs.python-cerberus.org/en/stable/usage.html#validation-rules), which can be used and extended for the validator case

### required
*(cerberus supported)*

Does the field contain data?

``` YAML
# Expects: boolean
# Records without data: is being tested
# Records of wrong data type: n/a

required: true # The term must contain data
required: false # The term cannot contain data
```

### type
*(partly cerberus supported)*

Does the data conform to a specific field type? Cerberus supports following dtypes:
* string
* integer
* float
* number (integer or float)
* boolean
* datetime (!the datatype itself, not formatted string)
* dict (formally collections.mapping)
* list (formally collections.sequence, excluding strings)
* set

The dwac validator uses a custom rule for dates, embedded in dateFormat. Furthermore, uri and json formats will be explicitly supported as group type.

```YAML
# Expects: string
# Records without data: are ignored
# Records of wrong data type: is being tested

type: integer
type: float
type: json
type: uri
```

### allowed
*(cerberus supported)*)*

Does the data equal a specific value? (cfr. equals)

```YAML
# Expects: string or list
# Records without data: are ignored
# Records of wrong data type: all considered strings

allowed: male
allowed: [male, female] # Male or female
```

### unique

Does this term contain unique values across all rows?
(Currently not planned for development)

```YAML
# Expects: boolean
# Records without data: are ignored??
# Records of wrong data type: all considered strings

unique: true # All values must be unique
unique: false # Default. Ignored
```

### minlength
*(cerberus supported)*

Is the length of the data string or list larger than the given value

```YAML
# Expects: integer
# Records without data: are ignored
# Records of wrong data type: all considered strings

minlength: 8  # Character length is larger than 2
```

### maxlength
*(cerberus supported)*

Is the length of the data string or list smaller than the given value

```YAML
# Expects: integer
# Records without data: are ignored
# Records of wrong data type: all considered strings

maxlength: 20  # Character length is smaller than 20
```

### minimum
*(cerberus supported)*

Minimum value allowed for any types that implement comparison operators.

```YAML
# Expects: int/float or other dtype supporting comparison; values will be compared as floats
# Records without data: are ignored
# Records of wrong data type: fail test

minimum: 0.5     # float
minimum: 20     # integer
```

### maximum
*(cerberus supported)*

Maximum value allowed for any types that implement comparison operators.

```YAML
# Expects: int/float or other dtype supporting comparison; values will be compared as floats
# Records without data: are ignored
# Records of wrong data type: fail test

maximum: 0.75     # float
maximum: 200     # integer
```

### daterange

Does the date/datetime objects fall between a specific date range?

```YAML
# Expects: list of two dates
# Records without data: are ignored
# Records of wrong data type: fail test

daterange: [1830-01-01, 2014-10-20] # Between 1 Jan 1830 and 20 October 2014 inclusive
daterange: [, 2014-10-20] # Before 20 October 2014
daterange: [1830-01-01,] # After 1 Jan 1830
daterange: [,]     # Incorrect syntax
```

### numberformat

Does the data conform to a [specific number format](https://mkaz.github.io/2012/10/10/python-string-format/)?

```YAML
# Expects: string
# Records without data: are ignored
# Records of wrong data type: fail test

numberformat: .5f # 5 decimals
```

### dateformat

Does the data conform to a specific date format?

```YAML
dateformat:[YYYY-MM-DD, YYYY-MM, YYYY] # Will match specific date formats
```

### regex

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

### delimitedValues

Subfunction to work on delimited data within a field. Will alter the functionality off all functions to work with the delimited data instead of the whole string. Requires `delimiter`.

```YAML
delimitedValues:
  delimiter: " | "  # Will use this delimiter for separating values.
                        # Depending on how well data is delimited, the
                        # following tests will fail or succeed
  required: true   # No empty delimited values
  type: url
  equals: [male, female] # Delimited values equal male or female
  unique: true      # Syntax error, not supported
  minlength: 8       
  maxlength: 8             
  minimum: 1
  maximum: 1  
  numberformat: .3f
  regex: ...
  listvalues: true  # List unique delimited values across all records
  dateformat: ...   # Use dateValues subfunction
  delimitedValues: ...  # Syntax error
```

### if

Subfunction to perform tests based on the tests on another term. All tests on the other term must succeed (i.e. they are combined with `AND`) before test are performed.

```YAML
if:
    - basisOfRecord:                # Another term
        - populated: true           # basisOfRecord must be populated
        - equals: HumanObservation  # AND basisOfRecord must be "HumanObservation"
    - equals: Event                 # Then the main term must be "Event"
    - populated: true               # Then the main term must be "Populated"
```
