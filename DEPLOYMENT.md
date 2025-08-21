# 🚀 Deploying DebugTutor to Vercel

This guide will help you deploy your DebugTutor app to Vercel with Google authentication.

## Prerequisites

- GitHub account
- Vercel account (free tier available)
- Supabase project with Google OAuth configured
- OpenRouter API key

## Step 1: Prepare Your Repository

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/debugtutor.git
   git push -u origin main
   ```

## Step 2: Configure Supabase for Production

1. **Update Supabase Authentication Settings**:
   - Go to your Supabase project dashboard
   - Navigate to Authentication > Settings
   - Add your Vercel domain to **Site URL** and **Redirect URLs**:
     ```
     https://your-app-name.vercel.app
     ```

2. **Configure Google OAuth**:
   - In Supabase Auth settings, ensure Google provider is enabled
   - Set the redirect URL to: `https://your-app-name.vercel.app`

## Step 3: Deploy to Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Environment Variables**:
   In Vercel dashboard, go to Settings > Environment Variables and add:

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=deepseek/deepseek-r1-distill-llama-70b:free
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key_here
   REDIRECT_URL=https://your-app-name.vercel.app
   ```

3. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically build and deploy your app

## Step 4: Update Your .env.example

Update your local `.env.example` file to include production URLs:

```env
# OpenRouter API (for AI features)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=deepseek/deepseek-r1-distill-llama-70b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions

# Supabase (for Google authentication)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Deployment URLs
REDIRECT_URL=http://localhost:8501  # For local development
# REDIRECT_URL=https://your-app-name.vercel.app  # For production
```

## Step 5: Test Your Deployment

1. **Visit your app**: `https://your-app-name.vercel.app`
2. **Test Google authentication**
3. **Test code debugging features**
4. **Verify all functionality works**

## Troubleshooting

### Common Issues

**Authentication not working**:
- Check Supabase redirect URLs match your Vercel domain exactly
- Verify environment variables are set correctly in Vercel
- Ensure Google OAuth is properly configured in Supabase

**Build failures**:
- Check Vercel build logs for specific errors
- Verify all dependencies are in `requirements.txt`
- Ensure Python version compatibility (3.9+)

**Tree-sitter issues**:
- The build script should handle tree-sitter installation
- If issues persist, check Vercel function logs

**API timeouts**:
- Vercel free tier has 10-second function timeout
- Consider upgrading to Pro for longer timeouts if needed

### Performance Optimization

1. **Enable caching** for static assets
2. **Optimize images** in your PWA config
3. **Use environment-specific configs** for development vs production

## Monitoring

- **Vercel Analytics**: Enable in project settings for usage insights
- **Error Tracking**: Check Vercel function logs for errors
- **Performance**: Monitor response times and function duration

## Updates and Maintenance

1. **Automatic Deployments**: Push to main branch triggers auto-deploy
2. **Environment Variables**: Update in Vercel dashboard as needed
3. **Dependencies**: Keep `requirements.txt` updated

---

**Your DebugTutor app is now live on Vercel! 🎉**

Share your deployed app with users and start helping them debug code with AI assistance.
