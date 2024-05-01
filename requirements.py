import subprocess

# Install pygooglenews without dependencies
subprocess.run(['pip', 'install', 'pygooglenews', '--no-deps'], check=True)

# List of packages and their versions to force install
packages = [
    'beautifulsoup4==4.12.3',
    'blinker==1.7.0',
    'certifi==2024.2.2',
    'charset-normalizer==3.3.2',
    'click==8.1.7',
    'colorama==0.4.6',
    'cssselect==1.2.0',
    'dateparse==1.4.0',
    'dateparser==0.7.6',
    'DateTime==4.9',
    'feedfinder2==0.0.4',
    'feedparser==6.0.11',
    'filelock==3.13.4',
    'Flask==3.0.3',
    'Flask-Cors==4.0.0',
    'fuzzywuzzy==0.18.0',
    'idna==3.7',
    'itsdangerous==2.1.2',
    'jieba3k==0.35.1',
    'Jinja2==3.1.3',
    'joblib==1.4.0',
    'Levenshtein==0.25.1',
    'lxml==5.2.1',
    'lxml_html_clean==0.1.1',
    'MarkupSafe==2.1.5',
    'newspaper3k==0.2.8',
    'nltk==3.8.1',
    'pillow==10.3.0',
    'python-dateutil==2.9.0.post0',
    'python-Levenshtein==0.25.1',
    'pytz==2024.1',
    'PyYAML==6.0.1',
    'rapidfuzz==3.8.1',
    'regex==2023.12.25',
    'requests==2.31.0',
    'requests-file==2.0.0',
    'sgmllib3k==1.0.0',
    'six==1.16.0',
    'soupsieve==2.5',
    'tinysegmenter==0.3',
    'tldextract==5.1.2',
    'tqdm==4.66.2',
    'tzdata==2024.1',
    'tzlocal==5.2',
    'urllib3==2.2.1',
    'Werkzeug==3.0.2',
    'zope.interface==6.3'
]

# Force install each package
for package in packages:
    subprocess.run(['pip', 'install', '--force', package], check=True)

print("All packages have been force installed successfully.")
