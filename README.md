# WebP Image Converter

A high-performance Python utility that recursively converts PNG and JPG images to optimized WebP format with parallel processing, detailed logging, and comprehensive statistics.

## Features

- **Recursive conversion**: Processes images in nested folders, preserving directory structure
- **Format support**: Converts PNG, JPG, and JPEG files
- **Parallel processing**: Concurrent conversion with configurable thread count for faster processing
- **Automatic optimization**: Saves WebP files with adjustable quality and compression method
- **Dry-run mode**: Preview conversions without modifying files
- **CLI arguments**: Customize source/dest directories, quality, and threads via command line
- **Config file support**: Load settings from JSON configuration files
- **Detailed logging**: Records conversion details with timestamps and compression statistics
- **Statistics tracking**: Generates JSON report with compression metrics and conversion time
- **Progress tracking**: Visual progress bar with real-time conversion status
- **Error handling**: Gracefully handles corrupted files and continues processing
- **Original removal**: Automatically deletes source images after successful conversion

## Requirements

- Python 3.7+
- Pillow (PIL) library
- tqdm (progress bar library)

## Installation

1. Clone or download this repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install Pillow tqdm
```

## Setup

### Directory Structure

Create your project directory structure:

```
your-project/
├── converter.py
├── requirements.txt
├── images/
│   ├── photo1.jpg
│   ├── photo2.png
│   └── subfolder/
│       └── photo3.jpg
└── (webp/ folder and logs will be created automatically)
```

### Configuration

The script uses sensible defaults but can be customized via CLI arguments or a JSON config file.

## Usage

### Basic Usage

Run the script with default settings:

```bash
python converter.py
```

This will look for images in `./images` and save WebP files to `./webp`.

### Command Line Arguments

```bash
python converter.py [options]
```

**Options:**

- `--source, -s` - Source directory containing images (default: `./images`)
- `--dest, -d` - Destination directory for WebP files (default: `./webp`)
- `--log, -l` - Log file path (default: `conversion_log.txt`)
- `--quality, -q` - WebP quality 0-100 (default: `85`)
- `--method, -m` - Compression method 0-6, higher is better (default: `6`)
- `--threads, -t` - Number of parallel threads (default: `4`)
- `--dry-run` - Preview conversions without modifying files
- `--config, -c` - Load settings from JSON config file

### Usage Examples

**Convert images in custom directories:**

```bash
python converter.py --source ./my_photos --dest ./output
```

**Preview conversions without modifying files:**

```bash
python converter.py --dry-run
```

**Higher quality (larger files, slower processing):**

```bash
python converter.py --quality 95 --method 6
```

**Lower quality (smaller files, faster processing):**

```bash
python converter.py --quality 75 --method 4
```

**Adjust parallel processing threads:**

```bash
python converter.py --threads 8
```

**Use a configuration file:**

```bash
python converter.py --config config.json
```

**Combine multiple options:**

```bash
python converter.py -s ./photos -d ./webp -q 85 -t 6 -l conversion.log
```

### Configuration File

Create a `config.json` file to save settings:

```json
{
  "source": "./my_images",
  "dest": "./output",
  "quality": 85,
  "method": 6,
  "threads": 4,
  "log": "conversion_log.txt"
}
```

Then run:

```bash
python converter.py --config config.json
```

**Note**: Command-line arguments override config file settings.

## Output

### Console Output

```
🚀 Starting recursive image conversion to .webp...

📁 Found 3 image(s) to convert
⚙️  Quality: 85, Method: 6, Threads: 4

Converting: 100%|████████████| 3/3 [00:05<00:00, 1.67it/s]

