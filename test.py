from pygooglenews import GoogleNews
from newspaper import Article
# default GoogleNews instance
gn = GoogleNews(lang = 'en', country = 'US')

s = gn.top_news()
url = s['entries'][0].link
a=Article(url, language='en')

a.download()
a.parse()
print(a.text)

"""
Generate 5 questions from the text; answer the question in the text; if
the question is answered in the context, output 5 questions
"""