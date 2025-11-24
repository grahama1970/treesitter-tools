package main

import (
	"fmt"
	"sync"
)

type Cache struct {
	mu    sync.RWMutex
	data  map[string]interface{}
	maxSize int
}

func NewCache(maxSize int) *Cache {
	return &Cache{
		data: make(map[string]interface{}),
		maxSize: maxSize,
	}
}

func (c *Cache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.data[key]
	return val, ok
}

func (c *Cache) Set(key string, value interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.data[key] = value
}

func HashString(s string) uint32 {
	h := uint32(0)
	for _, c := range s {
		h = 31*h + uint32(c)
	}
	return h
}

func main() {
	cache := NewCache(100)
	cache.Set("key", "value")
	fmt.Println(cache.Get("key"))
}
