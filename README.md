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

### populated

Does the field contain data?

``` YAML
# Expects: boolean
# Records without data: is being tested
# Records of wrong data type: n/a

populated: true # The term must contain data
populated: false # The term cannot contain data
```

### type

Does the data conform to a specific field type?

```YAML
# Expects: string
# Records without data: are ignored
# Records of wrong data type: is being tested

type: integer
type: float
type: json
type: uri
```

### equals

Does the data equal a specific value? 

```YAML
# Expects: string or list
# Records without data: are ignored
# Records of wrong data type: all considered strings

equals: male
equals: [male, female] # Male or female
```

### unique

Does this term contain unique values across all rows?

```YAML
# Expects: boolean
# Records without data: are ignored??
# Records of wrong data type: all considered strings

unique: true # All values must be unique
unique: false # Default. Ignored
```

### length

Does the data character length fall between a range?

```YAML
# Expects: integer or list of two integers
# Records without data: are ignored
# Records of wrong data type: all considered strings

length: 8
length: [2,4] # Character length is between 2 and 8 inclusive
```

### range

Does the data fall between a numeric range?

```YAML
# Expects: list of two integers or list of two floats
# Records without data: are ignored
# Records of wrong data type: fail test

range: [0.5,1] # Between 0.5 and 1 inclusive
range: [,200]  # Less or equal than 200
range: [1,]    # More or equal than 1
range: [,]     # Incorrect syntax
```

### numberFormat

Does the data conform to a [specific number format](https://mkaz.github.io/2012/10/10/python-string-format/)?

```YAML
# Expects: string
# Records without data: are ignored
# Records of wrong data type: fail test

numberFormat: .5f # 5 decimals
```

### regex

Does the data match a specific regex expression?

```YAML
# Expects: regex expression
# Records without data: are ignored!
# Records of wrong data type: all considered strings

regex: # No example yet
```

### listValues

Not a test, will just list all unique values in the output.

```YAML
# Expects: boolean
# Records without data: are ignored
# Records of wrong data type: all considered strings

listValues: true
listValues: false # Default. Ignored
```

### dateValues

Subfunction to work with date values. Will alter `equals` and `range` functionality. Alternative would be to work with `dateFormat` and `dateRange`.

```YAML
dateValues:
- equals: [YYYY-MM-DD, YYYY-MM, YYYY] # Will match specific date formats
- range: [1830-01-01, 2014-10-20] # Will match dates between specific date range (inclusive)
```

### delimitedValues

Subfunction to work on delimited data within a field. Will alter the functionality off all functions to work with the delimited data instead of the whole string. Requires `delimiter`.

```YAML
delimitedValues:
    - delimiter: " | "  # Will use this delimiter for separating values.
                        # Depending on how well data is delimited, the 
                        # following tests will fail or succeed
    - populated: true   # No empty delimited values
    - type: url
    - equals: [male, female] # Delimited values equal male or female
    - unique: true      # Syntax error, not supported
    - length: 8         
    - range: [1,2]
    - numberFormat: .3f
    - regex: ...
    - listValues: true  # List unique delimited values across all records
    - dateValues: ...   # Use dateValues subfunction
    - delimitedValues   # Syntax error
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
