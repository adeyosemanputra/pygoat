import yaml
import json
import subprocess
sample = {
  "foo": "bar",
  "baz": [
    "qux",
    "quxx"
  ],
  "corge": None,
  "grault": 1,
  "garply": True,
  "waldo": "false",
  "fred": "undefined",
  "emptyArray": [],
  "emptyObject": {},
  "emptyString": ""
}
data2="""baz:
- qux
- quxx
corge: null
emptyArray: []
emptyObject: {}
emptyString: ''
foo: bar
fred: undefined
garply: true
grault: 1
waldo: 'false'
"""

with open(r"ajmal.yaml") as file:
  data=yaml.load(file)
print(data);