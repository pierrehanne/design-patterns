// Decorator Pattern
// =================
// Category: Structural Design Pattern
//
// Intent:
//   Attach additional responsibilities to an object dynamically by wrapping it.
//   Each decorator adds one behavior and delegates to the wrapped object.
//
// When to use:
//   - When you want to add behavior without modifying the original type
//   - When behaviors need to be combined in arbitrary ways at runtime
//   - Follows Open/Closed Principle
//
// Key Participants:
//   - Component (interface): Base interface
//   - ConcreteComponent: The original object
//   - Decorator: Wraps the interface and adds behavior

package main

import (
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

// ---------------------------------------------------------------------------
// Component interface
// ---------------------------------------------------------------------------

type DataSource interface {
	Write(data string) string
	Read(data string) string
}

// ---------------------------------------------------------------------------
// Concrete Component
// ---------------------------------------------------------------------------

type StringDataSource struct{}

func (s *StringDataSource) Write(data string) string { return data }
func (s *StringDataSource) Read(data string) string  { return data }

// ---------------------------------------------------------------------------
// Encryption Decorator
// ---------------------------------------------------------------------------

type EncryptionDecorator struct {
	wrapped DataSource
	shift   int
}

func NewEncryptionDecorator(wrapped DataSource, shift int) *EncryptionDecorator {
	return &EncryptionDecorator{wrapped: wrapped, shift: shift}
}

func (e *EncryptionDecorator) shiftChar(c rune, forward bool) rune {
	if c >= 32 && c < 127 {
		var shifted int
		if forward {
			shifted = int(((int(c)-32+e.shift)%95)+32)
		} else {
			shifted = int(((int(c)-32-e.shift+95)%95)+32)
		}
		return rune(shifted)
	}
	return c
}

func (e *EncryptionDecorator) Write(data string) string {
	var encrypted strings.Builder
	for _, c := range data {
		encrypted.WriteRune(e.shiftChar(c, true))
	}
	return e.wrapped.Write(encrypted.String())
}

func (e *EncryptionDecorator) Read(data string) string {
	inner := e.wrapped.Read(data)
	var decrypted strings.Builder
	for _, c := range inner {
		decrypted.WriteRune(e.shiftChar(c, false))
	}
	return decrypted.String()
}

// ---------------------------------------------------------------------------
// Compression Decorator (simple RLE)
// ---------------------------------------------------------------------------

type CompressionDecorator struct {
	wrapped DataSource
}

func NewCompressionDecorator(wrapped DataSource) *CompressionDecorator {
	return &CompressionDecorator{wrapped: wrapped}
}

func rleEncode(data string) string {
	if len(data) == 0 {
		return ""
	}
	runes := []rune(data)
	var result strings.Builder
	count := 1

	for i := 1; i <= len(runes); i++ {
		if i < len(runes) && runes[i] == runes[i-1] {
			count++
		} else {
			if count > 1 {
				result.WriteString(strconv.Itoa(count))
			}
			result.WriteRune(runes[i-1])
			count = 1
		}
	}
	return result.String()
}

func rleDecode(data string) string {
	var result strings.Builder
	num := ""

	for _, c := range data {
		if unicode.IsDigit(c) {
			num += string(c)
		} else {
			count := 1
			if num != "" {
				count, _ = strconv.Atoi(num)
				num = ""
			}
			result.WriteString(strings.Repeat(string(c), count))
		}
	}
	return result.String()
}

func (c *CompressionDecorator) Write(data string) string {
	return c.wrapped.Write(rleEncode(data))
}

func (c *CompressionDecorator) Read(data string) string {
	return rleDecode(c.wrapped.Read(data))
}

// ---------------------------------------------------------------------------
// Logging Decorator
// ---------------------------------------------------------------------------

type LoggingDecorator struct {
	wrapped DataSource
}

func NewLoggingDecorator(wrapped DataSource) *LoggingDecorator {
	return &LoggingDecorator{wrapped: wrapped}
}

func (l *LoggingDecorator) Write(data string) string {
	fmt.Printf("  [LOG] Writing %d chars\n", len(data))
	result := l.wrapped.Write(data)
	fmt.Printf("  [LOG] After processing: %d chars\n", len(result))
	return result
}

func (l *LoggingDecorator) Read(data string) string {
	fmt.Printf("  [LOG] Reading %d chars\n", len(data))
	result := l.wrapped.Read(data)
	fmt.Printf("  [LOG] After processing: %d chars\n", len(result))
	return result
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	fmt.Println("=== Plain write/read ===")
	source := &StringDataSource{}
	written := source.Write("Hello, World!")
	fmt.Println("Written:", written)
	fmt.Println("Read:   ", source.Read(written))

	// Stack: Logging → Encryption → Compression → Base
	fmt.Println("\n=== Decorated: Logging + Encryption + Compression ===")
	decorated := NewLoggingDecorator(
		NewEncryptionDecorator(
			NewCompressionDecorator(&StringDataSource{}),
			5,
		),
	)

	data := "aaabbbccc Hello World!!!"
	processed := decorated.Write(data)
	fmt.Println("Original: ", data)
	fmt.Println("Processed:", processed)

	fmt.Println("\nReading back:")
	restored := decorated.Read(processed)
	fmt.Println("Restored: ", restored)
	fmt.Println("Match:    ", data == restored)
}
