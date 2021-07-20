# aws-cdk-python-example

To produce a CDK json file:

- Cd into the folder of the stack.
- Run `python -m pip install -r requirements.txt` to install the required dependencies.
- Then run `cdk synth MyStackName` or `cdk synth \*` if there are more than one stacks in the appication.
- A `cdk.out` folder will be generated and a `MyStack.template.json` file (or more if we have more stacks) should be generated in there.


To scan with Snyk IaC:

- Run `snyk iac test cdk.out/MyStack.template.json`
