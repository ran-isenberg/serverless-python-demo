## Decision log

This file is meant to capture project-level decisions that were made in this project and why. There are often no obvious correct answers, and we must decide with multiple options.

## 2023-08-17

### Project Structure

#### What
We chose an opinionated project structure with an infrastructure folder (CDK-based), a tests folder, and a service folder containing business domain Lambda function code with a makefile to automate developer actions.


#### Why
This structure has proven its worth in production for us. However, there's no right or wrong; other structures might make sense to you.

You can read more about it [here](https://www.ranthebuilder.cloud/post/aws-cdk-best-practices-from-the-trenches)

### CDK

#### What
We chose AWS CDK as the IaC of choice.

#### Why

- There are many IaC options. We chose CDK since we enjoy working with it and have a very positive experience with it and with the experience of defining resources in code instead of YAML files.
- Choose what fits your organization best: AWS SAM, Serverless, Terraform, Pulumi, etc.

### CDK Constructs Structure


#### What

We defined a stack that creates two constructs: one for the crud API and one for the stream processing. The CRUD API also makes the database construct.

#### Why

We chose a business domain-driven Constructs approach. Each domain gets its construct, with the DB being the exception as an "inner" construct.

We don't think there's a right or wrong approach to picking resources into constructs as long as it makes sense to you and you can find help and configurations easily.

However, choosing a business domain-driven approach to selecting which resources belong together in a construct makes sense the most.

Finding resources and understanding their connections is more accessible by looking at the service architecture diagram. It's also easier to share design patterns across teams in organizations that require the same architecture.

You can read more about it with a similar example [here](https://www.ranthebuilder.cloud/post/aws-cdk-best-practices-from-the-trenches)


### CDK Best Practices



#### What

- Stack per developer per branch, stack name is different
- Shared resources are built on the stack and passed as parameters to the constructs init functions.
- Lambda roles define inline policy definitions instead of using CDK's built-in functions



#### Why

- Stack per developer per branch - we wanted multiple developers to share a dev account and work in parallel on the same stack. The CI/CD main pipeline has its unique name to remove any chance of conflicts.
- Shared resources - made sense to build once and pass internal resources such as Lambda layers.
- Lambda roles define inline policy definitions instead of using CDK's built-in functions - CDK's built-in 'grant' function is less privileged and provides more resources than required. They also reduce visibility and abstract actual permissions too much.


You can read more about it [here](https://www.ranthebuilder.cloud/post/aws-cdk-best-practices-from-the-trenches)



### Lambda Layers Usage

#### What

We use a Lambda layer that all our Lambda functions use.

#### Why

We use it as a deployment optimization since all our functions require mostly (or the same) dependencies.

It comprises all '[tool.poetry.dependencies]' in the 'pyproject. toml' file.


You can read more about creating Lambda layers [here](https://www.ranthebuilder.cloud/post/build-aws-lambda-layers-with-aws-cdk) and best practices [here](https://www.ranthebuilder.cloud/post/aws-lambda-layers-best-practices).



### .build folder

#### What

We use as build stage as part of 'make deploy' to copy the Lambda contents from 'product' folder to '.build'.

#### Why

You must supply an asset folder when building a Lambda layer/lambda function with CDK. It removes the top folder and takes the contents.

If we were to supply the 'product' folder as the root folder, we would get import issues when invoking the function since the imports in our lambda function contain 'product.x.y' same as it resides on GitHub.

To solve this issue, we have a build step that it runs when you run 'make deploy'; it copies the 'product' folder from the root level to a new root level folder, the '.build.'

This way, when CDK takes the lambda contents from this new top level, it also takes the 'product' top folder and the imports remain valid.




### Lambda architecture layers

#### What

Under product, you have several folders: one per domain.

Each domain: crud and stream processor, have different layers.

We have different architectural layers: handler -> domain logic -> data access layer.

Each layer has folders for Pydantic schema classes and utilities.


#### Why

This is an opinionated structure backed by AWS best practices to separate handler code from domain logic.

You can read more about it [here](https://www.ranthebuilder.cloud/post/learn-how-to-write-aws-lambda-functions-with-architecture-layers).


### Testing methodology

#### What

We have unit tests, infrastructure tests, integration tests, and end-to-end tests.


#### Why

Each test type has its usage:
- Unit tests check small functions and mostly schema validations.
- Infrastructure tests are run before deployment; they check that critical resources exist and were not deleted from the CloudFormation template (CDK output) by mistake or bug.
- Integration tests occur after deployment and generate a mocked event, call the function handler in the IDE and allow debugging the functions with breakpoints. We call real AWs services and can choose what to mock to simulate failures and what resources to call directly.
- E2E tests - trigger the AWS deployed resources.

You can read about testing methodology and how to test serverless in [this blog series](https://www.ranthebuilder.cloud/post/guide-to-serverless-lambda-testing-best-practices-part-1)



### Pydantic Usage

#### What
We are using pydantic for environment variables parsing, schema validation of input/output, and more.

#### Why

Pydantic is a class leader parsing and validation Python library.

Input validation is a critical security aspect that each application must implement.

Read more about input validation in Lambda [here](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-5-input-validation).

Read more about why you should care about environment variables parsing [here](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-environment-variables).
