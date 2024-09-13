# dc-custom-component-template

This repository contains a template for creating custom components for your deepset Cloud pipelines. Components are Python code snippets that perform specific tasks within your pipeline. This template will guide you through all the necessary elements your custom component must include.
In addition this repository contains two sample components which are ready to be used: 
  - `CharacterSplitter` implemented in `/src/dc_custom_component/example_components/preprocessors/character_splitter.py` to be used in indexing pipelines
  - `KeywordBooster` implemented in `/src/dc_custom_component/example_components/rankers/keyword_booster.py` to be used in query pipelines

## Documentation
For more information about custom components, please refer to our [Custom Components](https://docs.deepset.ai/docs/custom-components) documentation. For a step-by-step guide on creating custom components, see [Create a Custom Component](https://docs.deepset.ai/docs/create-a-custom-component).

## 1. Setting up your local dev environment

### Prerequisites

- Python v3.10 or v3.11
- `hatch` package manager

### Hatch: A Python Package Manager

We use `hatch` to manage our Python packages. Install it with pip:

Linux and macOS:
```bash
pip install hatch
```

Windows:
Follow the instructions under https://hatch.pypa.io/1.12/install/#windows

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
| `/src/dc_custom_component/components` | Directory for implementing custom components. You can logically group custom components in sub-directories. E.g. see how example components are grouped by type. |
| `/src/dc_custom_component/__about__.py` | Your custom components' version. deepset Cloud always uses the latest version. Bump the version every time you update your component before uploading it to deepset Cloud. |
| `/pyproject.toml` | Information about the project. If needed, add your components' dependencies in this file in the `dependencies` section. |

Note that the location of your custom component implementation defines the type name of your component to be used in pipeline YAML. E.g. our example components have the following type names:
  - `dc_custom_component.example_components.preprocessor.character_splitter.CharacterSplitter`
  - `dc_custom_component.example_components.rankers.keyword_booster.KeyWordBooster`

### Formatting
We defined a suite of formatting tools. To format your code, run:

```bash
hatch run code-quality:all
```

### Testing

It's crucial to thoroughly test your custom component before uploading it to deepset Cloud. Consider adding unit tests and integration tests to ensure your component functions correctly within a pipeline.
- pytest is ready to be used with hatch
- implement your tests under `/test`
- run `hatch run tests`

## 3. Uploading your custom component

1. Fork this repository.
2. Navigate to the `/src/dc_custom_component/components/` folder.
3. Add your custom components following the examples under `/src/dc_custom_component/example_components/`.
4. Delete example components under `/src/dc_custom_component/example_components/`.
5. Update the components' version in `/src/__about__.py`.
6. Format your code using the `hatch run code-quality:all` command. (hatch commands work from project root directory only)
7. Set your [deepset Cloud API key](https://docs.cloud.deepset.ai/v2.0/docs/generate-api-key).
   - On Linux and macOS: `export API_KEY=<TOKEN>`
   - On Windows: `SET API_KEY=<TOKEN>`
8. Upload your project by running the following command from inside of this project:
   - On Linux and macOS: `hatch run dc:build-and-push`
   - On Windows: `hatch run dc:build-windows` and `hatch run dc:push-windows`
   This creates a zip file called `custom_component.zip` in the `dist` directory and uploads it to deepset Cloud.

For detailed instructions, refer to our documentation on [Creating a Custom Component](https://docs.deepset.ai/docs/create-a-custom-component).
