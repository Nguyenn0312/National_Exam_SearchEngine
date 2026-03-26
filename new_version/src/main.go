package main

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/bytedance/sonic"
	"github.com/redis/go-redis/v9"
	"github.com/valyala/fasthttp"
	"golang.org/x/sync/singleflight"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

// ================= MODEL =================

type ExamResult struct {
	SBD           int64   `gorm:"column:sbd;primaryKey" json:"sbd"`
	Literature    float64 `gorm:"column:literature" json:"literature"`
	Math          float64 `gorm:"column:math" json:"math"`
	LanguageCode  string  `gorm:"column:language_code" json:"language_code"`
	LanguageScore float64 `gorm:"column:language_score" json:"language_score"`
	Physic        float64 `gorm:"column:physic" json:"physic"`
	Chemistry     float64 `gorm:"column:chemistry" json:"chemistry"`
	Biology       float64 `gorm:"column:biology" json:"biology"`
	History       float64 `gorm:"column:history" json:"history"`
	Geography     float64 `gorm:"column:geography" json:"geography"`
	Civic         float64 `gorm:"column:civic" json:"civic"`
}

type cacheTask struct {
	key  string
	data []byte
}

// ================= GLOBAL =================

var (
	db        *gorm.DB
	rdb       *redis.Client
	ctx       = context.Background()
	cacheChan = make(chan cacheTask, 50000)
	group     singleflight.Group // Fixes the "Thundering Herd"
	resultPool = sync.Pool{
		New: func() interface{} { return new(ExamResult) },
	}
)

// ================= WORKER =================

func redisWorker() {
	for task := range cacheChan {
		// SetNX ensures we only write if the key doesn't exist
		_ = rdb.SetNX(context.Background(), task.key, task.data, 15*time.Minute).Err()
	}
}

// ================= MAIN =================

func main() {
	dsn := fmt.Sprintf(
		"root:%s@tcp(db:3306)/national_examsdb?charset=utf8mb4&parseTime=True&loc=Local",
		os.Getenv("DB_PASSWORD"),
	)

	var err error
	for i := 0; i < 15; i++ {
		db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{
			PrepareStmt: true,
		})
		
		if err == nil {
			sqlDB, _ := db.DB()
			if err = sqlDB.Ping(); err == nil {
				log.Println("Successfully connected to the database.")
				break
			}
		}

		log.Printf("Database not ready, retrying in 2s... (%d/15)", i+1)
		time.Sleep(2 * time.Second)
	}

	if err != nil {
		log.Fatal("DB connection failed:", err)
	}

	sqlDB, _ := db.DB()
	sqlDB.SetMaxIdleConns(500)
	sqlDB.SetMaxOpenConns(2000)

	rdb = redis.NewClient(&redis.Options{
        
        Addr:         "redis:6379", 
        PoolSize:     2000,         
        MinIdleConns: 200,          // Keep more connections "warm"
        PoolTimeout:  60 * time.Second, 
        DisableIndentity: true,     // Stops the "setinfo" log spam
        Protocol: 2,                
    })

    for i := 0; i < 50; i++ {
        go redisWorker()
    }

    log.Println("Server running on :8000 using Redis TCP")
    log.Fatal(fasthttp.ListenAndServe(":8000", requestHandler))
}

// ================= HANDLERS =================

var (
	searchPrefix = []byte("/api/search/")
	subjects     = []string{"math", "literature", "physic", "chemistry", "biology", "history", "geography", "civic"}
)

func requestHandler(ctxx *fasthttp.RequestCtx) {
	path := ctxx.Path()

	if bytes.HasPrefix(path, searchPrefix) {
		if len(path) > len(searchPrefix) {
			sbdStr := string(path[len(searchPrefix):])
			handleIDSearch(ctxx, sbdStr)
			return
		}
		handleFilterSearch(ctxx)
		return
	}

	ctxx.SetStatusCode(404)
	ctxx.SetBodyString("route not found")
}

func handleIDSearch(ctxx *fasthttp.RequestCtx, sbdStr string) {
	cacheKey := "student:" + sbdStr

	// 1. Redis Check
	val, err := rdb.Get(ctx, cacheKey).Bytes()
	if err == nil {
		if string(val) == "nf" {
			ctxx.SetStatusCode(404)
			ctxx.SetBodyString("not found (cached)")
			return
		}
		ctxx.Response.Header.Set("Content-Type", "application/json")
		ctxx.SetBody(val)
		return
	}

	// 2. Singleflight DB Fetch

	data, err, _ := group.Do(sbdStr, func() (interface{}, error) {
		student := resultPool.Get().(*ExamResult)
		defer resultPool.Put(student)

		if err := db.Table("exam_results").Where("sbd = ?", sbdStr).First(student).Error; err != nil {
			select {
			case cacheChan <- cacheTask{key: cacheKey, data: []byte("nf")}:
			default:
			}
			return nil, err
		}

		jsonData, _ := sonic.Marshal(student)
		select {
		case cacheChan <- cacheTask{key: cacheKey, data: jsonData}:
		default:
		}
		return jsonData, nil
	})

	if err != nil {
		ctxx.SetStatusCode(404)
		ctxx.SetBodyString("not found")
		return
	}

	ctxx.Response.Header.Set("Content-Type", "application/json")
	ctxx.SetBody(data.([]byte))
}

func handleFilterSearch(ctxx *fasthttp.RequestCtx) {
	query := db.Table("exam_results")
	hasFilter := false

	for _, sub := range subjects {
		val := ctxx.QueryArgs().Peek(sub)
		if len(val) > 0 {
			query = query.Where(fmt.Sprintf("%s = ?", sub), string(val))
			hasFilter = true
		}
	}

	if !hasFilter {
		ctxx.SetStatusCode(400)
		ctxx.SetBodyString("provide a filter")
		return
	}

	var results []ExamResult
	if err := query.Limit(100).Find(&results).Error; err != nil {
		ctxx.SetStatusCode(500)
		return
	}

	jsonData, _ := sonic.Marshal(results)
	ctxx.Response.Header.Set("Content-Type", "application/json")
	ctxx.SetBody(jsonData)
}