#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char* key;
    void* value;
} CacheEntry;

typedef struct {
    CacheEntry* entries;
    int size;
    int capacity;
} Cache;

Cache* cache_create(int capacity) {
    Cache* cache = malloc(sizeof(Cache));
    cache->entries = calloc(capacity, sizeof(CacheEntry));
    cache->size = 0;
    cache->capacity = capacity;
    return cache;
}

void cache_set(Cache* cache, const char* key, void* value) {
    if (cache->size < cache->capacity) {
        cache->entries[cache->size].key = strdup(key);
        cache->entries[cache->size].value = value;
        cache->size++;
    }
}

void* cache_get(Cache* cache, const char* key) {
    for (int i = 0; i < cache->size; i++) {
        if (strcmp(cache->entries[i].key, key) == 0) {
            return cache->entries[i].value;
        }
    }
    return NULL;
}

void cache_destroy(Cache* cache) {
    for (int i = 0; i < cache->size; i++) {
        free(cache->entries[i].key);
    }
    free(cache->entries);
    free(cache);
}

unsigned int hash_string(const char* str) {
    unsigned int hash = 0;
    while (*str) {
        hash = hash * 31 + *str++;
    }
    return hash;
}
