<h1 align="center">
<img src="https://github.com/cognaize/pycognaize/blob/master/media/logo/logo.png?raw=true" width="300">
</h1><br>

![Package Version](https://github.com/cognaize/pycognaize/blob/master/media/badges/package_version.svg?raw=true)
![Supported Python Versions](https://github.com/cognaize/pycognaize/blob/master/media/badges/python_versions.svg?raw=true)
![Stability Status](https://github.com/cognaize/pycognaize/blob/master/media/badges/stability_status.svg?raw=true)
![Coverage Percentage](https://github.com/cognaize/pycognaize/blob/master/media/badges/coverage_percentage.svg?raw=true)

# Cognaize SDK
Welcome to Cognaize SDK. Cognaize SDK provides tools and
functionalities for creating, evaluating and deploying models into Cognaize platform.

- **[Website](https://www.cognaize.com)**
- **[Documentation](http://pycognaize-docs.com.s3-website.us-east-2.amazonaws.com)**

**Cognaize SDK** provides:

- Working with **Cognaize snapshots**
- Working with **OCR data**
- Working with **PDF files**
- Working with **images**

## Installation

Cognaize SDK can be installed using pip:

```
pip install pycognaize
```

## Development
### Steps
The following steps should be followed after making changes to the codebase:
1. Update `pycognaize/__init__.py` with the new version number.
2. Update `CHANGELOG.md` with the new version number and a description of the changes.
3. Run `python scripts/update_badges.py` to update the badges in `README.md`.
4. Create docs by running the following commands:
    ```
    cd docs
    ./create_docs.sh
    ```

Have a look at the [quick tutorial](http://pycognaize-docs.com.s3-website.us-east-2.amazonaws.com/tutorials/quick_tutorial.html) 
for understanding main concepts of the SDK.
