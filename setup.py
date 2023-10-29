from setuptools import setup, find_packages

setup(
    name='bot-assistant',
    version='0.1.0',
    description='cli bot assistant',
    packages=find_packages(),
    author="Roman Slipchenko",
    author_email="romanslipchenko@gmail.com",
    license='MIT',
    entry_points={'console_scripts': [
        'bot-assistant = modules.bot_assistant.main:main']},
)
