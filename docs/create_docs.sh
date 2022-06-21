rm -rf API/_autosummary && make clean && make doctest && make html
aws s3 sync build/html/ s3://pycognaize-docs.com/ --delete
