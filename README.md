# dc-custom-component-template

This repository contains a template for creating custom components for your deepset Cloud pipelines. Components are Python code snippets that perform specific tasks within your pipeline. This template will guide you through all the necessary elements your custom component must include.

## Documentation

For more information about custom components, please refer to our [Custom Components](https://docs.deepset.ai/docs/custom-components) documentation. For a step-by-step guide on creating custom components, see [Create a Custom Component](https://docs.deepset.ai/docs/create-a-custom-component).

## 1. Setting up your local dev environment

### Prerequisites

- Python v3.10
- `hatch` package manager

### Hatch: A Python Package Manager

We use `hatch` to manage our Python packages. Install it with pip:

```bash
pip install hatch
```

Once installed, create a virtual environment by running:

```bash
hatch shell
```

This installs all necessary packages needed to create a custom component. You can reference this virtual environment in your IDE.

For more information on hatch, please refer to the [official Hatch documentation](https://hatch.pypa.io/).

## 2. Developing your custom component

### Structure

| File | Description |
|------|-------------|
| `/src/dc_custom_component/components` | Directory for creating custom components. You can logically group custom components in sub-directories. |
| `/src/dc_custom_component/__about__.py` | Your custom components' version. deepset Cloud always uses the latest version. Bump the version every time you update your component before uploading it to deepset Cloud. |
| `/pyproject.toml` | Information about the project. If needed, add your components' dependencies in this file in the `dependencies` section. |

### Testing

It's crucial to thoroughly test your custom component before uploading it to deepset Cloud. Consider adding unit tests and integration tests to ensure your component functions correctly within a pipeline. You can use Python's built-in `unittest` framework or third-party testing libraries like `pytest`.

## 3. Uploading your custom component

1. Clone this repository.
2. Navigate to the `/src/dc_custom_component/components/` module.
3. Implement your custom components following the samples.
4. Update the version in `/src/__about__.py`.
5. Format your code using the `hatch run code-quality:all` command.
6. Zip your project by running the following command from inside of this project:
   - On Linux and macOS: `hatch run dc:create-zip`
   - On Windows: `hatch run dc:create-zip-windows`
   This creates a zip file called `custom_component.zip` in the repository directory.
7. Upload your zip file to deepset Cloud using the [Import Custom Components endpoint](https://api.cloud.deepset.ai/api/v1/#operation/import_custom_component).

For detailed instructions, refer to our documentation on [Creating a Custom Component](https://docs.deepset.ai/docs/create-a-custom-component).
