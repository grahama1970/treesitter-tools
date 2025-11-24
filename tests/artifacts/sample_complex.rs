use std::collections::HashMap;

pub struct Cache<K, V> {
    data: HashMap<K, V>,
    max_size: usize,
}

impl<K, V> Cache<K, V> 
where
    K: std::hash::Hash + Eq,
{
    pub fn new(max_size: usize) -> Self {
        Cache {
            data: HashMap::new(),
            max_size,
        }
    }

    pub fn get(&self, key: &K) -> Option<&V> {
        self.data.get(key)
    }

    pub fn insert(&mut self, key: K, value: V) {
        if self.data.len() >= self.max_size {
            // Simplified: just clear
            self.data.clear();
        }
        self.data.insert(key, value);
    }
}

pub fn hash_string(s: &str) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let mut hasher = DefaultHasher::new();
    s.hash(&mut hasher);
    hasher.finish()
}
