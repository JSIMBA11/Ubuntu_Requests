import requests
import os
import hashlib
from urllib.parse import urlparse


def sanitize_filename(filename: str) -> str:
    """Ensure filename is safe and not empty."""
    if not filename:
        return "downloaded_image.jpg"
    return filename.replace("/", "_").replace("\\", "_")


def hash_content(content: bytes) -> str:
    """Generate a SHA256 hash of file content to detect duplicates."""
    return hashlib.sha256(content).hexdigest()


def fetch_image(url: str, save_dir: str, seen_hashes: set) -> None:
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            print(f"✗ Skipped (not an image): {url}")
            return

        parsed_url = urlparse(url)
        filename = sanitize_filename(os.path.basename(parsed_url.path))
        if not filename or filename == "downloaded_image.jpg":
            # Try to get extension from content-type
            ext = content_type.split("/")[-1].split(";")[0]
            filename = f"downloaded_image.{ext}"

        # Read content in memory (could be improved for large files)
        content = response.content
        file_hash = hash_content(content)

        if file_hash in seen_hashes:
            print(f"✗ Skipped duplicate: {filename}")
            return
        seen_hashes.add(file_hash)

        # Avoid filename collisions
        filepath = os.path.join(save_dir, filename)
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1

        with open(filepath, "wb") as f:
            f.write(content)

        print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error while fetching {url}: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"✗ Unexpected error with {url}: {type(e).__name__}: {e}")


def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    save_dir = "Fetched_Images"
    os.makedirs(save_dir, exist_ok=True)

    urls = input("Please enter image URL(s), separated by commas: ").split(",")
    urls = [u.strip() for u in urls if u.strip()]

    if not urls:
        print("✗ No valid URLs provided.")
        return

    seen_hashes = set()

    for url in urls:
        fetch_image(url, save_dir, seen_hashes)

    print("\nConnection strengthened. Community enriched.")


if __name__ == "__main__":
    main()
