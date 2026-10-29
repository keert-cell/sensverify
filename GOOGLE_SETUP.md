# 🌐 Google OAuth 2.0 Setup Guide for SensVerify

Follow these 5 simple steps to enable Google Sign-In:

### Step 1: Open Google Cloud Console
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Sign in with your Google account.
- Create a new project or select an existing project (e.g., `SensVerify-Auth`).

### Step 2: Configure OAuth Consent Screen
- In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
- Choose **External** user type and click **Create**.
- Enter:
  - **App name**: `SensVerify Universal Defense`
  - **User support email**: Your Gmail address
  - **Developer contact information**: Your Gmail address
- Click **Save and Continue** through Scopes and Test Users.

### Step 3: Create OAuth 2.0 Credentials
- Go to **APIs & Services** > **Credentials**.
- Click **+ CREATE CREDENTIALS** at the top and select **OAuth client ID**.
- Under **Application type**, choose **Web application**.
- Set **Name**: `SensVerify Web Client`.

### Step 4: Add Authorized Redirect URIs
- Under **Authorized JavaScript origins**, add:
  - `http://localhost:8501`
  - `http://localhost:8502`
  - `https://sensverify.onrender.com` (for production)
- Under **Authorized redirect URIs**, add:
  - `http://localhost:8501`
  - `http://localhost:8502`
  - `https://sensverify.onrender.com`
- Click **Create**.

### Step 5: Copy Keys to `.env`
- A modal dialog will appear with your **Client ID** and **Client Secret**.
- Copy and paste them into your `.env` file:
  ```env
  GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your_client_secret_here
  ```
- SensVerify will automatically read these credentials on startup!
