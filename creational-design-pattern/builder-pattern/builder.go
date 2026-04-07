// Builder Pattern
// ================
// Category: Creational Design Pattern
//
// Intent:
//   Separate the construction of a complex object from its representation,
//   allowing step-by-step construction with a fluent, chainable API.
//
// When to use:
//   - When a struct has many fields, some optional
//   - When you want validation at build-time
//   - When you want readable, self-documenting construction code
//
// Key Participants:
//   - Builder: Accumulates configuration via chained method calls
//   - Product: The final struct
//   - Director (optional): Preset construction sequences
//
// Go note:
//   Go doesn't have constructors or default params. The builder pattern and
//   functional options pattern are the two main approaches for complex construction.

package main

import (
	"fmt"
	"strings"
)

// ---------------------------------------------------------------------------
// Product
// ---------------------------------------------------------------------------

// HttpRequest is the complex object we're building. Once built, treat as immutable.
type HttpRequest struct {
	Method          string
	URL             string
	Headers         map[string]string
	QueryParams     map[string]string
	Body            *string // nil means no body
	TimeoutSeconds  int
	Retries         int
	FollowRedirects bool
}

func (r *HttpRequest) String() string {
	var sb strings.Builder

	url := r.URL
	if len(r.QueryParams) > 0 {
		params := make([]string, 0, len(r.QueryParams))
		for k, v := range r.QueryParams {
			params = append(params, k+"="+v)
		}
		url += "?" + strings.Join(params, "&")
	}
	fmt.Fprintf(&sb, "%s %s\n", r.Method, url)

	for k, v := range r.Headers {
		fmt.Fprintf(&sb, "  %s: %s\n", k, v)
	}
	if r.Body != nil {
		preview := *r.Body
		if len(preview) > 80 {
			preview = preview[:80]
		}
		fmt.Fprintf(&sb, "  Body: %s...\n", preview)
	}
	fmt.Fprintf(&sb, "  Timeout: %ds | Retries: %d | Follow redirects: %v",
		r.TimeoutSeconds, r.Retries, r.FollowRedirects)

	return sb.String()
}

// ---------------------------------------------------------------------------
// Builder — fluent API with method chaining
// ---------------------------------------------------------------------------

type HttpRequestBuilder struct {
	method          string
	url             string
	headers         map[string]string
	queryParams     map[string]string
	body            *string
	timeout         int
	retries         int
	followRedirects bool
}

func NewHttpRequestBuilder() *HttpRequestBuilder {
	return &HttpRequestBuilder{
		method:          "GET",
		headers:         make(map[string]string),
		queryParams:     make(map[string]string),
		timeout:         30,
		followRedirects: true,
	}
}

// HTTP method shortcuts — each returns the builder for chaining
func (b *HttpRequestBuilder) Get(url string) *HttpRequestBuilder {
	b.method = "GET"
	b.url = url
	return b
}

func (b *HttpRequestBuilder) Post(url string) *HttpRequestBuilder {
	b.method = "POST"
	b.url = url
	return b
}

func (b *HttpRequestBuilder) Put(url string) *HttpRequestBuilder {
	b.method = "PUT"
	b.url = url
	return b
}

func (b *HttpRequestBuilder) Delete(url string) *HttpRequestBuilder {
	b.method = "DELETE"
	b.url = url
	return b
}

// Configuration methods
func (b *HttpRequestBuilder) Header(key, value string) *HttpRequestBuilder {
	b.headers[key] = value
	return b
}

func (b *HttpRequestBuilder) Query(key, value string) *HttpRequestBuilder {
	b.queryParams[key] = value
	return b
}

func (b *HttpRequestBuilder) Body(content string) *HttpRequestBuilder {
	b.body = &content
	return b
}

func (b *HttpRequestBuilder) Timeout(seconds int) *HttpRequestBuilder {
	b.timeout = seconds
	return b
}

func (b *HttpRequestBuilder) Retries(count int) *HttpRequestBuilder {
	b.retries = count
	return b
}

func (b *HttpRequestBuilder) NoFollowRedirects() *HttpRequestBuilder {
	b.followRedirects = false
	return b
}

// Build validates and produces the final HttpRequest.
func (b *HttpRequestBuilder) Build() (*HttpRequest, error) {
	if b.url == "" {
		return nil, fmt.Errorf("URL is required")
	}
	if (b.method == "POST" || b.method == "PUT") && b.body == nil {
		return nil, fmt.Errorf("%s requests should have a body", b.method)
	}

	// Copy maps so the builder can be reused without shared state
	headers := make(map[string]string, len(b.headers))
	for k, v := range b.headers {
		headers[k] = v
	}
	qp := make(map[string]string, len(b.queryParams))
	for k, v := range b.queryParams {
		qp[k] = v
	}

	return &HttpRequest{
		Method:          b.method,
		URL:             b.url,
		Headers:         headers,
		QueryParams:     qp,
		Body:            b.body,
		TimeoutSeconds:  b.timeout,
		Retries:         b.retries,
		FollowRedirects: b.followRedirects,
	}, nil
}

// ---------------------------------------------------------------------------
// Director (optional) — preset construction sequences
// ---------------------------------------------------------------------------

func JsonApiGet(url string) *HttpRequestBuilder {
	return NewHttpRequestBuilder().
		Get(url).
		Header("Accept", "application/json").
		Header("Content-Type", "application/json").
		Timeout(10).
		Retries(3)
}

func AuthenticatedPost(url, token, body string) *HttpRequestBuilder {
	return NewHttpRequestBuilder().
		Post(url).
		Header("Authorization", "Bearer "+token).
		Header("Content-Type", "application/json").
		Body(body).
		Timeout(30)
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	// Manual step-by-step building with chaining
	request, err := NewHttpRequestBuilder().
		Get("https://api.example.com/users").
		Header("Authorization", "Bearer abc123").
		Query("page", "1").
		Query("limit", "50").
		Timeout(15).
		Retries(2).
		Build()

	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println("Manual build:")
	fmt.Println(request)

	// Director preset
	apiRequest, _ := JsonApiGet("https://api.example.com/products").
		Query("category", "electronics").
		Build()
	fmt.Println("\nDirector preset (JSON API GET):")
	fmt.Println(apiRequest)

	postRequest, _ := AuthenticatedPost(
		"https://api.example.com/orders",
		"secret-token",
		`{"item": "laptop", "qty": 1}`,
	).Build()
	fmt.Println("\nDirector preset (Authenticated POST):")
	fmt.Println(postRequest)
}
