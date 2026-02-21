IfcOpenShell AI Assistant 
=========================

A web-based client-side (pyodide + OpenAI API) model interrogation and generation API based on: ifcedit, ifcquery and ifcmcp packaged in a HTML+JS application.

### Setup instructions

```
mkdir ./src/chat/dist
cd ./src/ifcquery/
python -m build
cp ./dist/ifcquery-0.0.0-py3-none-any.whl ../chat/dist/
cd ../../src/ifcedit
python -m build
cp ./dist/ifcedit-0.0.0-py3-none-any.whl ../chat/dist/
cd ../../src/ifcmcp
python -m build
cp ./dist/ifcmcp-0.0.0-py3-none-any.whl ../chat/dist/
cd ../chat/dist/
wget https://files.pythonhosted.org/packages/82/3d/14ce75ef66813643812f3093ab17e46d3a206942ce7376d31ec2d36229e7/lark-1.3.1-py3-none-any.whl
```