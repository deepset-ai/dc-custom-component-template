# dc-custom-component-template



### Installation
We use `hatch` to manage our python packages. To install hatch, see the following [link](https://hatch.pypa.io/latest/install). Once installed, you can create yourself a virtual environment by running the following command:


```bash
hatch shell
```

This will install all necessary packages needed to create a custom component.
You can reference that virtual in your IDE.



### Formatting
We defined a suite of formatting tools. To format your code, run the following command:

```bash
hatch run code-quality:all
```

### Upload your custom component

To upload your custom component, you first need to zip your project. To do so, run the following command:

```bash
zip -r ../custom_component.zip ./*
```

from inside this project.

This will generate a zip file called `custom_component.zip` in the parent directory.

You can then upload the zip file [to this endpoint](https://docs.cloud.deepset.ai/reference/import_custom_components_api_v2_custom_components_post).

PS: don't forget to update the version in `dc_custom_component/__about__.py` before uploading. ;)