============================================================
📊 CONVERSION SUMMARY
============================================================
✅ Successfully converted: 3 file(s)
❌ Failed: 0 file(s)
⏱️  Time elapsed: 5.23 seconds
💾 Original total: 5017.25 KB
💾 New total: 2412.50 KB
🎉 Total saved: 2604.75 KB (51.92%)
============================================================
📝 Log saved to: conversion_log.txt
📁 WebP files saved to: ./webp/
```

### Log File (`conversion_log.txt`)

```
[2025-10-18 14:32:15] ✅ Converted: photo1.jpg | Original: 2048.50 KB → New: 1184.23 KB | Saved: 42.15%
[2025-10-18 14:32:16] ✅ Converted: subfolder/photo3.jpg | Original: 1512.75 KB → New: 918.91 KB | Saved: 39.20%
[2025-10-18 14:32:17] ✅ Converted: photo2.png | Original: 3456.00 KB → New: 1548.50 KB | Saved: 55.30%
```

### Statistics File (`webp/conversion_stats.json`)

```json
{
  "total_converted": 3,
  "total_failed": 0,
  "total_original_kb": 5017.25,
  "total_new_kb": 2412.50,
  "total_saved_kb": 2604.75,
  "compression_percent": 51.92,
  "start_time": "2025-10-18T14:32:15.123456",
  "end_time": "2025-10-18T14:32:20.456789",
  "duration_seconds": 5.23
}
```

## Quality & Method Parameters

### Quality (0-100)

- **75**: Smallest files, noticeable quality loss
- **85**: Recommended, good balance (default)
- **90**: Slightly larger, minimal quality loss
- **95**: Close to original, larger files

### Method (0-6)

- **0-3**: Faster compression, larger files
- **4-5**: Balanced
- **6**: Highest quality compression, slower (default)

## Performance Tips

- **Increase threads** for faster processing on multi-core systems: `--threads 8`
- **Reduce quality** for faster processing and smaller files: `--quality 75`
- **Reduce method** for faster compression: `--method 4`
- **Use dry-run first** to verify settings before bulk conversion: `--dry-run`

## Dry-Run Mode

Preview what will be converted without modifying files:

```bash
python converter.py --dry-run
```

Output:
```
🚀 Starting recursive image conversion to .webp...

📁 Found 3 image(s) to convert
⚙️  Quality: 85, Method: 6, Threads: 4

🔍 DRY RUN MODE - No files will be converted

  • photo1.jpg
  • subfolder/photo3.jpg
  • photo2.png

✓ Dry run complete. 3 file(s) would be converted.
```

## Error Handling

If a file fails to convert, the script will:
1. Log the error with details
2. Continue processing other files
3. Report the failure count in the summary

Example error log:
```
[2025-10-18 14:32:18] ❌ Failed: corrupted.jpg | Error: cannot identify image file
```

## Important Notes

- **Destructive operation**: Original image files are deleted after conversion. Consider backing up your images first.
- **WebP compatibility**: WebP has excellent support in modern browsers (Chrome, Firefox, Edge, Safari 14+)
- **Conversion is one-way**: To revert, restore from backups

## Troubleshooting

**"No such file or directory: ./images"**
- Create the `./images` folder before running the script or specify a different source: `--source ./my_images`

**"ModuleNotFoundError: No module named 'PIL' or 'tqdm'"**
- Install dependencies: `pip install -r requirements.txt`

**"Permission denied"**
- Ensure you have read/write permissions in the source and destination directories

**Slow processing**
- Increase threads: `--threads 8`
- Reduce quality: `--quality 75`
- Reduce method: `--method 4`

**Out of memory with many large files**
- Reduce threads: `--threads 2`
- Process files in batches from different folders

## Example Workflow

```bash
# 1. Create image folder
mkdir images
# Add your PNG/JPG files to the images/ folder

# 2. Preview conversions (optional)
python converter.py --dry-run

# 3. Create config file (optional)
cat > config.json << EOF
{
  "source": "./images",
  "dest": "./webp",
  "quality": 85,
  "threads": 4
}
EOF

# 4. Run the converter
python converter.py --config config.json

# 5. Check results
ls -la webp/                    # View converted files
cat conversion_log.txt          # Review log
cat webp/conversion_stats.json  # View statistics
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.