# Bluehost Python Deployment Guide

## Step 1: Check Python Support
1. Log into Bluehost cPanel
2. Look for "Python" or "Python Selector" in Software section
3. If available, proceed with setup

## Step 2: Create Python App
1. Go to "Python Selector" in cPanel
2. Create new Python application
3. Choose Python version (3.8+ recommended)
4. Set application root to: `/home/username/public_html/seo-tool/`

## Step 3: Upload Files
1. Use File Manager or FTP to upload files to `/public_html/seo-tool/`
2. Upload these files:
   - app.py
   - wsgi.py
   - requirements.txt
   - templates/ folder
   - All other project files

## Step 4: Install Dependencies
1. In Python Selector, go to "Manage Packages"
2. Install required packages:
   - flask
   - nltk
   - beautifulsoup4
   - requests
   - lxml

## Step 5: Configure Application
1. Set startup file to: `wsgi.py`
2. Set application URL to: `https://jpopham.com/seo-tool/`

## Step 6: Test
Visit: `https://jpopham.com/seo-tool/` 