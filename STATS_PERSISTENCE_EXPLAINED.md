# How Statistics Persistence Works in GET-SKILLS

## Overview

Your GET-SKILLS application uses a **dual-persistence strategy** to ensure data survives application restarts, deployments, and Azure App Service maintenance. The system stores all application statistics in Azure Blob Storage and loads them back when the application starts.

## Data Structures Being Persisted

The application maintains four critical in-memory data structures:

### 1. `skill_counter` (Counter)
```python
skill_counter = Counter()
# Example: {'Python': 15, 'JavaScript': 12, 'React': 8, ...}
```
- **Purpose**: Tracks how many documents contain each skill
- **Structure**: Counter object mapping skill names to occurrence counts

### 2. `skill_documents` (defaultdict)
```python
skill_documents = defaultdict(list)
# Example: {
#   'Python': [
#     {'filename': 'resume1.pdf', 'upload_date': '2025-09-23', 'file_date': '2025-09-20', 'file_type': 'pdf'},
#     {'filename': 'resume2.pdf', 'upload_date': '2025-09-22', 'file_date': '2025-09-21', 'file_type': 'pdf'}
#   ]
# }
```
- **Purpose**: Maps each skill to the documents that contain it
- **Structure**: Dictionary where keys are skills and values are lists of document metadata

### 3. `processed_documents` (dict)
```python
processed_documents = {}
# Example: {
#   'resume1.pdf': {
#     'upload_date': '2025-09-23 14:30:00',
#     'file_date': '2025-09-20',
#     'skills_found': ['Python', 'Flask', 'Azure'],
#     'storage_type': 'blob',
#     'file_type': 'pdf'
#   }
# }
```
- **Purpose**: Tracks all processed documents and their metadata
- **Structure**: Dictionary mapping filenames to document information

### 4. `monthly_skill_data` (nested defaultdict)
```python
monthly_skill_data = defaultdict(lambda: defaultdict(int))
# Example: {
#   'Python': {'2025-09': 5, '2025-08': 3, '2025-07': 2},
#   'JavaScript': {'2025-09': 4, '2025-08': 1}
# }
```
- **Purpose**: Tracks skill occurrences by month for chart generation
- **Structure**: Nested dictionary mapping skills to monthly counts

## Persistence Mechanism

### 1. **Storage Location**
- **Primary Storage**: Azure Blob Storage
- **Container**: `uploads` (configurable via `AZURE_STORAGE_CONTAINER_NAME`)
- **Main Stats File**: `app_stats.json`
- **Backup Files**: `backups/stats_backup_YYYYMMDD_HHMMSS.json`

### 2. **Data Serialization Format**
```json
{
  "skill_counter": {
    "Python": 15,
    "JavaScript": 12,
    "React": 8
  },
  "skill_documents": {
    "Python": [
      {
        "filename": "resume1.pdf",
        "upload_date": "2025-09-23 14:30:00",
        "file_date": "2025-09-20",
        "file_type": "pdf"
      }
    ]
  },
  "processed_documents": {
    "resume1.pdf": {
      "upload_date": "2025-09-23 14:30:00",
      "file_date": "2025-09-20",
      "skills_found": ["Python", "Flask", "Azure"],
      "storage_type": "blob",
      "file_type": "pdf"
    }
  },
  "monthly_skill_data": {
    "Python": {
      "2025-09": 5,
      "2025-08": 3
    }
  },
  "last_updated": "2025-09-23T14:30:00.123456",
  "version": "1.0"
}
```

## Persistence Flow

### **When Application Starts** (Load Phase)
```python
# This happens automatically when app.py is imported
try:
    load_stats_from_blob()
    print("Application stats loaded successfully on startup")
except Exception as e:
    print(f"Failed to load stats on startup: {e}")
    print("Starting with empty stats")
```

