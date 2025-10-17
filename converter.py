import os
import json
import argparse
from pathlib import Path
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class WebPConverter:
    def __init__(self, source_dir, dest_dir, log_file, quality=85, method=6, threads=4):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.log_file = log_file
        self.quality = quality
        self.method = method
        self.threads = threads
        
        # Statistics
        self.stats = {
            "total_converted": 0,
            "total_failed": 0,
            "total_original_kb": 0,
            "total_new_kb": 0,
            "start_time": None,
            "end_time": None,
            "conversions": []
        }
        
        # Validate directories
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        self.dest_dir.mkdir(parents=True, exist_ok=True)

    def convert_to_webp(self, image_path):
        """Converts an image to .webp and returns conversion data."""
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                
                # Determine destination path
                relative_path = image_path.relative_to(self.source_dir)
                dest_path = self.dest_dir / relative_path.parent / f"{relative_path.stem}.webp"
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save WebP
                img.save(str(dest_path), "webp", quality=self.quality, method=self.method)
                
                # Get file sizes
                original_size = image_path.stat().st_size
                new_size = dest_path.stat().st_size
                
                # Delete original file
                image_path.unlink()
                
                compression_ratio = (1 - (new_size / original_size)) * 100
                
                return {
                    "status": "success",
                    "filename": image_path.name,
                    "original_kb": round(original_size / 1024, 2),
                    "new_kb": round(new_size / 1024, 2),
                    "saved_percent": round(compression_ratio, 2),
                    "relative_path": str(relative_path),
                }
        except Exception as e:
            return {
                "status": "failed",
                "filename": image_path.name,
                "relative_path": str(image_path.relative_to(self.source_dir)),
                "error": str(e),
            }

    def log_conversion(self, data):
        """Logs conversion result to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if data["status"] == "success":
            log_entry = (
                f"[{timestamp}] ✅ Converted: {data['relative_path']} | "
                f"Original: {data['original_kb']} KB → New: {data['new_kb']} KB | "
                f"Saved: {data['saved_percent']}%\n"
            )
        else:
            log_entry = (
                f"[{timestamp}] ❌ Failed: {data['relative_path']} | "
                f"Error: {data['error']}\n"
            )
        
        with open(self.log_file, "a", encoding="utf-8") as log:
            log.write(log_entry)

    def get_image_files(self):
        """Get all image files to convert."""
        image_extensions = (".png", ".jpg", ".jpeg")
        files = []
        
        for root, _, filenames in os.walk(self.source_dir):
            for filename in filenames:
                if filename.lower().endswith(image_extensions):
                    files.append(Path(root) / filename)
        
        return files

    def run(self, dry_run=False):
        """Main conversion process."""
        print("🚀 Starting recursive image conversion to .webp...\n")
        
        image_files = self.get_image_files()
        
        if not image_files:
            print("⚠️  No image files found in source directory.")
            return
        
        print(f"📁 Found {len(image_files)} image(s) to convert")
        print(f"⚙️  Quality: {self.quality}, Method: {self.method}, Threads: {self.threads}")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be converted\n")
            for img_path in image_files:
                relative_path = img_path.relative_to(self.source_dir)
                print(f"  • {relative_path}")
            print(f"\n✓ Dry run complete. {len(image_files)} file(s) would be converted.")
            return
        
        print()
        
        self.stats["start_time"] = datetime.now()
        
        # Process files with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self.convert_to_webp, img_path): img_path 
                for img_path in image_files
            }
            
            # Use tqdm for progress bar
            for future in tqdm(as_completed(futures), total=len(futures), desc="Converting"):
                result = future.result()
                self.log_conversion(result)
                self.stats["conversions"].append(result)
                
                if result["status"] == "success":
                    self.stats["total_converted"] += 1
                    self.stats["total_original_kb"] += result["original_kb"]
                    self.stats["total_new_kb"] += result["new_kb"]
                else:
                    self.stats["total_failed"] += 1
        
        self.stats["end_time"] = datetime.now()
        self.print_summary()
        self.save_stats()

    def print_summary(self):
        """Print conversion summary statistics."""
        elapsed = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        total_saved = self.stats["total_original_kb"] - self.stats["total_new_kb"]
        overall_compression = (
            (1 - (self.stats["total_new_kb"] / self.stats["total_original_kb"])) * 100
            if self.stats["total_original_kb"] > 0 else 0
        )
        
        print("\n" + "="*60)
        print("📊 CONVERSION SUMMARY")
        print("="*60)
        print(f"✅ Successfully converted: {self.stats['total_converted']} file(s)")
        print(f"❌ Failed: {self.stats['total_failed']} file(s)")
        print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
        print(f"💾 Original total: {self.stats['total_original_kb']:.2f} KB")
        print(f"💾 New total: {self.stats['total_new_kb']:.2f} KB")
        print(f"🎉 Total saved: {total_saved:.2f} KB ({overall_compression:.2f}%)")
        print("="*60)
        print(f"📝 Log saved to: {self.log_file}")
        print(f"📁 WebP files saved to: {self.dest_dir}/")

    def save_stats(self):
        """Save statistics to JSON file."""
        stats_file = Path(self.dest_dir) / "conversion_stats.json"
        stats_data = {
            "total_converted": self.stats["total_converted"],
            "total_failed": self.stats["total_failed"],
            "total_original_kb": round(self.stats["total_original_kb"], 2),
            "total_new_kb": round(self.stats["total_new_kb"], 2),
            "total_saved_kb": round(self.stats["total_original_kb"] - self.stats["total_new_kb"], 2),
            "compression_percent": round(
                (1 - (self.stats["total_new_kb"] / self.stats["total_original_kb"])) * 100
                if self.stats["total_original_kb"] > 0 else 0,
                2
            ),
            "start_time": self.stats["start_time"].isoformat(),
            "end_time": self.stats["end_time"].isoformat(),
            "duration_seconds": (self.stats["end_time"] - self.stats["start_time"]).total_seconds(),
        }
        
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=2)

def load_config(config_file):
    """Load configuration from JSON file."""
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_file}")
        return {}

def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG/JPG images to optimized WebP format recursively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python converter.py
  python converter.py --source ./my_images --dest ./output
  python converter.py --quality 90 --dry-run
  python converter.py --config config.json
        """
    )
    
    parser.add_argument(
        "--source", "-s",
        default="./images",
        help="Source directory containing images (default: ./images)"
    )
    parser.add_argument(
        "--dest", "-d",
        default="./webp",
        help="Destination directory for WebP files (default: ./webp)"
    )
    parser.add_argument(
        "--log", "-l",
        default="conversion_log.txt",
        help="Log file path (default: conversion_log.txt)"
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=85,
        choices=range(0, 101),
        help="WebP quality (0-100, default: 85)"
    )
    parser.add_argument(
        "--method", "-m",
        type=int,
        default=6,
        choices=range(0, 7),
        help="WebP compression method (0-6, default: 6)"
    )
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=4,
        help="Number of threads for parallel processing (default: 4)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview conversions without modifying files"
    )
    parser.add_argument(
        "--config", "-c",
        help="Load settings from JSON config file"
    )
    
    args = parser.parse_args()
    
    # Load config if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Merge config with CLI args (CLI args take precedence)
    source = args.source if args.source != "./images" else config.get("source", "./images")
    dest = args.dest if args.dest != "./webp" else config.get("dest", "./webp")
    log_file = args.log if args.log != "conversion_log.txt" else config.get("log", "conversion_log.txt")
    quality = args.quality if args.quality != 85 else config.get("quality", 85)
    method = args.method if args.method != 6 else config.get("method", 6)
    threads = args.threads if args.threads != 4 else config.get("threads", 4)
    
    try:
        converter = WebPConverter(source, dest, log_file, quality, method, threads)
        converter.run(dry_run=args.dry_run)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()