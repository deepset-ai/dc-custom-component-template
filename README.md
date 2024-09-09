# dc-custom-component-template
## A Template for Creating Custom Components in deepset Cloud

This repository contains a template for creating custom components for your deepset Cloud pipelines. Components are pieces of Python code that perform specific tasks. The template will guide you through all the necessary elements your custom component must have.

### Structure

| File | Description |
|------|-------------|
| `/src/custom_component/src.py` | Template for creating custom components. Write your custom component here. |
| `/src/__about__.py` | Your component version. deepset Cloud always uses the latest version. Bump the version every time you update your component before uploading it to deepset Cloud. |
| /pyproject.toml | Information about this project. If needed, you can add your component's dependencies in this file in the `dependencies` section. |

### Documentation
To learn more about custom components, see [Custom Components](https://docs.cloud.deepset.ai/v2.0/docs/custom-components).
For a step-by-step guide for creating custom components, see [Create a Custom Component](https://docs.cloud.deepset.ai/v2.0/docs/create-a-custom-component).

### Prerequisites
Anything here? like min Python version? hatch package manager?

### Installation
We use `hatch` to manage our python packages. For instructions to install Hatch, see the following [Hatch Installation](https://hatch.pypa.io/latest/install). Once installed, you can create a virtual environment by running:


```bash
hatch shell
```

This installs all the necessary packages needed to create a custom component.
You can reference this virtual environment in your IDE.

### Upload your custom component
1. Clone this repository.
2. Navigate to the `/src/custom_component/src.py` file.
3. Implement your custom component following the template.
4. Update the version in `/src/__about__.py`.
5. Format your code using the `hatch run code-quality:all` command. For details, see the Formatting section.
6. Zip your project by running the following command from inside of this project: `zip -r ../custom_component.zip ./*` (on Linux and MacOS) or `Compress-Archive -Path .\* -DestinationPath ..\custom_component.zip -Force` (on Windows). This creates a zip file called `custom_component.zip` in the parent directory.
6. Upload your zip file to deepset Cloud using the Import [Custom Components](https://docs.cloud.deepset.ai/reference/import_custom_components_api_v2_custom_components_post) endpoint.

For detailed instructions, refer to our documentation on [Creating a Custom Component](https://docs.cloud.deepset.ai/v2.0/docs/create-a-custom-component).


### Formatting
We defined a suite of formatting tools. To format your code, run:

```bash
hatch run code-quality:all
```
 ### Testing
 How is it tested? should add some info?

