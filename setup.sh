# Exit when any command returns non-zero code
set -e

echo "Updating pip, setuptools, wheel and twine"
pip install --upgrade build
pip install --upgrade twine
echo "----------------------------------------------------------------------"
echo "PERFORMING TESTS"
python3 setup.py test
echo "----------------------------------------------------------------------"
echo "PERFORMING DOCTESTS"
cd docs && make doctest && cd ..
echo "----------------------------------------------------------------------"
echo "CLEANING PREVIOUS BUILD"
rm -rf build/ dist/ pycognaize.egg-info/ .eggs/ .pytest_cache/
echo "----------------------------------------------------------------------"
echo "CREATING WHEEL FILE"
python3 -m build
echo "----------------------------------------------------------------------"
echo "PUSHING $(find dist -maxdepth 1 -name 'pycognaize*.whl')"
# DELETE --repository testpypi TO UPLOAD TO PYPI
python3 -m twine upload --repository pypi dist/* --username cognaize
echo "----------------------------------------------------------------------"
echo "REMOVING LEFTOVER FOLDERS"
rm -rf build/ dist/ pycognaize.egg-info/ .eggs/ .pytest_cache/
echo "----------------------------------------------------------------------"

echo "PROCESS COMPLETED"
