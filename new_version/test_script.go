package main

import (
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

const (
	URL         = "http://localhost/api/search/24008611"//?chemistry=10
	NB_REQUESTS = 1000
	CONCURRENCY = 500
)

func main() {
	var successCount int64
	var failCount int64
	// Pre-allocate 10,000 buckets
	buckets := make([]int64, 10001)

	tr := &http.Transport{
		MaxIdleConns:        CONCURRENCY,
		MaxIdleConnsPerHost: CONCURRENCY,
		IdleConnTimeout:     90 * time.Second,
		DisableCompression:  true,
		DisableKeepAlives:   false,
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	var wg sync.WaitGroup
	reqPerWorker := NB_REQUESTS / CONCURRENCY

	fmt.Printf("Starting High-Perf Load Test: %d requests\n", NB_REQUESTS)
	startTime := time.Now()

	for i := 0; i < CONCURRENCY; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < reqPerWorker; j++ {
				startReq := time.Now()
				resp, err := client.Get(URL)
				
				// Calculate latency in milliseconds
				lat := time.Since(startReq).Milliseconds()
				if lat > 10000 { lat = 10000 } // Cap at 10s for the bucket index

				if err != nil {
					atomic.AddInt64(&failCount, 1)
					continue
				}
				
				if resp.StatusCode >= 200 && resp.StatusCode < 400 {
					atomic.AddInt64(&successCount, 1)
				} else {
					atomic.AddInt64(&failCount, 1)
				}
				resp.Body.Close()

				// Record latency in a thread-safe way without Mutexes
				atomic.AddInt64(&buckets[lat], 1)
			}
		}()
	}

	// Wait logic
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-stop:
		fmt.Println("\n⚠️ Interrupted by user.")
	case <-done:
		fmt.Println("\n✅ Test Complete.")
	}

	duration := time.Since(startTime)
	totalRequests := successCount + failCount

	// Calculate Percentiles from buckets
	p50, p95, p99 := calculatePercentiles(buckets, totalRequests)

	fmt.Println("\n========================================")
	fmt.Printf("URL:         %s\n", URL)
	fmt.Printf("RPS:         %.2f\n", float64(totalRequests)/duration.Seconds())
	fmt.Printf("Total Time:  %.3fs\n", duration.Seconds())
	fmt.Printf("Success:     %d\n", successCount)
	fmt.Printf("Fail:        %d\n", failCount)
	fmt.Printf("p50:         %d ms\n", p50)
	fmt.Printf("p95:         %d ms\n", p95)
	fmt.Printf("p99:         %d ms\n", p99)
	fmt.Println("========================================")
}

func calculatePercentiles(buckets []int64, total int64) (p50, p95, p99 int64) {
	if total == 0 { return }
	var count int64
	targets := []float64{0.50, 0.95, 0.99}
	results := make([]int64, 3)
	targetIdx := 0

	for ms, val := range buckets {
		count += val
		for targetIdx < len(targets) && float64(count) >= float64(total)*targets[targetIdx] {
			results[targetIdx] = int64(ms)
			targetIdx++
		}
	}
	return results[0], results[1], results[2]
}