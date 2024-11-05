from setuptools import setup, find_packages

setup(
    name="fastapi-supabase",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "pyjwt>=2.8.0",
        # "uvicorn>=0.22.0",
    ],
    extras_require={
        "dev": [
            "python-dotenv>=1.0.0",
            "httpie>=3.2.1",
        ],
    },
) 