# dc-custom-component-template
## A Template for Creating Custom Components in deepset Cloud

This repository contains a template for creating custom components for your deepset Cloud pipelines. Components are pieces of Python code that perform specific tasks. The template will guide you through all the necessary elements your custom component must have.
This repository contains two sample components which are ready to be used: 
  - `CharacterSplitter` implemented in `/src/dc_custom_component/components/preprocessors/character_splitter.py` to be used in indexing pipelines
  - `KeywordBooster` implemented in `/src/dc_custom_component/components/rankers/keyword_booster.py` to be used in query pipelines

### Structure

| File | Description |
|------|-------------|
| `/src/dc_custom_component/components/../component.py` | Custom component implementation: Write your custom component here. |
| `/src/dc_custom_component/__about__.py` | Your component version. deepset Cloud always uses the latest version. Bump the version every time you update your component before uploading it to deepset Cloud. |
| /pyproject.toml | Information about this project. If needed, you can add your component's dependencies in this file in the `dependencies` section. |

### Documentation
To learn more about custom components, see [Custom Components](https://docs.cloud.deepset.ai/v2.0/docs/custom-components).
For a step-by-step guide for creating custom components, see [Create a Custom Component](https://docs.cloud.deepset.ai/v2.0/docs/create-a-custom-component).

### Prerequisites
- Python 3.11
- hatch >= 1.7.0 (run `pip install hatch`)

### Development
We use `hatch` to manage our python packages. For instructions to install Hatch, see the following [Hatch Installation](https://hatch.pypa.io/latest/install). Once installed, you can create a virtual environment by running:


```bash
hatch shell
```

This installs all the necessary packages needed to create a custom component.
You can reference this virtual environment in your IDE.

### Formatting
We defined a suite of formatting tools. To format your code, run:

```bash
hatch run code-quality:all
```
### Testing
- pytest is ready to be used with hatch
- implement your tests under `/test`
- run `hatch run tests`

### Upload your custom component
1. Clone this repository.
2. Note that the location of your custom component implementation defines the type name of your component to be used in pipeline YAML. E.g. our sample components have the following type names:
  - `dc_custom_component.components.preprocessor.character_splitter.CharacterSplitter`
  - `dc_custom_component.components.rankers.keyword_booster.KeyWordBooster`

3. Implement your custom components following the sample components' schema..
4. Update the version in `/src/__about__.py`.
5. Format your code using the `hatch run code-quality:all` command. For details, see the Formatting section.
6. Zip your project by running the following command from inside of this project: `hatch run dc:create-zip` (on Linux and MacOS) or `hatch run dc:create-zip-windows` (on Windows). This creates a zip file called `custom_component.zip` in the repository directory.
6. Upload your zip file to deepset Cloud using the Import [Custom Components](https://docs.cloud.deepset.ai/reference/import_custom_components_api_v2_custom_components_post) endpoint.

For detailed instructions, refer to our documentation on [Creating a Custom Component](https://docs.cloud.deepset.ai/v2.0/docs/create-a-custom-component).

