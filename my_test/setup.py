from setuptools import setup, find_packages

setup(
    name="shopify_module",                 # keep this same as your package folder name
    version="1.0.0",                      # change if you update later
    packages=find_packages(),             # auto-detects modules inside create_module/
    install_requires=[                    # list of dependencies your code needs
        "requests",
        "python-dotenv",
        "pandas",
        "openpyxl",
        "shopifyapi",
    ],
    python_requires=">=3.8",              # Python version requirement
    author="Ganesh Gayakwad",                   # change to your name
    description="Shopify integration utilities",  # short description
)
