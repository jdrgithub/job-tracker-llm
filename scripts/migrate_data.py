#!/usr/bin/env python3
"""
Migration script to move existing job opportunity data to the new structure.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_opportunities():
    """Migrate opportunities from old structure to new structure."""
    
    # Define paths
    old_data_dir = Path("src/job_tracker/opportunities")
    new_data_dir = Path("data/opportunities")
    
    # Create new directory
    new_data_dir.mkdir(parents=True, exist_ok=True)
    
    if not old_data_dir.exists():
        logger.info("No old data directory found. Nothing to migrate.")
        return
    
    # Find all JSON files in old directory
    old_files = list(old_data_dir.glob("*.json"))
    
    if not old_files:
        logger.info("No opportunity files found to migrate.")
        return
    
    logger.info(f"Found {len(old_files)} opportunity files to migrate.")
    
    migrated_count = 0
    error_count = 0
    
    for old_file in old_files:
        try:
            logger.info(f"Migrating {old_file.name}...")
            
            # Read old file
            with open(old_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert old format to new format
            new_data = convert_opportunity_format(data)
            
            # Generate new filename
            company = new_data.get('company', 'unknown')
            role = new_data.get('role', 'unknown')
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
            
            safe_company = company.lower().replace(' ', '-').replace('/', '-')
            safe_role = role.lower().replace(' ', '-').replace('/', '-')
            
            new_filename = f"{safe_company}_{safe_role}_{timestamp}.json"
            new_filepath = new_data_dir / new_filename
            
            # Ensure unique filename
            counter = 1
            original_filepath = new_filepath
            while new_filepath.exists():
                name_part = original_filepath.stem
                new_filepath = new_data_dir / f"{name_part}_{counter}.json"
                counter += 1
            
            # Write new file
            with open(new_filepath, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, default=str)
            
            logger.info(f"✓ Migrated to {new_filepath}")
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"✗ Error migrating {old_file.name}: {e}")
            error_count += 1
    
    logger.info(f"Migration complete: {migrated_count} successful, {error_count} errors")
    
    if migrated_count > 0:
        logger.info(f"Data migrated to: {new_data_dir}")
        
        # Ask if user wants to backup old files
        response = input("\nDo you want to backup the old files? (y/n): ").lower()
        if response in ['y', 'yes']:
            backup_dir = Path("backup_old_data")
            backup_dir.mkdir(exist_ok=True)
            
            for old_file in old_files:
                shutil.copy2(old_file, backup_dir / old_file.name)
            
            logger.info(f"Old files backed up to: {backup_dir}")


def convert_opportunity_format(old_data):
    """Convert old opportunity format to new format."""
    
    # Handle different old formats
    if 'interaction_date' in old_data and 'interaction_type' in old_data:
        # Old format with separate interaction fields
        new_data = {
            "timestamp": old_data.get('timestamp', datetime.now().isoformat()),
            "company": old_data.get('company', ''),
            "role": old_data.get('role', ''),
            "recruiter_name": old_data.get('recruiter_name'),
            "recruiter_contact": old_data.get('recruiter_contact'),
            "job_description": old_data.get('job_description'),
            "resume_text": old_data.get('resume_text'),
            "cover_letter_text": old_data.get('cover_letter_text'),
            "notes": old_data.get('notes'),
            "next_steps": old_data.get('next_steps'),
            "company_link": old_data.get('company_link'),
            "source": old_data.get('source'),
            "active": old_data.get('active', True),
            "interest_level": old_data.get('interest_level', 3),
            "status": old_data.get('status'),
            "interactions": []
        }
        
        # Convert old interaction format to new format
        if old_data.get('interaction_date') and old_data.get('interaction_type'):
            interaction = {
                "date": old_data['interaction_date'],
                "type": old_data['interaction_type'],
                "method": old_data.get('interaction_method'),
                "notes": old_data.get('interaction_notes')
            }
            new_data["interactions"].append(interaction)
    
    else:
        # Already in new format or unknown format
        new_data = old_data.copy()
        
        # Ensure required fields exist
        if 'timestamp' not in new_data:
            new_data['timestamp'] = datetime.now().isoformat()
        
        if 'interactions' not in new_data:
            new_data['interactions'] = []
        
        if 'active' not in new_data:
            new_data['active'] = True
        
        if 'interest_level' not in new_data:
            new_data['interest_level'] = 3
    
    return new_data


def cleanup_old_structure():
    """Clean up old directory structure."""
    
    old_dirs = [
        Path("src/job_tracker"),
        Path("src/job_tracker/opportunities")
    ]
    
    for old_dir in old_dirs:
        if old_dir.exists():
            logger.info(f"Removing old directory: {old_dir}")
            shutil.rmtree(old_dir)


def main():
    """Main migration function."""
    print("Job Tracker Data Migration")
    print("=" * 30)
    
    try:
        # Migrate opportunities
        migrate_opportunities()
        
        # Ask if user wants to clean up old structure
        response = input("\nDo you want to remove the old directory structure? (y/n): ").lower()
        if response in ['y', 'yes']:
            cleanup_old_structure()
            print("✓ Old directory structure removed")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"✗ Migration failed: {e}")


if __name__ == "__main__":
    main()
