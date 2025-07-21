#!/usr/bin/env python3
"""
Script to fix markdown list formatting by:
1. Removing the leading '- ' from lines that start with '- **'
2. Removing the blank line that follows these items
3. Keeping the indented sub-items as they are
"""

import os
import re
from pathlib import Path

def process_markdown_file(file_path):
    """Process a single markdown file to fix list formatting."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match:
    # - **something**
    # (blank line)
    #    - sub-item
    # The pattern captures the item text and the indented sub-items
    pattern = r'^- (\*\*[^*]+\*\*)\s*\n\s*\n((?:[ \t]+-[^\n]+\n?)+)'
    
    # Replace with the item without '- ' prefix and without the blank line
    replacement = r'\1\n\2'
    
    # Apply the replacement
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Check if any changes were made
    if content != original_content:
        return True, content
    else:
        return False, content

def process_directory(directory_path):
    """Process all .md files in a directory and its subdirectories."""
    
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory_path}")
        return [], []
    
    changed_files = []
    unchanged_files = []
    
    # Find all .md files recursively
    md_files = list(directory.rglob('*.md'))
    
    if not md_files:
        print(f"No .md files found in {directory_path}")
        return [], []
    
    print(f"\nProcessing {len(md_files)} .md files in {directory_path}...")
    
    for md_file in md_files:
        try:
            changed, new_content = process_markdown_file(md_file)
            
            if changed:
                # Save the modified content
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                changed_files.append(str(md_file))
                print(f"  ✓ Modified: {md_file.relative_to(directory)}")
            else:
                unchanged_files.append(str(md_file))
                
        except Exception as e:
            print(f"  ✗ Error processing {md_file}: {e}")
    
    return changed_files, unchanged_files

def show_example_changes(file_path, num_examples=2):
    """Show examples of changes made in a file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    examples_shown = 0
    i = 0
    
    while i < len(lines) and examples_shown < num_examples:
        line = lines[i].rstrip()
        
        # Look for pattern that was changed (now without '- ')
        if line.startswith('**') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Check if next line is an indented sub-item
            if next_line.startswith('- '):
                print(f"\n  Example from line {i+1}:")
                print(f"  {line}")
                
                # Show a few sub-items
                j = i + 1
                sub_items_shown = 0
                while j < len(lines) and sub_items_shown < 3:
                    sub_line = lines[j].rstrip()
                    if sub_line.strip().startswith('- '):
                        print(f"  {sub_line}")
                        sub_items_shown += 1
                    elif sub_line.strip() and not sub_line.strip().startswith('- '):
                        break
                    j += 1
                
                examples_shown += 1
                i = j
                continue
        
        i += 1

def main():
    """Main function to process both directories."""
    
    directories = [
        '/Users/brian.stark/work/Cust_Axonops/documentation/docs/metrics/cassandra/',
        '/Users/brian.stark/work/Cust_Axonops/documentation/docs/metrics/kafka/'
    ]
    
    all_changed_files = []
    all_unchanged_files = []
    
    for directory in directories:
        changed, unchanged = process_directory(directory)
        if changed:
            all_changed_files.extend(changed)
        if unchanged:
            all_unchanged_files.extend(unchanged)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files processed: {len(all_changed_files) + len(all_unchanged_files)}")
    print(f"Files modified: {len(all_changed_files)}")
    print(f"Files unchanged: {len(all_unchanged_files)}")
    
    if all_changed_files:
        print("\nModified files:")
        for file in all_changed_files:
            print(f"  - {file}")
        
        # Show examples from a few changed files
        print("\n" + "="*60)
        print("EXAMPLE CHANGES")
        print("="*60)
        
        for file in all_changed_files[:3]:  # Show examples from up to 3 files
            print(f"\nFrom file: {Path(file).name}")
            show_example_changes(file)

if __name__ == "__main__":
    main()