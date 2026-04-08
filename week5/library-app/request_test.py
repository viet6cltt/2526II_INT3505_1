import requests
import statistics

BASE_URL = "http://localhost:5000"

def benmark_page_based(pages, page_size, repeat=5):
    results = []
    
    for page in pages:
        times = []
        for _ in range(repeat):
            response = requests.get(f"{BASE_URL}/books", params={"type": "page-based", "page": page, "pageSize": page_size})
            times.append(response.elapsed.total_seconds())
        results.append({
            "page": page,
            "pageSize": page_size,
            "avg_time": statistics.mean(times) * 1000,  # to miliseconds
            "min_time": min(times) * 1000,  
            "max_time": max(times) * 1000  
        })
    
    return results    

def benmark_cursor_based(cursors, page_size, repeat=5):
    results = []
    
    for cursor in cursors:
        times = []
        for _ in range(repeat):
            response = requests.get(f"{BASE_URL}/books", params={"type": "cursor-based", "cursor": cursor, "pageSize": page_size})
            times.append(response.elapsed.total_seconds())
        results.append({
            "cursor": cursor,
            "pageSize": page_size,
            "avg_time": statistics.mean(times) * 1000,  
            "min_time": min(times) * 1000,  
            "max_time": max(times) * 1000  
        })
    
    return results
    
if __name__ == "__main__":
    print("PAGE_BASED BENCHMARK")
    print(benmark_page_based(pages=[1, 100, 1000, 9999], page_size=100))
    
    print("CURSOR_BASED BENCHMARK")
    print(benmark_cursor_based(cursors=[None, 990000, 900000, 100], page_size=100))
        
    
    
    