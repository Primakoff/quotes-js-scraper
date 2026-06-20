# Тест: повторяем реальную структуру quotes.toscrape.com/js и проверяем разбор
from scraper import extract_quotes, find_next_url

MOCK = '''<!DOCTYPE html><html><body>
<div class="container"><div class="quotes"></div>
<nav><ul class="pager"><li class="next"><a href="/js/page/2/">Next</a></li></ul></nav>
</div>
<script src="/static/jquery.js"></script>
<script>
var data = [
{
"tags": ["change", "deep-thoughts", "thinking", "world"],
"author": {"name": "Albert Einstein", "goodreads_link": "/author/show/9810.Albert_Einstein", "slug": "Albert-Einstein"},
"text": "\\u201cThe world as we have created it is a process of our thinking.\\u201d"
},
{
"tags": ["abilities", "choices"],
"author": {"name": "J.K. Rowling", "goodreads_link": "/author/show/1077326", "slug": "J-K-Rowling"},
"text": "\\u201cIt is our choices that show what we truly are.\\u201d"
}
];
for (var i in data) {
  var d = data[i];
  var quote = "<div>" + d.text + "</div>";
}
</script>
</body></html>'''

quotes = extract_quotes(MOCK)
print("Извлечено цитат:", len(quotes))
for q in quotes:
    print(f'  [{q.author}] {q.text}  | теги: {q.tags}')
print("Ссылка Next:", find_next_url(MOCK, "https://quotes.toscrape.com/js/"))