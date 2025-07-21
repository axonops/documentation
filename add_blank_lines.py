#!/usr/bin/env python3
"""
Script to add blank lines after lines containing double asterisks (**) in markdown files.
Processes all .md files in specified directories.
"""

import os
import re
from pathlib import Path

def is_in_code_block(lines, current_index):
    """Check if the current line is inside a code block."""
    code_block_count = 0
    for i in range(current_index):
        if lines[i].strip().startswith('```'):
            code_block_count += 1
    return code_block_count % 2 == 1

def is_table_line(line):
    """Check if the line is part of a markdown table."""
    stripped = line.strip()
    # Table separator line
    if re.match(r'^\|[\s\-:|]+\|$', stripped):
        return True
    # Regular table line with pipes
    if stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') >= 3:
        return True
    return False

def process_file(filepath):
    """Process a single markdown file to add blank lines after ** lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        current_line = lines[i]
        new_lines.append(current_line)
        
        # Check if this line contains ** (double asterisks)
        if '**' in current_line:
            # Skip if in code block or is a table line
            if not is_in_code_block(lines, i) and not is_table_line(current_line):
                # Check if the next line exists and is not blank
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    # Add a blank line
                    new_lines.append('\n')
                    modified = True
        
        i += 1
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    """Main function to process all markdown files in specified directories."""
    directories = [
        '/Users/brian.stark/work/Cust_Axonops/documentation/docs/metrics/cassandra/',
        '/Users/brian.stark/work/Cust_Axonops/documentation/docs/metrics/kafka/'
    ]
    
    total_files = 0
    modified_files = 0
    changes_made = []
    
    for directory in directories:
        print(f"\nProcessing directory: {directory}")
        
        # Get all .md files in the directory
        for filepath in Path(directory).glob('*.md'):
            total_files += 1
            print(f"  Checking: {filepath.name}", end='')
            
            # Create a backup of the original content for comparison
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            if process_file(filepath):
                modified_files += 1
                print(" - Modified")
                
                # Read the modified content
                with open(filepath, 'r', encoding='utf-8') as f:
                    modified_content = f.read()
                
                # Count changes
                original_lines = original_content.splitlines()
                modified_lines = modified_content.splitlines()
                changes = len(modified_lines) - len(original_lines)
                
                changes_made.append({
                    'file': filepath.name,
                    'directory': directory,
                    'blank_lines_added': changes
                })
            else:
                print(" - No changes needed")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Files unchanged: {total_files - modified_files}")
    
    if changes_made:
        print(f"\nDetailed changes:")
        for change in changes_made:
            print(f"  - {change['file']}: {change['blank_lines_added']} blank lines added")
    
    print(f"\nScript completed successfully!")

if __name__ == "__main__":
    main()