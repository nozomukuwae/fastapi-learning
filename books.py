from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{title}")
async def read_book(title: str):
    return next(
        (book for book in BOOKS if book['title'].casefold() == title.casefold()),
        None
    )


@app.get("/books/")
async def read_category_by_query(category: str):
    return [book for book in BOOKS if book['category'].casefold() == category.casefold()]


@app.get("/books/{author}/")
async def read_author_category_by_query(author: str, category: str):
    return [book for book in BOOKS if
            book['author'].casefold() == author.casefold() and book['category'].casefold() == category.casefold()]


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
