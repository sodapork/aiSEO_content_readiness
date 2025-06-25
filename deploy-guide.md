# SEO Tool Deployment Guide for Bluehost + Ghost

## Option A: Vercel Deployment (Recommended)

### 1. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository
4. Deploy automatically

### 2. Get Your Vercel URL
- Your app will be available at: `https://your-app-name.vercel.app`

### 3. Set Up Custom Domain in Bluehost
1. Log into Bluehost cPanel
2. Go to "Domains" → "Subdomains"
3. Create subdomain: `seo-tools.jpopham.com`
4. Point it to your Vercel app

### 4. Configure DNS
In Bluehost DNS settings, add CNAME record:
- Name: `seo-tools`
- Value: `your-app-name.vercel.app`

## Option B: Railway Deployment

### 1. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy automatically

### 2. Get Railway URL
- Your app will be at: `https://your-app-name.railway.app`

### 3. Set up custom domain (same as above)

## Option C: Render Deployment

### 1. Deploy to Render
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service"
4. Deploy automatically

### 2. Get Render URL
- Your app will be at: `https://your-app-name.onrender.com`

## Integration with Ghost Site

### Method 1: Link from Ghost
Add a link in your Ghost navigation or create a page that links to your tool.

### Method 2: Embed in Ghost Page
Create a Ghost page and embed the tool using an iframe:

```html
<iframe src="https://seo-tools.jpopham.com" 
        width="100%" 
        height="800px" 
        frameborder="0">
</iframe>
```

### Method 3: API Integration
Use the tool's API endpoints directly from your Ghost site. 