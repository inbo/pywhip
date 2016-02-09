# dwca_validator
Environment to set up validations of dwca archives

The aim is to create an easy to set up suite of 'unit' tests for Darwin Core data archives, which can be set up on a institutional and/or data set level. 
A config-file (yaml,...) is used to define the tests that need to be included and the Vocabulary to test for. The config provides a distinction in between 
'institute' specific tests and core-archiv tests

All tests are specified by a Term testing in that row in combination with a Test. Tests are grouped in different Test-types (Equal, EqualOptions,..) 
- Equal
- NotEqual
- Conditional
- ValidDataType (json, integer...)
- Delimiter
- StringFormat (ISO8601, UpperCamelCase, lowercase, .5f)
(- RegExpress=> generic general expression? would be for more advanced users)

All the validation info is stored in a dictionary object, referring to the Term and the type of test and logging:
- IDs  or only just a counter -> to reevaluate later
- different kind of failures (different kind of mistakes within a single test) => For every mistake, the set of existing mistakes is checked and if other flavour of wrong, these are enlisted; till a max of 10

dict-object: 
{Term:{TestType:{"ids": [id1, id2,...], "sample": [value1,...value10]
                                  }
            }
}


The resulting object will be processed by a Report creator, which provides an overview of the current problems for each of the tests set up...