**Step-by-step process:**
1. **Check Azure Blob Storage availability**
2. **Look for existing `app_stats.json` file**
3. **Download and parse JSON data**
4. **Restore all global variables**:
   - Convert plain dict back to `Counter` for `skill_counter`
   - Convert plain dict back to `defaultdict(list)` for `skill_documents`
   - Restore `processed_documents` as-is
   - Convert nested dict back to `defaultdict(lambda: defaultdict(int))` for `monthly_skill_data`
5. **Log success with statistics summary**

### **When Processing Files** (Save Phase)
```python
# After successfully processing a PDF/Excel file:
save_stats_to_blob()  # Save main stats
# Plus create timestamped backup
```

**Step-by-step process:**
1. **Serialize all data structures** to JSON-compatible format
2. **Upload to Azure Blob Storage** as `app_stats.json`
3. **Create timestamped backup** in `backups/` folder
4. **Log success with timestamp**

## Backup Strategy

### **Primary Backup**
- **File**: `app_stats.json` (main stats file, overwritten each time)
- **Purpose**: Current application state
- **Updated**: Every time a file is processed

### **Secondary Backup**
- **Files**: `backups/stats_backup_YYYYMMDD_HHMMSS.json`
- **Purpose**: Point-in-time snapshots for recovery
- **Created**: Every time a file is processed
- **Format**: Timestamped files with essential data

**Example backup filename**: `backups/stats_backup_20250923_143022.json`

## Error Handling & Resilience

### **If Azure Blob Storage is Unavailable**
```python
if not blob_service_client:
    print("Warning: Azure Blob Storage not available for stats persistence")
    return False
```
- Application continues to work with in-memory data
- Data will be lost on restart (fallback mode)
- Logs warning messages

### **If Stats File Doesn't Exist**
```python
if not blob_client.exists():
    print("Info: No existing stats found, starting with empty stats")
    return False
```
- Application starts with empty data structures
- Normal behavior for first deployment

### **If Loading Fails**
```python
except Exception as e:
    print(f"Error loading stats from blob storage: {e}")
    import traceback
    traceback.print_exc()
    return False
```
- Detailed error logging with stack trace
- Application starts with empty data (safe fallback)

## Manual Operations

### **Health Check**
```bash
curl https://your-app.azurewebsites.net/api/health
```
**Response includes:**
- Whether stats are loaded
- Total documents and skills
- Azure Blob Storage availability
- Timestamp

### **Manual Reload**
```bash
curl -X POST https://your-app.azurewebsites.net/api/reload-stats
```
**Use cases:**
- After manual data restoration
- If stats corruption is suspected
- For debugging purposes

## Why This Approach Works

### ✅ **Advantages**
1. **Survives App Service restarts**: Data persists beyond application lifecycle
2. **No database overhead**: Simple JSON storage for small datasets
3. **Automatic backups**: Point-in-time recovery capability
4. **Fast loading**: All data loaded into memory at startup
5. **Azure-native**: Uses existing blob storage infrastructure

### ⚠️ **Considerations**
1. **Memory usage**: All data loaded into RAM (fine for moderate datasets)
2. **Consistency**: No ACID transactions (acceptable for this use case)
3. **Concurrent writes**: Single-instance application (no concurrency issues)

## Data Recovery Scenarios

### **Scenario 1: Stats Not Loading**
1. Check `/api/health` endpoint
2. Use `/api/reload-stats` to manually reload
3. Check Azure Blob Storage for `app_stats.json`

### **Scenario 2: Data Corruption**
1. Check backup files in `backups/` folder
2. Copy a good backup to `app_stats.json`
3. Use `/api/reload-stats` to reload

### **Scenario 3: Complete Data Loss**
1. Review backup files: `backups/stats_backup_*.json`
2. Restore manually from most recent backup
3. Re-process critical documents if needed

This persistence system ensures your skill statistics and charts remain available even when Azure App Service restarts, providing a reliable user experience while keeping the implementation simple and maintainable.