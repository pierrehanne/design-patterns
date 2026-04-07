/**
 * Builder Pattern
 * ================
 * Category: Creational Design Pattern
 *
 * Intent:
 *   Separate the construction of a complex object from its representation,
 *   allowing step-by-step construction with a fluent, chainable API.
 *
 * When to use:
 *   - When a constructor would need many parameters
 *   - When some parameters are optional and you want readable construction
 *   - When you want validation at build-time, not scattered across setters
 *
 * Key Participants:
 *   - Builder: Provides fluent methods for step-by-step construction
 *   - Product: The complex object being built (immutable once created)
 *   - Director (optional): Defines preset construction sequences
 */

// ---------------------------------------------------------------------------
// Product — immutable once built (all fields readonly)
// ---------------------------------------------------------------------------
interface HttpRequest {
  readonly method: string;
  readonly url: string;
  readonly headers: Record<string, string>;
  readonly queryParams: Record<string, string>;
  readonly body: string | null;
  readonly timeoutSeconds: number;
  readonly retries: number;
  readonly followRedirects: boolean;
}

function formatRequest(req: HttpRequest): string {
  let line = `${req.method} ${req.url}`;
  const qs = Object.entries(req.queryParams)
    .map(([k, v]) => `${k}=${v}`)
    .join("&");
  if (qs) line += `?${qs}`;

  const lines = [line];
  for (const [k, v] of Object.entries(req.headers)) {
    lines.push(`  ${k}: ${v}`);
  }
  if (req.body) {
    lines.push(`  Body: ${req.body.slice(0, 80)}...`);
  }
  lines.push(
    `  Timeout: ${req.timeoutSeconds}s | Retries: ${req.retries} | Follow redirects: ${req.followRedirects}`
  );
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Builder — fluent API with method chaining
// ---------------------------------------------------------------------------
class HttpRequestBuilder {
  private _method = "GET";
  private _url = "";
  private _headers: Record<string, string> = {};
  private _queryParams: Record<string, string> = {};
  private _body: string | null = null;
  private _timeout = 30;
  private _retries = 0;
  private _followRedirects = true;

  // HTTP method shortcuts
  get(url: string): this {
    this._method = "GET";
    this._url = url;
    return this;
  }

  post(url: string): this {
    this._method = "POST";
    this._url = url;
    return this;
  }

  put(url: string): this {
    this._method = "PUT";
    this._url = url;
    return this;
  }

  delete(url: string): this {
    this._method = "DELETE";
    this._url = url;
    return this;
  }

  // Configuration methods (each returns `this` for chaining)
  header(key: string, value: string): this {
    this._headers[key] = value;
    return this;
  }

  query(key: string, value: string): this {
    this._queryParams[key] = value;
    return this;
  }

  body(content: string): this {
    this._body = content;
    return this;
  }

  timeout(seconds: number): this {
    this._timeout = seconds;
    return this;
  }

  retries(count: number): this {
    this._retries = count;
    return this;
  }

  noFollowRedirects(): this {
    this._followRedirects = false;
    return this;
  }

  // Build: validate and produce the immutable product
  build(): HttpRequest {
    if (!this._url) {
      throw new Error("URL is required");
    }
    if (["POST", "PUT"].includes(this._method) && this._body === null) {
      throw new Error(`${this._method} requests should have a body`);
    }

    return {
      method: this._method,
      url: this._url,
      headers: { ...this._headers },
      queryParams: { ...this._queryParams },
      body: this._body,
      timeoutSeconds: this._timeout,
      retries: this._retries,
      followRedirects: this._followRedirects,
    };
  }
}

// ---------------------------------------------------------------------------
// Director (optional) — preset construction sequences
// ---------------------------------------------------------------------------
class RequestDirector {
  static jsonApiGet(url: string): HttpRequestBuilder {
    return new HttpRequestBuilder()
      .get(url)
      .header("Accept", "application/json")
      .header("Content-Type", "application/json")
      .timeout(10)
      .retries(3);
  }

  static authenticatedPost(
    url: string,
    token: string,
    body: string
  ): HttpRequestBuilder {
    return new HttpRequestBuilder()
      .post(url)
      .header("Authorization", `Bearer ${token}`)
      .header("Content-Type", "application/json")
      .body(body)
      .timeout(30);
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const request = new HttpRequestBuilder()
  .get("https://api.example.com/users")
  .header("Authorization", "Bearer abc123")
  .query("page", "1")
  .query("limit", "50")
  .timeout(15)
  .retries(2)
  .build();

console.log("Manual build:");
console.log(formatRequest(request));

console.log("\nDirector preset (JSON API GET):");
const apiRequest = RequestDirector.jsonApiGet(
  "https://api.example.com/products"
)
  .query("category", "electronics")
  .build();
console.log(formatRequest(apiRequest));

console.log("\nDirector preset (Authenticated POST):");
const postRequest = RequestDirector.authenticatedPost(
  "https://api.example.com/orders",
  "secret-token",
  '{"item": "laptop", "qty": 1}'
).build();
console.log(formatRequest(postRequest));
