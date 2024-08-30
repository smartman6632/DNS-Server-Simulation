import subprocess
import time

def run_client_queries():
    queries = [
        "python3 ./client.py 54321 example.com. A 5",
        "python3 ./client.py 54321 example.com. A 1",
        "python3 ./client.py 54321 bar.example.com. CNAME 5",
        "python3 ./client.py 54321 . NS 5",
        "python3 ./client.py 54321 bar.example.com. A 5",
        "python3 ./client.py 54321 foo.example.com. A 5",
        "python3 ./client.py 54321 example.org. A 5",
        "python3 ./client.py 54321 example.org. CNAME 5",
        "python3 ./client.py 54321 example.org. NS 5",
        "python3 ./client.py 54321 www.metalhead.com. A 5"
    ]

    for query in queries:
        print(f"Running query: {query}")
        subprocess.run(query, shell=True)
        time.sleep(1)  # 等待一秒钟，确保服务器有时间处理每个请求

if __name__ == "__main__":
    run_client_queries()
