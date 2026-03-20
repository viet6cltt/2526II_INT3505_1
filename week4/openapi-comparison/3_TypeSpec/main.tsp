import "@typespec/http";
import "@typespec/openapi";

using Http;

@service(#{
  title: "Book Management API",
})
@server("http://localhost", "Dev server")
@server("https://2526-ii-int-3505-1-one.vercel.app", "Deploy server")
namespace BookAPI;

// =====================
// Models (schemas)
// =====================

model BookListItem {
  id: int32;
  title: string;
  author: string;
}

model BookDetail {
  id: int32;
  title: string;
  author: string;
  category: string;
}

model BookCreateRequest {
  title: string;
  author: string;
  category: string;
}

model BookUpdateRequest {
  title: string;
  author: string;
  category: string;
}

model ErrorDetail {
  code: int32;
  message: string;
  details?: string;
}

model ErrorResponse {
  error: ErrorDetail;
}

model PaginationMetadata {
  page: int32;
  limit: int32;
  total: int32;
}

model BookListResponse {
  data: BookListItem[];
  metadata: PaginationMetadata;
}

model BookDetailResponse {
  data: BookDetail;
}

// =====================
// Security
// =====================

alias BearerAuth = {
  type: "http";
  scheme: "bearer";
};

alias CookieAuth = {
  type: "apiKey";
  in: "cookie";
  name: "refresh_token";
};

// =====================
// Routes
// =====================

@route("/books")
interface Books {

  @get
  listBooks(
    @query page?: int32,
    @query limit?: int32,
    @query category?: string
  ): BookListResponse | ErrorResponse;

  @post
  @useAuth(BearerAuth)
  createBook(
    @body body: BookCreateRequest
  ): BookDetailResponse | ErrorResponse;
}


@route("/books/{bookId}")
interface BookDetailAPI {

  @get
  @useAuth(BearerAuth)
  getBook(
    @path bookId: int32,
    @header cacheControl?: string
  ): BookDetailResponse | ErrorResponse;

  @put
  @useAuth(BearerAuth)
  updateBook(
    @path bookId: int32,
    @body body: BookUpdateRequest
  ): BookDetailResponse | ErrorResponse;

  @delete
  @useAuth(BearerAuth)
  deleteBook(
    @path bookId: int32
  ): void | ErrorResponse;
}


@route("/users")
interface Users {

  @get
  getUsers(
    @cookie debug?: 0 | 1,
    @cookie theme?: "light" | "dark"
  ): void;
}


@route("/auth/refresh")
interface Auth {

  @post
  @useAuth(CookieAuth)
  refreshToken(): {
    accessToken: string;
  };
}