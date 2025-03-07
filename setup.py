from setuptools import setup, find_packages

setup(
    name="financelib",
    version="0.1.0",
    description="Simple finance library for stock market data",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="financelib"),
    package_dir={"": "financelib"},
    install_requires=[
        "yfinance>=0.2.36",
        "pandas>=1.5.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
