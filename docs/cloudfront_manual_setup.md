# CloudFront Setup Guide - Manual Steps

This guide walks you through setting up CloudFront for your S3-hosted static website, especially when working in a restricted AWS environment.

## Why CloudFront + Private S3?

- **Security Compliant**: S3 bucket remains private (no public access)
- **Better Performance**: Global CDN edge locations
- **HTTPS by default**: Free SSL certificate from AWS
- **Works with corporate policies**: No public S3 buckets needed

---

## Step-by-Step Setup

### 1. Ensure S3 Bucket is Private

1. Go to **S3 Console** → Select your bucket (`llm-prompt-repository`)
2. Navigate to **Permissions** tab
3. Under **Block public access**, ensure all 4 options are **ON**:
   - ✅ Block all public access
   - ✅ Block public access to buckets and objects granted through new access control lists (ACLs)
   - ✅ Block public access to buckets and objects granted through any access control lists (ACLs)
   - ✅ Block public access to buckets and objects granted through new public bucket or access point policies
   - ✅ Block public and cross-account access to buckets and objects through any public bucket or access point policies

### 2. Create CloudFront Distribution

1. Go to **CloudFront Console**
2. Click **Create Distribution**

#### Origin Settings:
- **Origin domain**: Select your S3 bucket from dropdown
  - Should be: `llm-prompt-repository.s3.us-east-1.amazonaws.com` (adjust region)
- **Origin path**: Leave blank
- **Name**: Auto-filled (keep default)
- **Origin access**: Select **Origin access control settings (recommended)**
  - Click **Create new OAC**
  - Name: `llm-prompt-repository-oac`
  - Click **Create**

#### Default Cache Behavior:
- **Viewer protocol policy**: Redirect HTTP to HTTPS
- **Allowed HTTP methods**: GET, HEAD
- **Cache policy**: CachingOptimized (recommended)
- **Origin request policy**: None
- **Response headers policy**: None

#### Settings:
- **Default root object**: `index.html`
- **Custom error responses**: Click **Create custom error response**
  - HTTP error code: `403`
  - Customize error response: Yes
  - Response page path: `/index.html`
  - HTTP Response code: `200`
  - (This enables client-side routing for SPAs)

3. Click **Create distribution**
4. **IMPORTANT**: Copy the **S3 bucket policy** shown in the blue banner at the top
   - Click **Copy policy**

### 3. Update S3 Bucket Policy

1. Go back to **S3 Console** → Your bucket → **Permissions** tab
2. Scroll to **Bucket policy**
3. Click **Edit**
4. Paste the policy you copied from CloudFront (should look like this):

```json
{
    "Version": "2012-10-17",
    "Statement": {
        "Sid": "AllowCloudFrontServicePrincipal",
        "Effect": "Allow",
        "Principal": {
            "Service": "cloudfront.amazonaws.com"
        },
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::llm-prompt-repository/*",
        "Condition": {
            "StringEquals": {
                "AWS:SourceArn": "arn:aws:cloudfront::YOUR-ACCOUNT-ID:distribution/YOUR-DISTRIBUTION-ID"
            }
        }
    }
}
```

5. Click **Save changes**

### 4. Wait for Deployment

- Go to **CloudFront Console** → **Distributions**
- Status will show **Deploying** (takes 5-15 minutes)
- Once status is **Enabled**, your site is ready

### 5. Test Your Website

- Find your **Distribution domain name** (e.g., `d1234abcd.cloudfront.net`)
- Open in browser: `https://d1234abcd.cloudfront.net`
- Your website should load!

---

## Optional: Add Backend API to CloudFront

To serve both frontend and backend through the same CloudFront domain:

### 1. Add Lambda Function URL as Origin

1. Go to your CloudFront distribution → **Origins** tab
2. Click **Create origin**
   - **Origin domain**: Your Lambda Function URL (without https://)
     - Example: `abc123.lambda-url.us-east-1.on.aws`
   - **Protocol**: HTTPS only
   - **Origin path**: Leave blank
   - **Name**: `lambda-backend`

### 2. Create Cache Behavior for API

1. Go to **Behaviors** tab
2. Click **Create behavior**
   - **Path pattern**: `/api/*`
   - **Origin**: Select `lambda-backend`
   - **Viewer protocol policy**: HTTPS only
   - **Allowed HTTP methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - **Cache policy**: CachingDisabled
   - **Origin request policy**: AllViewer
   - **Response headers policy**: CORS-with-preflight (or create custom)

3. Click **Create behavior**

### 3. Update Backend CORS

In your `backend/main.py`, update CORS to allow your CloudFront domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://d1234abcd.cloudfront.net",  # Your CloudFront domain
        "http://localhost:5173"  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Update Frontend API URL

Update your frontend to use CloudFront domain for API calls:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://d1234abcd.cloudfront.net/api';
```

---

## Quick Reference Commands

### Check distribution status:
```bash
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName,Status]' --output table
```

### Get distribution details:
```bash
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID
```

### Create invalidation (clear cache):
```bash
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

### Update files in S3:
```bash
aws s3 sync frontend/dist s3://llm-prompt-repository --delete
# Then create invalidation to clear CloudFront cache
```

---

## Troubleshooting

### 403 Access Denied
- Check bucket policy is correctly applied
- Verify OAC is attached to the origin
- Ensure bucket is in the same account

### Website not updating
- CloudFront caches content for 24 hours by default
- Create an invalidation: `aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"`

### CORS errors
- Update backend CORS settings to include CloudFront domain
- Check if OPTIONS requests are allowed in CloudFront behavior

---

## Cost Estimate

- **CloudFront**: $0.085 per GB (first 10 TB/month in US)
- **Free tier**: 1 TB data transfer out per month for first 12 months
- Typically very cheap for small applications (<$5-10/month)

---

## Next Steps

1. ✅ CloudFront setup complete
2. 🔐 (Optional) Set up custom domain with Route 53
3. 📜 (Optional) Add SSL certificate for custom domain
4. 🚀 Update deployment scripts to invalidate CloudFront cache after S3 upload
