from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="krishiai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered farming assistant for rural farmers with voice and SMS support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/krishiai",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Farmers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'flask>=2.0.0',
        'flask-cors>=3.0.0',
        'google-generativeai>=0.3.0',
        'openai>=1.0.0',
        'google-cloud-texttospeech>=2.0.0',
        'google-cloud-speech>=2.0.0',
        'googletrans>=4.0.0',
        'requests>=2.25.0',
        'python-dotenv>=0.19.0',
        'twilio>=8.0.0',
        'speechrecognition>=3.8.0',
        'pydub>=0.25.0',
    ],
    entry_points={
        'console_scripts': [
            'krishiai=app:main',
        ],
    },
)
