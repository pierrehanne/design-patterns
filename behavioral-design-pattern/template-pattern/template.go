// Template Method Pattern
// ========================
// Category: Behavioral Design Pattern
//
// Intent:
//   Define the skeleton of an algorithm in a base class, deferring some steps
//   to subclasses. Template Method lets subclasses redefine certain steps of
//   an algorithm without changing the algorithm's structure.
//
// When to use:
//   - You want to implement the invariant parts of an algorithm once and let
//     subclasses provide the behavior that varies
//   - Common behavior among subclasses should be factored and localized in a
//     single class to avoid duplication
//   - You want to control which steps subclasses can extend (hooks vs. required)
//
// Key Participants:
//   - AbstractClass (DataMinerSteps interface): defines the steps to implement
//   - ConcreteClass (CSVMiner, JSONMiner, DatabaseMiner): implements the steps
//   - Template Method (Mine function): the algorithm skeleton that calls the steps
//
// Hollywood Principle:
//   "Don't call us, we'll call you." -- The Mine function calls the steps
//   defined by each implementation; the implementations don't drive the flow.
//
// Note: Go doesn't have inheritance. We use an interface for the varying steps
// and a standalone function for the template method. Hook methods are expressed
// via optional interfaces that implementations may satisfy.

package main

import (
	"fmt"
	"strconv"
	"strings"
)

// Record represents a single parsed data entry.
type Record map[string]string

// --- Abstract Steps (Interface) ---

// DataMinerSteps defines the required steps every miner must implement.
type DataMinerSteps interface {
	ReadData(source string) string
	ParseData(rawData string) []Record
	AnalyzeData(data []Record) map[string]string
	GenerateReport(results map[string]string)
}

// --- Optional Hook Interfaces ---

// BeforeAnalyzer is an optional hook called before analysis.
type BeforeAnalyzer interface {
	BeforeAnalysis(data []Record)
}

// Cleaner is an optional hook called after the pipeline completes.
type Cleaner interface {
	Cleanup()
}

// --- Template Method ---

// Mine is the template method: it defines the algorithm skeleton.
// It accepts any DataMinerSteps and calls the steps in the fixed order.
// If the implementation also satisfies hook interfaces, those are called too.
func Mine(miner DataMinerSteps, source string) {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("  Mining data from: %s\n", source)
	fmt.Println(strings.Repeat("=", 60))

	rawData := miner.ReadData(source)
	parsed := miner.ParseData(rawData)

	// Hook: optional pre-analysis (check if the miner implements it)
	if hook, ok := miner.(BeforeAnalyzer); ok {
		hook.BeforeAnalysis(parsed)
	}

	results := miner.AnalyzeData(parsed)
	miner.GenerateReport(results)

	// Hook: optional cleanup
	if hook, ok := miner.(Cleaner); ok {
		hook.Cleanup()
	}

	fmt.Println("  Pipeline complete.")
}

// --- Concrete Classes ---

// CSVMiner mines data from CSV files.
type CSVMiner struct{}

func (m *CSVMiner) ReadData(source string) string {
	fmt.Printf("  [CSV] Reading file: %s\n", source)
	return "name,age,city\nAlice,30,Paris\nBob,25,London\nCharlie,35,Berlin"
}

func (m *CSVMiner) ParseData(rawData string) []Record {
	fmt.Println("  [CSV] Parsing CSV rows...")
	lines := strings.Split(strings.TrimSpace(rawData), "\n")
	headers := strings.Split(lines[0], ",")

	records := make([]Record, 0, len(lines)-1)
	for _, line := range lines[1:] {
		values := strings.Split(line, ",")
		rec := make(Record)
		for i, h := range headers {
			rec[h] = values[i]
		}
		records = append(records, rec)
	}
	fmt.Printf("  [CSV] Parsed %d records\n", len(records))
	return records
}

func (m *CSVMiner) AnalyzeData(data []Record) map[string]string {
	fmt.Println("  [CSV] Analyzing age distribution...")
	sum, min, max := 0, 999, 0
	for _, r := range data {
		age, _ := strconv.Atoi(r["age"])
		sum += age
		if age < min {
			min = age
		}
		if age > max {
			max = age
		}
	}
	count := len(data)
	avg := float64(sum) / float64(count)

	return map[string]string{
		"count":       strconv.Itoa(count),
		"average_age": fmt.Sprintf("%.1f", avg),
		"min_age":     strconv.Itoa(min),
		"max_age":     strconv.Itoa(max),
	}
}

func (m *CSVMiner) GenerateReport(results map[string]string) {
	fmt.Println("  [CSV] Report:")
	for _, key := range []string{"count", "average_age", "min_age", "max_age"} {
		fmt.Printf("    %s: %s\n", key, results[key])
	}
}

// JSONMiner mines data from JSON sources.
type JSONMiner struct{}

