# deepset Cloud Custom Component Template

This repository contains a template for creating custom components for your deepset Cloud pipelines. Components are Python code snippets that perform specific tasks within your pipeline. This template will guide you through all the necessary elements your custom component must include.
This template contains two sample components which are ready to be used: 
  - `CharacterSplitter` implemented in `/src/dc_custom_component/example_components/preprocessors/character_splitter.py`: A component that splits documents into smaller chunks by the number of characters you set. You can use it in indexing pipelines.
  - `KeywordBooster` implemented in `/src/dc_custom_component/example_components/rankers/keyword_booster.py`: A component that boosts the score of documents that contain specific keywords. You can use it in query pipelines.

We've created these examples to help you understand how to structure your components. When importing your custom components to deepset Cloud, you can remove or rename the `example_components` folder with the sample components, if you're not planning to use them. 

This template serves as a custom components library for your organization. Only the components present in the most recently uploaded template are available for use in your pipelines. 

## Documentation
For more information about custom components, see [Custom Components](https://docs.cloud.deepset.ai/docs/custom-components). 
For a step-by-step guide on creating custom components, see [Create a Custom Component](https://docs.cloud.deepset.ai/docs/create-a-custom-component).
See also our tutorial for [creating a custom RegexBooster component](https://docs.cloud.deepset.ai/docs/tutorial-creating-a-custom-component).

## 1. Setting up your local dev environment

### Prerequisites

- Python v3.10 or v3.11
- `hatch` package manager

### Hatch: A Python package manager

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

This installs all the necessary packages needed to create a custom component. You can reference this virtual environment in your IDE.

For more information on `hatch`, please refer to the [official Hatch documentation](https://hatch.pypa.io/).

## 2. Developing your custom component

### Structure

| File | Description |
|------|-------------|
| `/src/dc_custom_component/components` | Directory for implementing custom components. You can logically group custom components in sub-directories. See how sample components are grouped by type. |
| `/src/dc_custom_component/__about__.py` | Your custom components' version. deepset Cloud always uses the latest version. Bump the version every time you update your component before uploading it to deepset Cloud. |
| `/pyproject.toml` | Information about the project. If needed, add your components' dependencies in this file in the `dependencies` section. |

The directory where your custom component is stored determines the name of the component group in Pipeline Builder. For example, the `CharacterSplitter` component would appear in the `Preprocessors` group, while the `KeywordBooster` component would be listed in the `Rankers` group. You can drag these components onto the canvas to use them.

When working with YAML, the location of your custom component implementation defines your component's `type`. For example, the sample components have the following types because of their location:
  - `dc_custom_component.example_components.preprocessors.character_splitter.CharacterSplitter`
  - `dc_custom_component.example_components.rankers.keyword_booster.KeywordBooster`

Here is how you would add them to a pipeline:
```yaml
components:
  splitter:
    type: dc_custom_component.example_components.preprocessors.character_splitter.CharacterSplitter
    init_parameters: {}
  ...
    
```
### Working on your component

1. Fork this repository.
2. Navigate to the `/src/dc_custom_component/components/` folder.
3. Add your custom components following the examples.
4. Update the components' version in `/src/__about__.py`.
5. Format your code using the `hatch run code-quality:all` command. (Note that hatch commands work from the project root directory only.)

### Formatting
We defined a suite of formatting tools. To format your code, run:

```bash
hatch run code-quality:all
```

### Testing

It's crucial to thoroughly test your custom component before uploading it to deepset Cloud. Consider adding unit and integration tests to ensure your component functions correctly within a pipeline.
- `pytest` is ready to be used with `hatch`
- implement your tests under `/test`
- run `hatch run tests`

## 3. Uploading your custom component

You can upload in one of two ways:
- By releasing your forked directory.
- By zipping the forked repository and uploading it with commands.

### Uploading by releasing your forked repository

We use GitHub Actions to build and push custom components to deepset Cloud. The action runs the tests and code quality checks before pushing the component code to deepset Cloud. Create a tag to trigger the build and the push job. This method helps you keep track of the changes and investigate the code deployed to deepset Cloud.

After forking or cloning this repository:

1. Push all your changes to the forked repository.
2. Add the `DEEPSET_CLOUD_API_KEY` [secret to your repository](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions). This is your deepset Cloud API key.
(To add a secret, go to your repository and choose _Settings > Secrets and variables > Actions > New repository secret_.)
3. Enable workflows for your repository by going to _Actions > Enable workflows_.
4. (Optional) Adjust the workflow file in `.github/workflows/publish_on_tag.yaml` as needed.
5. Create a new release with a tag to trigger the GitHub Actions workflow. The workflow builds and pushes the custom component to deepset Cloud with the tag as version. For help, see [GitHub documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

> **Warning:** When using this GitHub Actions workflow, the version specified in the `__about__` file will be overwritten by the tag value. Make sure your tag matches the desired version number. 

You can check the upload status in the `Actions` tab of your forked repository. 

### Uploading a zipped repository with commands

In this method, you run commands to zip and push the repository to deepset Cloud.

1. Set your [deepset Cloud API key](https://docs.cloud.deepset.ai/docs/generate-api-key).
   - On Linux and macOS: `export API_KEY=<TOKEN>`
   - On Windows: `set API_KEY=<TOKEN>`
2. Upload your project by running the following command from inside of this project:
   - On Linux and macOS: `hatch run dc:build-and-push`
   - On Windows: `hatch run dc:build-windows` and `hatch run dc:push-windows`
   This creates a ZIP file called `custom_component.zip` in the `dist` directory and uploads it to deepset Cloud.






