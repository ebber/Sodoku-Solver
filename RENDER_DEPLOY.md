# 🚀 Deploy to Render - Complete Guide

Get your Sudoku app live on the internet in 10 minutes using Render's web interface!

---

## What You'll Get
- ✅ Live URL like `https://your-sudoku-app.onrender.com`
- ✅ Hosted 24/7 on Render's cloud servers
- ✅ Free tier available (sleeps after 15 min inactivity, wakes in ~30 sec)
- ✅ Automatic HTTPS/SSL
- ✅ Auto-deploys when you push to GitHub

---

## Step 1: Push Your Code to GitHub (5 minutes)

### If you need to push:

1. **Open your terminal** and navigate to the project:
   ```bash
   cd "/Users/erik/Documents/Kellogg/Classes/MBAI MBAi 410 Computation Thinking for Business Leaders/Assignment 8/Sodoku-Solver"
   ```

2. **Check the status** (your code is already committed):
   ```bash
   git status
   ```
   You should see: "Your branch is ahead of 'origin/main' by 1 commit"

3. **Push to GitHub**:
   ```bash
   git push origin main
   ```

   If prompted for credentials, enter:
   - Username: `ebber` (or your GitHub username)
   - Password: Your GitHub **Personal Access Token** (not your regular password)

   **Don't have a token?** Get one here: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select `repo` scope
   - Copy the token and use it as your password

4. **Verify it's pushed**:
   Go to https://github.com/ebber/Sodoku-Solver and you should see all your files!

---

## Step 2: Sign Up for Render (2 minutes)

1. **Go to Render**: https://render.com

2. **Click "Get Started for Free"** (top right)

3. **Sign up with GitHub**:
   - Click "Sign in with GitHub"
   - Authorize Render to access your GitHub
   - Done! You're logged in

---

## Step 3: Deploy Your App (3 minutes)

### 3.1 Create New Web Service

1. **Click the "New +" button** (top right of Render dashboard)

2. **Select "Web Service"**

### 3.2 Connect Your Repository

1. **Connect GitHub** (if not already connected)
   - Click "Connect GitHub"
   - Authorize Render

2. **Find your repository**:
   - Look for `ebber/Sodoku-Solver`
   - Click "Connect" next to it

### 3.3 Configure the Service

Fill in these settings:

| Field | Value |
|-------|-------|
| **Name** | `sudoku-app` (or any name you like) |
| **Region** | Choose closest to you (e.g., Oregon USA) |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app` |
| **Plan** | **Free** |

**Screenshot guide:**
```
Name:             sudoku-app
Region:           Oregon (US West)
Branch:           main
Root Directory:   [blank]
Environment:      Python 3
Build Command:    pip install -r requirements.txt
Start Command:    gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app

Instance Type:    Free
```

### 3.4 Deploy!

1. **Scroll down** and click **"Create Web Service"**

2. **Wait for deployment** (~2-3 minutes):
   - You'll see build logs in real-time
   - "Installing Python dependencies..."
   - "Starting service..."
   - Look for: **"Your service is live"** 🎉

3. **Get your URL**:
   - At the top of the page, you'll see: `https://sudoku-app.onrender.com`
   - Click it to open your app!

---

## Step 4: Test Your Live App! 🎮

1. **Open the URL** Render gave you

2. **Test the game**:
   - Select a difficulty (Easy/Medium/Hard)
   - Play some Sudoku!
   - Try an invalid move (should flash red and revert)
   - Toggle the theme (Light/Dark)
   - Use a hint
   - Try the auto-solve

3. **Share the URL** with friends, classmates, or your professor!

---

## Understanding the Free Tier

### What "Sleep" Means:
- After 15 minutes of NO visitors, Render puts your app to sleep (saves resources)
- First visitor after sleep waits ~30 seconds for it to wake up
- Then it's fast again for everyone
- Perfect for demos, assignments, low-traffic apps

### To Keep It Awake (Optional):
- Upgrade to Starter plan ($7/month) - stays awake 24/7
- Or use a free uptime monitor to ping it every 10 minutes (keeps it awake)

---

## Auto-Deploy from GitHub

Once set up, Render automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Added new feature"
git push origin main

# Render automatically detects the push and redeploys!
# Takes ~2-3 minutes
```

---

## Viewing Logs

If something goes wrong:

1. **Go to Render dashboard**
2. **Click your service** (sudoku-app)
3. **Click "Logs" tab**
4. See real-time logs of your app

---

## Troubleshooting

### App Won't Start

**Check the logs:**
- Look for errors in build or start process
- Common issues:
  - Missing dependencies → Add to `requirements.txt`
  - Port error → Make sure using `$PORT` variable (already configured)
  - Python version → Render uses Python 3.7 by default

**Still stuck?**
- Check `DEPLOYMENT.md` for more help
- Render docs: https://render.com/docs

### Push to GitHub Failed

**SSH key issue:**
```bash
# Switch to HTTPS (easier)
git remote set-url origin https://github.com/ebber/Sodoku-Solver.git
git push origin main
```

**Need access token:**
- Go to: https://github.com/settings/tokens
- Generate new token (classic)
- Select `repo` scope
- Use token as password when pushing

### Can't Find Repository on Render

1. Make sure you connected GitHub account
2. Check repository is public (or grant Render access to private repos)
3. Refresh the repository list

---

## Upgrade Options (Optional)

### Free Tier:
- ✅ 750 hours/month
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Sleeps after 15 min inactivity

### Starter ($7/month):
- ✅ Everything in Free
- ✅ No sleep (always on)
- ✅ Faster startup
- ✅ More resources

For this Sudoku app, **Free tier is perfect** for demos and assignments!

---

## Custom Domain (Optional)

Want `sudoku.yourdomain.com`?

1. Buy a domain (Namecheap, Google Domains, etc.)
2. In Render dashboard → Settings → Custom Domains
3. Add your domain
4. Update DNS records (Render shows you how)
5. Free SSL included!

---

## Your App Architecture

```
Internet Users
      ↓
https://sudoku-app.onrender.com (Render's servers)
      ↓
Gunicorn (4 workers)
      ↓
Flask App (app.py)
      ↓
Python Solver (Assignment8.py)
```

**Everything runs in Render's cloud** - your computer can be off!

---

## Next Steps After Deployment

1. **Share your URL** with everyone!
2. **Monitor usage** in Render dashboard
3. **View deployment logs** to see visitors
4. **Keep developing**: Push to GitHub → Auto-deploys!

---

## Alternative Platforms

If Render doesn't work for you:
- **Railway** - Similar, $5 free credits/month (see `DEPLOYMENT.md`)
- **Fly.io** - Free tier, 3 VMs, more technical
- **Heroku** - $5/month minimum, industry standard

Render is recommended for easiest free deployment!

---

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Repository connected to Render
- [ ] Service configured and deployed
- [ ] Got live URL
- [ ] Tested the game
- [ ] Shared with friends! 🎉

---

## Need Help?

- **This guide**: You're reading it!
- **Full guide**: See `DEPLOYMENT.md`
- **Render docs**: https://render.com/docs
- **Render community**: https://community.render.com

---

## Estimated Time

- ⏱️ Push to GitHub: 5 minutes
- ⏱️ Sign up for Render: 2 minutes
- ⏱️ Deploy: 3 minutes
- ⏱️ **Total: 10 minutes**

Then your Sudoku app is live on the internet! 🚀