func (m *JSONMiner) ReadData(source string) string {
	fmt.Printf("  [JSON] Fetching JSON from: %s\n", source)
	return "product:Widget,price:9.99|product:Gadget,price:24.99|product:Doohickey,price:4.99"
}

func (m *JSONMiner) ParseData(rawData string) []Record {
	fmt.Println("  [JSON] Parsing JSON array...")
	entries := strings.Split(rawData, "|")
	records := make([]Record, 0, len(entries))
	for _, entry := range entries {
		rec := make(Record)
		for _, field := range strings.Split(entry, ",") {
			parts := strings.SplitN(field, ":", 2)
			rec[parts[0]] = parts[1]
		}
		records = append(records, rec)
	}
	fmt.Printf("  [JSON] Parsed %d records\n", len(records))
	return records
}

func (m *JSONMiner) AnalyzeData(data []Record) map[string]string {
	fmt.Println("  [JSON] Analyzing price data...")
	total := 0.0
	min, max := 1e18, -1e18
	for _, r := range data {
		price, _ := strconv.ParseFloat(r["price"], 64)
		total += price
		if price < min {
			min = price
		}
		if price > max {
			max = price
		}
	}
	return map[string]string{
		"total_products":         strconv.Itoa(len(data)),
		"total_revenue_potential": fmt.Sprintf("%.2f", total),
		"cheapest":               fmt.Sprintf("%.2f", min),
		"most_expensive":         fmt.Sprintf("%.2f", max),
	}
}

func (m *JSONMiner) GenerateReport(results map[string]string) {
	fmt.Println("  [JSON] Report:")
	for _, key := range []string{"total_products", "total_revenue_potential", "cheapest", "most_expensive"} {
		fmt.Printf("    %s: %s\n", key, results[key])
	}
}

// BeforeAnalysis implements the BeforeAnalyzer hook for JSONMiner.
func (m *JSONMiner) BeforeAnalysis(data []Record) {
	fmt.Println("  [JSON] Validating schema: all records have 'product' and 'price'...")
	for _, rec := range data {
		if _, ok := rec["product"]; !ok {
			panic("Missing 'product' field")
		}
		if _, ok := rec["price"]; !ok {
			panic("Missing 'price' field")
		}
	}
	fmt.Println("  [JSON] Schema validation passed.")
}

// DatabaseMiner mines data from a database connection.
type DatabaseMiner struct {
	connectionOpen bool
}

func (m *DatabaseMiner) ReadData(source string) string {
	fmt.Printf("  [DB] Connecting to database: %s\n", source)
	m.connectionOpen = true
	fmt.Println("  [DB] Executing query: SELECT * FROM users")
	return "id:1,name:Alice,role:admin|id:2,name:Bob,role:user|id:3,name:Charlie,role:user"
}

func (m *DatabaseMiner) ParseData(rawData string) []Record {
	fmt.Println("  [DB] Parsing query results...")
	rows := strings.Split(rawData, "|")
	records := make([]Record, 0, len(rows))
	for _, row := range rows {
		rec := make(Record)
		for _, field := range strings.Split(row, ",") {
			parts := strings.SplitN(field, ":", 2)
			rec[parts[0]] = parts[1]
		}
		records = append(records, rec)
	}
	fmt.Printf("  [DB] Parsed %d records\n", len(records))
	return records
}

func (m *DatabaseMiner) AnalyzeData(data []Record) map[string]string {
	fmt.Println("  [DB] Analyzing user roles...")
	roles := make(map[string]int)
	for _, rec := range data {
		roles[rec["role"]]++
	}

	results := map[string]string{
		"total_users": strconv.Itoa(len(data)),
	}
	parts := make([]string, 0)
	for role, count := range roles {
		parts = append(parts, fmt.Sprintf("%s=%d", role, count))
	}
	results["role_distribution"] = strings.Join(parts, ", ")
	return results
}

func (m *DatabaseMiner) GenerateReport(results map[string]string) {
	fmt.Println("  [DB] Report:")
	fmt.Printf("    Total users: %s\n", results["total_users"])
	fmt.Printf("    Roles: %s\n", results["role_distribution"])
}

// Cleanup implements the Cleaner hook for DatabaseMiner.
func (m *DatabaseMiner) Cleanup() {
	if m.connectionOpen {
		fmt.Println("  [DB] Closing database connection...")
		m.connectionOpen = false
	}
}

// --- Main ---

func main() {
	// Each miner follows the same algorithm (Mine), but the steps differ.
	// The Mine function controls the flow -- Hollywood Principle in action.

	type pipeline struct {
		miner  DataMinerSteps
		source string
	}

	pipelines := []pipeline{
		{&CSVMiner{}, "users.csv"},
		{&JSONMiner{}, "https://api.example.com/products"},
		{&DatabaseMiner{}, "postgres://localhost:5432/mydb"},
	}

	for _, p := range pipelines {
		Mine(p.miner, p.source)
	}
}
