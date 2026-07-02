#!/usr/bin/env python3
"""
Rename LinkedIn post images according to their source .md files.
Each .md file gets its own image renamed to match its title.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKEDIN_POSTS_ROOT = ROOT / "research" / "linkedin-posts"


def slugify(text):
    """Convert text to a filename-safe slug."""
    # Remove special characters, keep alphanumeric and hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:50] or "linkedin-post"


def extract_title_from_md(md_path):
    """Extract title from .md file content."""
    try:
        content = md_path.read_text(encoding='utf-8')
        # Look for Title: line
        title_match = re.search(r'^Title:\s*(.+)$', content, re.M)
        if title_match:
            return title_match.group(1).strip()
    except Exception:
        pass
    return None


def rename_images_in_folder(expert_folder):
    """Rename images in an expert folder based on .md files - one image per .md file."""
    md_files = sorted(expert_folder.glob("*.md"))
    if not md_files:
        return
    
    print(f"Processing {expert_folder.name} with {len(md_files)} .md files")
    
    # Find all image files that need renaming (those starting with "image")
    image_files = sorted([
        f for f in expert_folder.iterdir() 
        if f.is_file() and f.name.startswith("image") and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    ])
    
    if not image_files:
        print(f"  No images to rename")
        return
    
    print(f"  Found {len(image_files)} images to rename")
    
    # Match each .md file to an image (in order)
    for i, md_file in enumerate(md_files):
        if i >= len(image_files):
            print(f"  No more images for {md_file.name}")
            break
            
        title = extract_title_from_md(md_file)
        if not title:
            print(f"  Could not extract title from {md_file.name}")
            continue
        
        slug = slugify(title)
        img_file = image_files[i]
        
        # Create new filename with slug
        new_name = f"{slug}{img_file.suffix}"
        new_path = expert_folder / new_name
        
        # Handle naming conflicts
        counter = 1
        while new_path.exists():
            new_name = f"{slug}_{counter}{img_file.suffix}"
            new_path = expert_folder / new_name
            counter += 1
        
        # Rename the file
        img_file.rename(new_path)
        print(f"  Renamed {img_file.name} -> {new_name} (from {md_file.name})")


def main():
    # Find all expert folders
    expert_folders = [folder for folder in LINKEDIN_POSTS_ROOT.iterdir() 
                     if folder.is_dir() and folder.name != "."]
    
    if not expert_folders:
        print(f"No expert folders found in {LINKEDIN_POSTS_ROOT}")
        return
    
    print(f"Found {len(expert_folders)} expert folders")
    
    for expert_folder in expert_folders:
        rename_images_in_folder(expert_folder)
        print()


if __name__ == "__main__":
    main()