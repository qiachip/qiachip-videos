import requests

def main():
    urls = [
        "https://raw.githubusercontent.com/qiachip/qiachip/main/docs/KR0548-1CH/QIACHIP_KR0548-1CH.md",
        "https://raw.githubusercontent.com/qiachip/qiachip/main/KR0548-1CH/QIACHIP_KR0548-1CH.md",
        "https://raw.githubusercontent.com/qiachip/qiachip/main/docs/KR0548-1CH/index.md",
        "https://raw.githubusercontent.com/qiachip/qiachip/main/KR0548-1CH/index.md"
    ]

    print("--- Probing GitHub Raw MD Paths ---")
    found_valid = False

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"Trying: {url} -> Status: {response.status_code}")

            if response.status_code == 200:
                print(f"\n--- SUCCESS! First 50 lines of {url} ---\n")
                lines = response.text.splitlines()
                for line in lines[:50]:
                    print(line)
                found_valid = True
                break
        except Exception as e:
            print(f"Error checking {url}: {e}")

    if not found_valid:
        print("\nGitHub raw 路由失败，需换方案")

if __name__ == "__main__":
    main()
