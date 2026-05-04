from typing import Optional

from fastapi import FastAPI, Path
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_year: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_year: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year


class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(ge=1, le=5)
    published_year: int = Field(ge=2000, le=2100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Nozomu Kuwae",
                "description": "A description of a new book",
                "rating": 5,
                "published_year": 2026
            }
        }
    }


BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2012),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2020),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2024),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2026),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2013),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 1999)
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(ge=1)):
    return next(
        book for book in BOOKS if book.id == book_id
    )


@app.get("/books/")
async def read_books_by_rating(rating: int):
    return [book for book in BOOKS if book.rating == rating]


@app.get("/books/by_year/")
async def read_books_by_published_year(year: int):
    return [book for book in BOOKS if book.published_year == year]


@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    print(type(new_book))
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) <= 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book")
async def update_book(book_request: BookRequest):
    for index, book in enumerate(BOOKS):
        if book.id == book_request.id:
            BOOKS[index] = Book(**book_request.model_dump())


@app.delete("/books/{book_id}")
async def delete_book(book_id: int = Path(ge=1)):
    for book in BOOKS:
        if book.id == book_id:
            BOOKS.remove(book)
